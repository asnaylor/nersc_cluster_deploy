from __future__ import annotations

import re
import socket

import ray
from SuperfacilityAPI import SuperfacilityAPI  # noqa: F401
from SuperfacilityAPI.nersc_systems import NERSC_DEFAULT_COMPUTE

from .utility import convert_size
from .utility import supported_nersc_machines

def get_ray_cluster_address(sfp_api: SuperfacilityAPI, jobid: int, site: str = NERSC_DEFAULT_COMPUTE) -> str:
    """
    Get the ray cluster address of the slurm job.

    Args:
        sfp_api: SuperfacilityAPI,
            SuperfacilityAPI object.
        jobid: int,
            Slum jobid.
        site: str, optional
            Name of the NERSC site, by default NERSC_DEFAULT_COMPUTE.

    Returns:
        ray_address: str,
            Return json from sf_api request.
    """
    #Input handling    
    if site not in supported_nersc_machines:
        raise TypeError(f'{site} not supported. Currently only {supported_nersc_machines}')
    
    # Get job information
    job_sqs = sfp_api.get_jobs(site=site, sacct=False, jobid=jobid)
    if job_sqs['output'][0]['state'] != 'RUNNING':
        raise RuntimeError(f'Slurm job {jobid} is not currently RUNNING')

    # Parse nodelist and convert to ip
    nodelist = job_sqs['output'][0]['nodelist']
    head_nodename = _parse_nodelist(nodelist)
    head_node_ipaddress = socket.gethostbyname(head_nodename)

    return 'ray://{}:10001'.format(head_node_ipaddress)


def _parse_nodelist(nodelist: str) -> str:
    """
    Parse nodelist to return first node

    Args:
        nodelist: str,
            nodelist output from sqs

    Returns:
        first_node: str,
            Name of first node
    """
    x = re.findall("\d+(?=[-,])", nodelist)

    if len(x) == 0:
        return nodelist
    else:
        return nodelist.split('[')[0] + x[0]



def ray_cluster_summary() -> None:
    """
    Print out a summary of the connected ray cluster
    """
    node_resources = ray.cluster_resources()

    print("Cluster Summary")
    print("---------------")
    print("Nodes: {:0.0f}".format(len([i for i in node_resources if 'node' in i])))
    print("CPU:   {:0.0f}".format(node_resources['CPU']))
    print("GPU:   {:0.0f}".format(node_resources.get('GPU', 0)))
    print("RAM:   {}".format(convert_size(node_resources['memory'])))
    return
