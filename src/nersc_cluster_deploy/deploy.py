from __future__ import annotations

import json
import pkgutil

from jinja2 import Environment
from jinja2 import PackageLoader
from SuperfacilityAPI import SuperfacilityAccessToken  # noqa: F401
from SuperfacilityAPI import SuperfacilityAPI  # noqa: F401
from SuperfacilityAPI.nersc_systems import NERSC_DEFAULT_COMPUTE

from .utility import slurm_long_options
from .utility import supported_cluster_types
from .utility import supported_nersc_machines


def deploy_ray_cluster(
    sfp_api: SuperfacilityAPI,
    slurm_options: dict | str,
    site: str = NERSC_DEFAULT_COMPUTE,
    use_gpu: bool = True,
    job_setup: list | str = None,
    post_job: list | str = None,
    srun_flags: str = '',
) -> dict:
    """
    Create and submit a Ray Cluster slurm job.

    Args:
        sfp_api: SuperfacilityAPI,
            SuperfacilityAPI object.
        slurm_options: dict or str,
            Slurm configuration dictionary or string.
        site: str, optional
            Name of the NERSC site, by default NERSC_DEFAULT_COMPUTE.
        use_gpu: bool, optional
            Use gpus in cluster, by default True.
        job_setup: list or str, optional
            bash commands to setup the job, by default None.
        post_job: list or str, optional
            bash commands after the job, by default None.
        srun_flags: str, optional
                additional srun flags

    Returns:
        output_json: dict,
            Return json from sf_api request.
    """
    return _deploy_cluster(sfp_api, 'ray', slurm_options, site, use_gpu, job_setup, post_job, srun_flags)


def _deploy_cluster(
    sfp_api: SuperfacilityAPI,
    cluster_type: str,
    slurm_options: dict | str,
    site: str,
    use_gpu: bool,
    job_setup: list | str,
    post_job: list | str,
    srun_flags: str = '',
) -> dict:
    """
    Create and submit cluster slurm job.

    Args:
        sfp_api: SuperfacilityAPI,
            SuperfacilityAPI object.
        cluster_type: str,
            Type of cluster to deploy.
        slurm_options: dict or str,
            Slurm configuration dictionary or string.
        site: str,
            Name of the NERSC site.
        use_gpu: bool,
            Use gpus in cluster.
        job_setup: list or str
            bash commands to setup the job.
        post_job: list or str
            bash commands after the job.
        srun_flags: str, optional
                additional srun flags

    Returns:
        output_json: dict,
            Return json from sf_api request.
    """
    # Input handeling
    if cluster_type not in supported_cluster_types:
        raise TypeError(f'{cluster_type} not supported. Currently only {supported_cluster_types}')

    if site not in supported_nersc_machines:
        raise TypeError(f'{site} not supported. Currently only {supported_nersc_machines}')
    
    # Process slurm options
    slurm_config = _convert_slurm_options(slurm_options, cluster_type, site, use_gpu)

    # Generate slurm script
    slurm_script = _generate_slurm_script(slurm_config, cluster_type, job_setup, post_job, srun_flags)

    # Submit Job
    return sfp_api.post_job(site, slurm_script, isPath=False)


def _convert_slurm_options(slurm_options: dict | str, cluster_type: str, site: str, use_gpu: bool) -> dict:
    """
    Organise and load the slurm options.

    Args:
        slurm_options: dict or str,
            Slurm configuration dictionary or string.
        cluster_type: str,
            Type of cluster to deploy.
        site: str,
            Name of the NERSC site.
        use_gpu: bool,
            Use gpus in cluster.

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
    use_gpu_flag = '_gpu' if use_gpu else ''
    default_slurm_options = json.loads(pkgutil.get_data(__name__, f'configs/{cluster_type}_{site}{use_gpu_flag}.json'))['slurm_options']

    # Combine the user and default slurm options
    return {**default_slurm_options, **slurm_options}


def _generate_slurm_script(slurm_options: dict, cluster_type: str, job_setup: list | str = None, post_job: list | str = None, srun_flags: str = '') -> str:
    """
    Generate and write temporary slurm script.

    Args:
        slurm_options: dict,
            slurm configuration dictionary.
        cluster_type: str,
            type of cluster to deploy.
        job_setup: list or str, optional
            bash commands to setup the job, by default None.
        post_job: list or str, optional
            bash commands after the job, by default None.
        srun_flags: str, optional
                additional srun flags

    Returns:
        slurm_script: str,
            Slurm script.
    """
    # Load in jinja cluster template
    env = Environment(loader=PackageLoader('nersc_cluster_deploy'))
    template = env.get_template(f'{cluster_type}.j2')

    # Give template user variables
    slurm_script_template = slurm_script_template_class(slurm_options, job_setup, post_job, srun_flags)

    # Render slurm script
    return template.render(job=slurm_script_template)


class slurm_script_template_class:
    def __init__(self, sbatch_options, job_setup: list | str = None, post_job: list | str = None, srun_flags: str = ''):
        """
        Slurm script template generate for jinja2.

        Args:
            slurm_options: dict
                slurm configuration dictionary.
            job_setup: list or str, optional
                bash commands to setup the job, by default None.
            post_job: list or str, optional
                bash commands after the job, by default None.
            srun_flags: str, optional
                additional srun flags

        """
        self.sbatch_options = sbatch_options
        self.shifter_flag = 'shifter' if 'image' in sbatch_options else ''
        self.srun_flags = srun_flags
        self.job_setup = job_setup
        self.post_job = post_job

    def getSbatch(self):
        return '\n'.join([f'#SBATCH --{k}={v}' if v else f'#SBATCH --{k}' for k, v in self.sbatch_options.items()])

    def _process_commands(self, commands):
        if isinstance(commands, list):
            return '\n'.join(commands)
        return commands

    def getJob_setup(self):
        return self._process_commands(self.job_setup)

    def getPost_job(self):
        return self._process_commands(self.post_job)
