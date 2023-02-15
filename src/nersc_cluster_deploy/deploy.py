from __future__ import annotations


def deploy_ray_cluster(slurm_options: dict) -> str:
    """
    Creates a Ray Cluster slurm job. Load default slurm options 
    from ray_cluster_config.yaml
    
    Args:
        slurm_options: dictionary containing slurm job options
        
    Returns:
        slurm_jobid
    """


    return _deploy_cluster('ray', slurm_options)


def _deploy_cluster(cluster_type: str,slurm_options: dict) -> str:
    """
    Deploys cluster
    
    Args:
        cluster_type: 'ray' or 'dask'
        slurm_options: dictionary containing slurm job options
        
    Returns:
        slurm_jobid
    """

    return