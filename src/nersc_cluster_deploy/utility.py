import math

supported_cluster_types = ['ray']  # dask coming soon

supported_nersc_machines = ['perlmutter', 'muller']


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


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
