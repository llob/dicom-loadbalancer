'''
Configuration management module
'''
import os
import json
from typing import List, Tuple, Dict
import abc
import logging
import jsonschema

class AbstractConfiguration:
    '''
    Abstract super class for all configuration classes
    '''
    def _validate_json(self, json_object):
        try:
            jsonschema.validate(json_object, schema=self.schema())
        except jsonschema.ValidationError as exception:
            raise ConfigurationError(exception.message)

    @abc.abstractmethod
    def schema(self) -> Dict:
        '''Get the JSON schema for this configuration section'''

class HeaderRequirementConfiguration(AbstractConfiguration):
    '''
    Configuration class representing a single header
    requirement
    '''
    REGEXP_MATCH = "regexp-match"
    ABSENT = "absent"
    PRESENT = "present"

    def __init__(self, json_data: json) -> None:
        self._validate_json(json_data)
        self._tag = (int(json_data['tag'][0], 16), int(json_data['tag'][1], 16))
        self._requirement = json_data['requirement']
        self._regexp = json_data['regexp']

    @property
    def tag(self) -> Tuple[int, int]:
        '''
        Get the DICOM tag associated with this requirement
        '''
        return self._tag

    @property
    def requirement(self) -> str:
        '''
        Get the type of requirement
        '''
        return self._requirement

    @property
    def regexp(self) -> str:
        '''Get the regular expression associated with requirement'''
        return self._regexp

    def schema(self):
        return {
            "type": "object",
            "title": "Header Requirement",
            "properties": {
                "tag": { "type": "array", "items": { "type": "string" }, "minItems": 2},
                "requirement": { "type": "string" },
                "regexp": { "type": "string" }
            },
            "required": ["tag", "requirement", "regexp"]
        }

class WorkerSetConfiguration(AbstractConfiguration):
    '''
    Class representing a single WorkerSet configuration
    '''
    def __init__(self, json_data: json) -> None:
        self._validate_json(json_data)
        self._id = json_data['id']
        self._name = json_data['name']
        self._worker_ids = json_data['worker-ids']
        self._distribution = json_data['distribution']
        self._hash_method = json_data['hash-method']
        self._accepted_scp_ids = json_data['accepted-scp-ids']
        self._header_requirements: List[HeaderRequirementConfiguration] = []
        for json_obj in json_data['header-requirements']:
            self._header_requirements.append(HeaderRequirementConfiguration(json_obj))

    def schema(self):
        return {
            "type": "object",
            "title": "Worker Set",
            "properties": {
                "id": { "type": "string" },
                "name": { "type": "string" },
                "worker-ids": {
                    "type": "array",
                    "minItems": 1,
                    "items": { "type": "string" } 
                },
                "distribution": { "type": "string" },
                "hash-method": { "type": "string" },
                "accepted-scp-ids": { 
                    "type": "array",
                    "items": { "type": "string", "minItems": 1 } 
                },
                "header-requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tag": { "type": "array", "items": { "type": "string" }, "minItems": 2},
                            "requirement": { "type": "string" },
                            "regexp": { "type": "string" }
                        }
                    }
                }
            },
            "required": [
                "id",
                "worker-ids",
                "distribution",
                "hash-method",
                "accepted-scp-ids",
                "header-requirements"]
        }

    @property
    def id(self) -> str:
        '''
        The unique id of the worker set
        '''
        return self._id

    @property
    def name(self) -> str:
        '''
        The friendly name of the worker set
        '''
        return self._name

    @property
    def worker_ids(self) -> List[str]:
        '''
        The list of worker ids included in the worker set
        '''
        return self._worker_ids

    @property
    def distribution(self):
        '''
        The distribution algorithm
        '''
        return self._distribution

    @property
    def hash_method(self):
        '''
        The hash method used to associate incoming studies
        with workers
        '''
        return self._hash_method

    @property
    def accepted_scp_ids(self) -> List[str]:
        '''
        The list of SCP ids accepted by this worker set
        '''
        return self._accepted_scp_ids

    @property
    def header_requirements(self) -> List[HeaderRequirementConfiguration]:
        '''
        Get a list of requirements which must be satisfied by a DICOM instance
        to be routed to this workerset
        '''
        return self._header_requirements


