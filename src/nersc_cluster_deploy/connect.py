from __future__ import annotations

import os
import re
import socket
from shlex import split
from subprocess import Popen
from typing import Union

import ray
from SuperfacilityAPI import SuperfacilityAPI  # noqa: F401
from SuperfacilityAPI.nersc_systems import NERSC_DEFAULT_COMPUTE

from .utility import convert_size
from .utility import supported_nersc_machines

grafana_port_default = '3000'
ray_dashboard_port_default = '8265'


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
    # Input handling
    if site not in supported_nersc_machines:
        raise TypeError(f'{site} not supported. Currently only {supported_nersc_machines}')

    # Get headnode name and convert to ip
    head_node_ipaddress = socket.gethostbyname(_get_ray_headnode(sfp_api, jobid, site))

    return 'ray://{}:10001'.format(head_node_ipaddress)


def _get_ray_headnode(sfp_api: SuperfacilityAPI, jobid: int, site: str = NERSC_DEFAULT_COMPUTE) -> str:
    """
    Get Ray cluster headnode

    Args:
        sfp_api: SuperfacilityAPI,
            SuperfacilityAPI object.
        jobid: int,
            Slum jobid.
        site: str, optional
            Name of the NERSC site, by default NERSC_DEFAULT_COMPUTE.

    Returns:
        ray_headnode: str,
            Return Ray headnode name
    """
    # Get job information
    job_sqs = sfp_api.get_jobs(site=site, sacct=False, jobid=jobid)
    if job_sqs['output'][0]['state'] != 'RUNNING':
        raise RuntimeError(f'Slurm job {jobid} is not currently RUNNING')

    # Parse nodelist
    nodelist = job_sqs['output'][0]['nodelist']
    return _parse_nodelist(nodelist)


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
    x = re.findall(r"\d+(?=[-,])", nodelist)

    if len(x) == 0:
        return nodelist
    else:
        return nodelist.split('[')[0] + x[0]


def connect_ray_dashboard(
    sfp_api: SuperfacilityAPI = None,
    jobid: int = 0,
    site: str = NERSC_DEFAULT_COMPUTE,
    machine: str = None,
    metrics: bool = True,
    ray_dashboard_port: str = ray_dashboard_port_default,
    grafana_port: str = grafana_port_default,
) -> Union[str, tuple]:
    """
    Connect to the ray and grafana dashboards

    Args:
        sfp_api: SuperfacilityAPI, optional
            SuperfacilityAPI object.
        jobid: int, optional
            Slum jobid.
        site: str, optional
            Name of the NERSC site, by default NERSC_DEFAULT_COMPUTE.
        machine: str, optional
            remote machine running ray head node.
        metrics: bool, optional
            Connect to grafana, by default True.
        ray_dashboard_port: str, optional
            Ray dashboard port, by default 8265.
        grafana_port: str, optional
            Grafana dashboard port, by default 3000.

    """
    # Check if not within slurm job
    if "SLURM_JOB_ID" not in os.environ:
        # Get head node from slurm
        if not machine:
            machine = _get_ray_headnode(sfp_api, jobid, site)

        if metrics:
            _ssh_port_forward(grafana_port, machine)
        _ssh_port_forward(ray_dashboard_port, machine)

    return get_ray_dashboard_url(metrics=metrics, ray_dashboard_port=ray_dashboard_port, grafana_port=grafana_port)


def _ssh_port_forward(port: str, machine: str) -> Popen:
    """
    SSH port forwarding from remote to local machine
    """
    return Popen(split(f'ssh -N -L localhost:{port}:localhost:{port} {machine} -o LOGLEVEL=ERROR'))


def get_ray_dashboard_url(
    metrics: bool = True, ray_dashboard_port: str = ray_dashboard_port_default, grafana_port: str = grafana_port_default
) -> Union[str, tuple]:
    """
    Get the Ray and Grafana dashboards

    Args:
        metrics: bool, optional
            Get the Grafana URL path, by default True.
        ray_dashboard_port: str, optional
            Ray dashboard port, by default 8265.
        grafana_port: str, optional
            Grafana dashboard port, by default 3000.

    Returns:
        ray_dashboard: str,
            URL path of Ray dashboard.
        grafana_dashboard: str, optional
            URL path of Grafana dashboard.
    """
    user_jupyter = os.getenv('JUPYTERHUB_SERVICE_PREFIX')

    ray_dashboard = f'https://jupyter.nersc.gov{user_jupyter}proxy/localhost:{ray_dashboard_port}/#/new/overview'
    if metrics:
        return (ray_dashboard, f"https://jupyter.nersc.gov{user_jupyter}proxy/{grafana_port}/d/rayDefaultDashboard")
    else:
        return ray_dashboard


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
