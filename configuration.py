import os
import json
from typing import List
import logging

class WorkerSetConfiguration:
    def __init__(self, json_data: json) -> None:
        self._id = json_data['id']
        self._name = json_data['name']
        self._worker_ids = json_data['worker-ids']
        self._distribution = json_data['distribution']
        self._hash_method = json_data['hash-method']
        self._accepted_scp_ids = json_data['accepted-scp-ids']

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def worker_ids(self):
        return self._worker_ids

    @property
    def distribution(self):
        return self._distribution

    @property
    def hash_method(self):
        return self._hash_method

    @property
    def accepted_scp_ids(self):
        return self._accepted_scp_ids

class CoreConfiguration:
    def __init__(self, json_data: json) -> None:
        print(json_data)
        self._log_dir_path = json_data['log-dir-path']
        self._log_format = json_data['log-format']
        self._buffer_dir_path = json_data['buffer-dir-path']
        self._router_count = json_data['router-count']

    @property
    def log_dir_path(self):
        return self._log_dir_path

    @property
    def log_format(self):
        return self._log_format

    @property
    def buffer_dir_path(self):
        return self._buffer_dir_path

    @property
    def router_count(self):
        return self._router_count

class SCPConfiguration:
    def __init__(self, json_data: json) -> None:
        self._id = json_data['id']
        self._name = json_data['name']
        self._ae_title = json_data['ae-title']
        self._address = json_data['address']
        self._port = json_data['port']

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def ae_title(self):
        return self._ae_title

    @property
    def address(self):
        return self._address

    @property
    def port(self):
        return self._port

class WorkerConfiguration:
    def __init__(self, json_data: json) -> None:
        self._id = json_data['id']
        self._name = json_data['name']
        self._ae_title = json_data['ae-title']
        self._address = json_data['address']
        self._port = json_data['port']

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def ae_title(self):
        return self._ae_title

    @property
    def address(self):
        return self._address

    @property
    def port(self):
        return self._port

class Configuration:

    def __init__(self, path: str) -> None:

        self._workers: List[WorkerConfiguration] = []
        self._scps: List[SCPConfiguration] = []
        self._core: CoreConfiguration = None
        self._worker_sets: List[WorkerSetConfiguration] = []
        self._logger = logging.getLogger(__name__)

        if not os.path.exists(path):
            raise BaseException(f'{str} does not exist during attempt to load configuration')
        if os.path.isdir(path):
            self._read_config_dir(path)
        else:
            self._read_config_file(path)

    def _read_config_dir(self, path) -> bool:
        if os.path.isdir(path):
            files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            for file in files:
                self._read_config_file(file)
        else:
            raise BaseException(f'{path} is not a directory during attempt to load configuration')

    def _read_config_file(self, path) -> bool:
        self._logger.info(f'Reading config from {path}')
        with open(path) as f:
            data = json.load(f)
            self._parse_config(data)

    def _parse_config(self, config) -> bool:
        if 'core' in config:
            self._core = CoreConfiguration(config['core'])
        if 'worker-sets' in config:
            for worker_set in config['worker-sets']:
                #print('Creating worker set')
                worker_set = WorkerSetConfiguration(worker_set)
                self._worker_sets.append(worker_set)
        if 'scps' in config:
            for scp in config['scps']:
                #print('Creating scp configuration')
                scp = SCPConfiguration(scp)
                self._scps.append(scp)
        if 'workers' in config:
            for worker in config['workers']:
                #print('Creating worker configuration')
                wc = WorkerConfiguration(worker)
                self._workers.append(wc)
                

    def workers(self) -> List[WorkerConfiguration]:
        return self._workers

    def scps(self) -> List[SCPConfiguration]:
        return self._scps

    def core(self) -> CoreConfiguration:
        return self._core

    def worker_sets(self) -> List[WorkerSetConfiguration]:
        return self._worker_sets