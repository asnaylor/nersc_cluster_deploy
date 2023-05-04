from __future__ import annotations

import json
import os
import pkgutil
import socket
import tempfile
from shlex import split
from subprocess import Popen

from jinja2 import Environment
from jinja2 import PackageLoader

from nersc_cluster_deploy._util import slurm_long_options
from nersc_cluster_deploy.service import serviceManager


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

    # Start RayHead
    rayHeadService = serviceManager(gf_root_url=gf_root_url, srun_flags=srun_flags, job_setup=job_setup, metrics=metrics)

    # If only on 1 compute node no need to create workers
    if int(os.getenv('SLURM_NNODES', 0)) == 1:
        return rayHeadService

    # Creater Ray workers
    with tempfile.NamedTemporaryFile('w+', delete=False) as fp:
        # Generate script to create workers
        fp.write(
            _generate_slurm_script(slurm_options, 'ray', rayHeadService.ray.cluster_address, job_setup=job_setup, srun_flags=srun_flags)
        )

        if os.getenv('SLURM_JOBID'):
            print("Creating Ray workers via srun")
            rayHeadService.workers = Popen(split(f'/bin/bash {fp.name}'))
        else:
            print("Creating Ray workers via sbatch")
            Popen(split(f'sbatch {fp.name}'))  # TODO: Return jobid (--parsable)

    return rayHeadService


def _generate_slurm_script(
    slurm_options: dict | str,
    cluster_type: str,
    ray_head_address: str,
    job_setup: list | str = None,
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
                print(flag)
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
        job_setup: list | str = None,
        srun_flags: str = '',
    ):
        """
        Slurm script template generate for jinja2.

        Args:
            slurm_options: dict
                slurm configuration dictionary.
            ray_head_address: str
                ip address + port of ray head.
            job_setup: list or str, optional
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

    def _process_commands(self, commands):
        if isinstance(commands, list):
            return '\n'.join(commands)
        return commands

    def getJob_setup(self):
        return self._process_commands(self.job_setup)
