from __future__ import annotations

import json
import logging
import os
import pkgutil
import socket
import tempfile
from shlex import split
from subprocess import Popen, PIPE

from jinja2 import Environment
from jinja2 import PackageLoader

from nersc_cluster_deploy._util import slurm_long_options
from nersc_cluster_deploy.service import service, serviceManager

logger = logging.getLogger('nersc_cluster_deploy')

def _process_commands(commands):
    if isinstance(commands, list):
        return ';'.join(commands)
    return commands

def deploy_ray_cluster(
    slurm_options: dict | str = '',
    metrics: bool = True,
    gf_root_url: str = '',
    job_setup: list | str = '',
    srun_flags: str = '',
) -> serviceManager:
    """
    Create a Ray cluster at NERSC

    Args:
        slurm_options: dict or str, optional
            Slurm configuration dictionary or string.
        metrics: bool, optional
            Use metrics in cluster, by default True.
        gf_root_url: str, optional
            Root url path of Grafana instance.
        job_setup: list or str, optional
            bash commands to setup the job, by default None.
        srun_flags: str, optional
            additional srun flags

    Returns:
        serviceManager
    """

    # Prepare metrics url
    if gf_root_url.endswith('/'):
        gf_root_url = gf_root_url.rstrip('/')
    if metrics and not gf_root_url:
        gf_root_url = f"https://jupyter.nersc.gov{os.getenv('JUPYTERHUB_SERVICE_PREFIX')}proxy/3000"

    # Prepare job_setup
    job_setup = _process_commands(job_setup)

    # Start RayHead
    rayServiceManager = serviceManager(gf_root_url=gf_root_url, srun_flags=srun_flags, job_setup=job_setup, metrics=metrics)

    # If only on 1 compute node no need to create workers
    if int(os.getenv('SLURM_NNODES', 0)) == 1:
        print(f"Ray cluster running at {rayServiceManager.ray.cluster_address}")
        print(f"Dashboard avaliable at {rayServiceManager.ray_dashboard_url} {'with metrics' if metrics else ''}")
        return rayServiceManager

    # Creater Ray workers
    with tempfile.NamedTemporaryFile('w+', delete=False) as fp:
        # Generate script to create workers
        fp.write(
            _generate_slurm_script(slurm_options, 'ray', rayServiceManager.ray.cluster_address, job_setup=job_setup, srun_flags=srun_flags)
        )
        logger.debug(f'<{__name__}>: Job script {fp.name}')
        fp.seek(0)
        logger.debug(f'<{__name__}>: {fp.read()}')

        if os.getenv('SLURM_JOBID'):
            logger.info(f'<{__name__}>: Creating Ray workers via srun')
            rayServiceManager.workers = service('RayWorkers', command=f'/bin/bash {fp.name}')
            rayServiceManager.workers.start()
        else:
            logger.info(f'<{__name__}>: Creating Ray workers via sbatch')
            sbatch_process = Popen(split(f'sbatch --parsable {fp.name}'), stdout=PIPE, stderr=PIPE)
            p_stdout, p_stderr = tuple(map(lambda x: x.decode("utf-8"),  sbatch_process.communicate()))
            
            if p_stderr:
                logger.critical(f'<{__name__}>: Unable to run sbatch {p_stderr}')
                raise RuntimeError("Unable to submit sbatch")

            rayServiceManager.jobid = p_stdout.strip('\n')
            logger.info(f'<{__name__}>: jobid {p_stdout}')

    # Print useful information to screen
    print(f"Ray cluster running at {rayServiceManager.ray.cluster_address} {f'(jobid {rayServiceManager.jobid})' if rayServiceManager.jobid else ''}")
    print(f"Dashboard avaliable at {rayServiceManager.ray_dashboard_url} {'with metrics' if metrics else ''}")

    return rayServiceManager


def _generate_slurm_script(
    slurm_options: dict | str,
    cluster_type: str,
    ray_head_address: str,
    job_setup: str = '',
    srun_flags: str = '',
) -> str:
    """
    Generate and write temporary slurm script.

    Args:
        slurm_options: dict,
            slurm configuration dictionary.
        cluster_type: str,
            type of cluster to deploy.
        ray_head_address: str
            ip address + port of ray head.
        job_setup: list or str, optional
            bash commands to setup the job, by default None.
        srun_flags: str, optional
            additional srun flags.


    Returns:
        slurm_script: str,
            Slurm script.
    """
    # Check if in job
    slurm_options = None if os.getenv('SLURM_JOBID') else _convert_slurm_options(slurm_options, 'ray')

    # Load in jinja cluster template
    env = Environment(loader=PackageLoader('nersc_cluster_deploy'))
    template = env.get_template(f'{cluster_type}.j2')

    # Give template user variables
    slurm_script_template = slurm_script_template_class(slurm_options, ray_head_address, job_setup, srun_flags)

    # Render slurm script
    return template.render(job=slurm_script_template)


def _convert_slurm_options(slurm_options: dict | str, cluster_type: str) -> dict:
    """
    Organise and load the slurm options.

    Args:
        slurm_options: dict or str,
            Slurm configuration dictionary or string.
        cluster_type: str,
            Type of cluster to deploy.

    Returns:
        slurm_config: dict,
            Return slurm config.
    """
    # Convert slurm options string into dict
    if isinstance(slurm_options, str):
        slurm_options_copy = [i for i in slurm_options.split(' ') if i]
        slurm_options = dict()

        while len(slurm_options_copy):
            flag = slurm_options_copy.pop(0)
            if '--' in flag:
                v, k = flag.strip('--').split('=')
                slurm_options[v] = k
            else:
                option = slurm_options_copy.pop(0)
                slurm_options[flag.strip('-')] = option

    # Convert slurm options from short to long
    slurm_options = {(slurm_long_options[k] if len(k) == 1 else k): v for k, v in slurm_options.items()}

    # Load default slurm options
    default_slurm_options = json.loads(pkgutil.get_data(__name__, f'configs/{cluster_type}.json'))['slurm_options']

    # Combine the user and default slurm options
    return {**default_slurm_options, **slurm_options}


class slurm_script_template_class:
    def __init__(
        self,
        sbatch_options,
        ray_head_address,
        job_setup: str = '',
        srun_flags: str = '',
    ):
        """
        Slurm script template generate for jinja2.

        Args:
            slurm_options: dict
                slurm configuration dictionary.
            ray_head_address: str
                ip address + port of ray head.
            job_setup: str, optional
                bash commands to setup the job, by default None.
            srun_flags: str, optional
                additional srun flags

        """
        self.sbatch_options = sbatch_options
        self.ray_head_address = ray_head_address
        self.srun_flags = srun_flags
        self.job_setup = job_setup
        self.ray_headnode = socket.gethostname()

    def getSbatch(self):
        return '\n'.join([f'#SBATCH --{k}={v}' if v else f'#SBATCH --{k}' for k, v in self.sbatch_options.items()])

    def getJob_setup(self):
        return self.job_setup
