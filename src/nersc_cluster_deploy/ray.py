from __future__ import annotations

import ray

from nersc_cluster_deploy._util import convert_size


def cluster_summary() -> None:
    """
    Print out a summary of the ray cluster
    """
    node_resources = ray.cluster_resources()

    print("Nodes: {:0.0f}".format(len([i for i in node_resources if 'node' in i])))
    print("CPU:   {:0.0f}".format(node_resources.get('CPU', 0)))
    print("GPU:   {:0.0f}".format(node_resources.get('GPU', 0)))
    print("RAM:   {}".format(convert_size(node_resources.get('memory', 0))))
    return
