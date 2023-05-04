from __future__ import annotations

import logging
import os
import socket
import time
from pathlib import Path
from shlex import split
from subprocess import DEVNULL  # noqa: F401
from subprocess import Popen

from nersc_cluster_deploy._util import get_host_ip_address

# Format the log message
logging.basicConfig(format='%(asctime)s %(levelname)s <%(name)s> %(message)s')


# Base service class
class service:
    def __init__(self, name, command):
        self.name = name
        self._command = command
        self.logger = self._create_logger()
        self.logger.setLevel(logging.DEBUG)  # TODO: config logging correctly

    def _create_logger(self):
        return logging.getLogger(self.name)

    def start(self):
        self.logger.info('Starting service')
        self.logger.debug(f'Running cmd: {self._command}')
        self.process = Popen(split(self._command))  # , stdout=DEVNULL, stderr=DEVNULL
        # TODO: returncode and print out stderr if problem

    def kill(self):
        self.logger.info('Stopping service')
        self.process.kill()


# Ray Head Service
class serviceRayHead(service):
    def __init__(self, preamble='module load python', srun='', head_resources='--num-cpus=0 --num-gpus=0', port='6379'):
        self._preamble = preamble
        self._srun = srun
        self._port = port
        self._rayhead = f'ray start --head --block --port {self._port} {head_resources}'
        self.cluster_address = f'{get_host_ip_address()}:{self._port}'
        super(serviceRayHead, self).__init__('RayHead', command=self._generate_command())

    def _generate_command(self):
        commands = []
        commands += [self._preamble.rstrip().rstrip(';')]
        commands += [self._srun + ' ' + self._rayhead] if self._srun else [self._rayhead]
        return '/bin/bash -c "' + ';'.join(commands) + '"'


# Prometheus Service
class servicePrometheus(service):
    def __init__(self, image='prom/prometheus:v2.42.0', prom_dir=''):
        self._srun = True if os.getenv('SLURM_JOBID') else False
        self.image = image
        self._cluster_dir = f'{os.getenv("SCRATCH")}/ray_cluster/'
        self._prom_dir = prom_dir if prom_dir else f'{self._cluster_dir}prometheus'
        self._setup()
        super(servicePrometheus, self).__init__('Prometheus', command=self._generate_command())

    def _setup(self):
        Path(f"{self._prom_dir}").mkdir(parents=True, exist_ok=True)

    def _generate_command(self):
        command = (
            f'shifter --image={self.image} --volume={self._prom_dir}:/prometheus '
            f'/bin/prometheus '
            f'--config.file=/tmp/ray/session_latest/metrics/prometheus/prometheus.yml '
            f'--storage.tsdb.path=/prometheus'
        )
        if self._srun:
            command = f'srun --nodes=1 --ntasks=1 --cpus-per-task=2 --gpus-per-task=0 -w {socket.gethostname()} ' + command
        return command


# Grafana Service
class serviceGrafana(service):
    def __init__(self, image='grafana/grafana-oss:9.4.3', gf_dir='', gf_root_url=''):
        self._srun = True if os.getenv('SLURM_JOBID') else False
        self.image = image
        self._cluster_dir = f'{os.getenv("SCRATCH")}/ray_cluster/'
        self._gf_dir = gf_dir if gf_dir else f'{self._cluster_dir}grafana'
        self.gf_root_url = gf_root_url
        self._setup()
        super(serviceGrafana, self).__init__('Grafana', command=self._generate_command())

    def _setup(self):
        Path(f"{self._gf_dir}").mkdir(parents=True, exist_ok=True)

    def _generate_command(self):
        command = (
            f'shifter --image={self.image} --volume={self._gf_dir}:/grafana '
            f'--env GF_PATHS_DATA=/grafana '
            f'--env GF_PATHS_PLUGINS=/grafana/plugins '
            f'--env GF_SERVER_ROOT_URL={self.gf_root_url}/ '
            f'--env GF_PATHS_CONFIG=/tmp/ray/session_latest/metrics/grafana/grafana.ini '
            f'--env GF_PATHS_PROVISIONING=/tmp/ray/session_latest/metrics/grafana/provisioning '
            f'--entrypoint &'
        )
        if self._srun:
            command = f'srun --nodes=1 --ntasks=1 --cpus-per-task=2 --gpus-per-task=0 -w {socket.gethostname()} ' + command
        return command


# Service Manager
class serviceManager:
    def __init__(self, gf_root_url='', srun_flags='', job_setup='', metrics=True, ray_port='6379'):
        self.logger = self._create_logger()
        self.logger.setLevel(logging.DEBUG)
        self._delay = 10
        self.gf_root_url = gf_root_url
        self._srun_flags = srun_flags
        self._metrics = metrics
        self._job_setup = f'export RAY_GRAFANA_IFRAME_HOST={self.gf_root_url}; ' + job_setup if self._metrics else job_setup
        self._ray_port = ray_port
        self.start()

    def _create_logger(self):
        return logging.getLogger('Service-Manager')

    def start(self):
        self.logger.info('Starting up cluster')

        # Check if code executed is in slurm job
        head_resources = '--num-cpus=0 --num-gpus=0'
        srun_flags = self._srun_flags
        if os.getenv('SLURM_JOBID'):
            ncpus = 124 if self._metrics else 128
            srun_flags = f'srun --nodes=1 --ntasks=1 --cpus-per-task={ncpus} --gpus-per-task=4 -w {socket.gethostname()} ' + srun_flags
            head_resources = f'--num-cpus={ncpus} --num-gpus=4'

        # Start RayHead
        self.ray = serviceRayHead(preamble=self._job_setup, srun=srun_flags, head_resources=head_resources, port=self._ray_port)
        self.ray.start()
        time.sleep(self._delay)

        # Start Metrics Services
        if self._metrics:
            self.prometheus = servicePrometheus()
            self.prometheus.start()

            self.grafana = serviceGrafana(gf_root_url=self.gf_root_url)
            self.grafana.start()

        self.logger.info("Cluster startup complete")

    @property
    def ray_dashboard_url(self):
        return f'https://jupyter.nersc.gov{os.getenv("JUPYTERHUB_SERVICE_PREFIX")}proxy/localhost:8265/'

    @property
    def grafana_dashboard_url(self):
        return f'{self.gf_root_url}/d/rayDefaultDashboard'

    def shutdown(self):
        self.logger.info('Shutdown cluster')
        self.grafana.kill()
        self.prometheus.kill()
        if os.getenv('SLURM_JOBID') and int(os.getenv('SLURM_NNODES', 0)):
            self.workers.kill()  # TODO: better way to manage workers
        self.ray.kill()  # TODO: investigate how to properly kill Ray head
