from __future__ import annotations

import math
import socket

slurm_long_options = {
    'A': 'account',
    'a': 'array',
    'b': 'begin',
    'D': 'chdir',
    'M': 'clusters',
    'C': 'constraint',
    'S': 'core-spec',
    'c': 'cpus-per-task',
    'd': 'dependency',
    'm': 'distribution',
    'e': 'error',
    'x': 'exclude',
    'B': 'extra-node-info',
    'G': 'gpus',
    'i': 'input',
    'J': 'job-name',
    'L': 'licenses',
    'k': 'no-kill',
    'F': 'nodefile',
    'w': 'nodelist',
    'N': 'nodes',
    'n': 'ntasks',
    'o': 'output',
    'O': 'overcommit',
    's': 'oversubscribe',
    'p': 'partition',
    'q': 'qos',
    't': 'time',
}

grafana_port_default = '3000'
ray_dashboard_port_default = '8265'


def convert_size(size_bytes: int | float) -> str:
    """Convert bytes to human readable."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def get_host_ip_address() -> str:
    """Get the ip address of current machine"""
    return socket.gethostbyname(socket.gethostname())