class CoreConfiguration(AbstractConfiguration):
    def __init__(self, json_data: json) -> None:
        self._validate_json(json_data)
        self._log_dir_path = json_data['log-dir-path']
        self._log_format = json_data['log-format']
        self._buffer_dir_path = json_data['buffer-dir-path']
        self._router_count = json_data['router-count']

    @property
    def log_dir_path(self):
        '''
        Path to the directory where log files are written
        '''
        return self._log_dir_path

    @property
    def log_format(self):
        '''
        Logging format to use
        '''
        return self._log_format

    @property
    def buffer_dir_path(self):
        '''
        Temporary dir used for buffering incoming files
        '''
        return self._buffer_dir_path

    @property
    def router_count(self):
        '''
        Number of routing threads to spin up
        '''
        return self._router_count

    def schema(self):
        return {
            "type": "object",
            "title": "Core",
            "properties": {
                "log-dir-path": { "type": "string" },
                "log-format": { "type": "string" },
                "buffer-dir-path": { "type": "string" },
                "router-count": { "type": "number", "minimum": 1 }
            },
            "required": ["log-dir-path", "log-format", "buffer-dir-path", "router-count"]
        }

class SCPConfiguration(AbstractConfiguration):
    def __init__(self, json_data: json) -> None:
        self._validate_json(json_data)
        self._id = json_data['id']
        self._name = json_data['name']
        self._ae_title = json_data['ae-title']
        self._address = json_data['address']
        self._port = json_data['port']

    @property
    def id(self):
        '''
        Get the unique id of this SCP
        '''
        return self._id

    @property
    def name(self):
        '''
        Get the friendly name of this SCP
        '''
        return self._name

    @property
    def ae_title(self):
        '''
        Get the AE title of this SCP
        '''
        return self._ae_title

    @property
    def address(self):
        '''
        Get the bind IP address of this SCP
        '''
        return self._address

    @property
    def port(self):
        '''
        Get the bind port of this SCP
        '''
        return self._port

    def schema(self):
        return {
            "type": "object",
            "name": "SCP",
            "properties": {
                "id": { "type": "string" },
                "name": { "type": "string" },
                "ae-title": { "type": "string" },
                "address": { "type": "string" },
                "port": { "type": "number", "minimum": 1 }
            },
            "required": ["id", "name", "ae-title", "address", "port"]
        }

class WorkerConfiguration(AbstractConfiguration):

    TYPE_SCU = "scu"
    TYPE_LOCAL_STORAGE = "local-storage"

    def __init__(self, json_data: json) -> None:
        self._validate_json(json_data)
        self._id = json_data['id']
        self._name = json_data['name']
        self._ae_title = json_data['ae-title']
        self._address = json_data['address']
        self._port = json_data['port']
        self._type = json_data['type']
        

    @property
    def id(self):
        '''
        Get the unique id of this worker
        '''
        return self._id

    @property
    def name(self):
        '''
        Get the friendly name of this worker
        '''
        return self._name

    @property
    def ae_title(self):
        '''
        Get the AE title of this worker (if type is scu)
        '''
        return self._ae_title

    @property
    def address(self):
        '''
        Get the SCP IP address (if type is scu)
        '''
        return self._address

    @property
    def port(self):
        '''
        Get the SCP port (if type is scu)
        '''
        return self._port

    @property
    def type(self):
        '''
        Get the type of worker
        '''
        return self._type

    def schema(self):
        return {
            "type": "object",
            "name": "Worker",
            "properties": {
                "type": { "type": "string" },
                "id": { "type": "string" },
                "name": { "type": "string" },
                "ae-title": { "type": "string" },
                "address": { "type": "string" },
                "port": { "type": "number" },
                "output-dir-path": { "type": "string" }
            },
            "required": ["type", "id", "name", "ae-title"]
        }

class ConfigurationError(BaseException):
    pass

class Configuration:
    '''
    Entry point class for loading full configuration files
    '''
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
        '''
        Read all configuration files in specified directory.
        If multiple configuration files are loaded, defined
        entries are simply stacked on top of each other.
        '''
        if os.path.isdir(path):
            files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            for file in files:
                self._read_config_file(file)
        else:
            raise BaseException(f'{path} is not a directory during attempt to load configuration')

    def _read_config_file(self, path) -> bool:
        '''
        Read a single config file and populate Configuration object
        '''
        self._logger.info(f'Reading config from {path}')
        with open(path) as f:
            data = json.load(f)
            self._parse_config(data)

    def _parse_config(self, config: json) -> bool:
        '''
        Parse json configuration object
        '''
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
        '''
        Get the list of workers defined in this configuration
        '''
        return self._workers

    def scps(self) -> List[SCPConfiguration]:
        '''
        Get the list of SCPs configured'''
        return self._scps

    def core(self) -> CoreConfiguration:
        '''
        Get the core configuration
        '''
        return self._core

    def worker_sets(self) -> List[WorkerSetConfiguration]:
        '''
        Get worker set configurations for all worker sets
        '''
        return self._worker_sets
