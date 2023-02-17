from __future__ import annotations

import ray

from .utility import convert_size


def get_ray_cluster_address():
    """Get the ray head node address from the scratch file."""
    node_address = ''  # TO-DO get ip addres from slurm, may need work around for cori
    return 'ray://{}:10001'.format(node_address)


def cluster_summary():
    node_resources = ray.cluster_resources()

    print("Cluster Summary")
    print("---------------")
    print("Nodes: {:0.0f}".format(len([i for i in node_resources if 'node' in i])))
    print("CPU:   {:0.0f}".format(node_resources['CPU']))
    print("GPU:   {:0.0f}".format(node_resources.get('GPU', 0)))
    print("RAM:   {}".format(convert_size(node_resources['memory'])))
    return
