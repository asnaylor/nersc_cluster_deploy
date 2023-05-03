from __future__ import annotations

import json
import os
import pkgutil

from nersc_cluster_deploy._util import slurm_long_options
from nersc_cluster_deploy.service import serviceManager

# from jinja2 import Environment
# from jinja2 import PackageLoader


def deploy_ray_cluster(
    slurm_options: dict | str = '',
    metrics: bool = True,
    gf_root_url: str = '',
    job_setup: list | str = None,
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

    # TODO: Test submitting with sbatch
    # if slurm_options:
    #     #submit to sbatch

    #     # Process slurm options
    #     slurm_config = _convert_slurm_options(slurm_options, 'ray')

    #     # Generate slurm script
    #     slurm_script = _generate_slurm_script(slurm_config, cluster_type, job_setup, post_job, srun_flags, metrics, gf_root_url)

    # Submit Job
    return rayHeadService


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


# def _generate_slurm_script(
#     slurm_options: dict,
#     cluster_type: str,
#     job_setup: list | str = None,
#     post_job: list | str = None,
#     srun_flags: str = '',
#     metrics: bool = True,
#     gf_root_url: str = '',
# ) -> str:
#     """
#     Generate and write temporary slurm script.

#     Args:
#         slurm_options: dict,
#             slurm configuration dictionary.
#         cluster_type: str,
#             type of cluster to deploy.
#         job_setup: list or str, optional
#             bash commands to setup the job, by default None.
#         post_job: list or str, optional
#             bash commands after the job, by default None.
#         srun_flags: str, optional
#             additional srun flags
#         metrics: bool, optional
#             Use metrics in cluster.
#         gf_root_url: str, optional
#             Root url path of Grafana instance.

#     Returns:
#         slurm_script: str,
#             Slurm script.
#     """
#     # Load in jinja cluster template
#     env = Environment(loader=PackageLoader('nersc_cluster_deploy'))
#     template = env.get_template(f'{cluster_type}.j2')

#     # Give template user variables
#     slurm_script_template = slurm_script_template_class(slurm_options, job_setup, post_job, srun_flags, metrics, gf_root_url)

#     # Render slurm script
#     return template.render(job=slurm_script_template)


# class slurm_script_template_class:
#     def __init__(
#         self,
#         sbatch_options,
#         job_setup: list | str = None,
#         post_job: list | str = None,
#         srun_flags: str = '',
#         metrics: bool = True,
#         gf_root_url: str = '',
#     ):
#         """
#         Slurm script template generate for jinja2.

#         Args:
#             slurm_options: dict
#                 slurm configuration dictionary.
#             job_setup: list or str, optional
#                 bash commands to setup the job, by default None.
#             post_job: list or str, optional
#                 bash commands after the job, by default None.
#             srun_flags: str, optional
#                 additional srun flags
#             metrics: bool, optional
#                 Use metrics in cluster.
#             gf_root_url: str, optional
#                 Root url path of Grafana instance.

#         """
#         self.sbatch_options = sbatch_options
#         self.shifter_flag = 'shifter' if 'image' in sbatch_options else ''
#         self.srun_flags = srun_flags
#         self.job_setup = job_setup
#         self.post_job = post_job
#         self.metrics = metrics
#         self.GF_root_url = gf_root_url

#     def getSbatch(self):
#         return '\n'.join([f'#SBATCH --{k}={v}' if v else f'#SBATCH --{k}' for k, v in self.sbatch_options.items()])

#     def _process_commands(self, commands):
#         if isinstance(commands, list):
#             return '\n'.join(commands)
#         return commands

#     def getJob_setup(self):
#         return self._process_commands(self.job_setup)

#     def getPost_job(self):
#         return self._process_commands(self.post_job)
