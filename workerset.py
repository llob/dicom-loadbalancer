import worker
from typing import List, Dict
import configuration
import logging

class WorkerSet:
    def __init__(self, config: configuration.WorkerSetConfiguration, all_workers: Dict[str, worker.Worker], hash_function) -> None:
        self._workers: Dict[str, worker.Worker] = {}
        for worker_id in config.worker_ids:
            self._workers[worker_id] = all_workers[worker_id]
        self._hash_function = hash_function
        self._id = config.id
        self._logger = logging.getLogger(__name__)
        self._logger.info(f'Creating worker set {self._id} with {len(self._workers)} workers')


    def can_accept(self):
        # FIXME Make decision based on DICOM header matching
        # FIXME and originating SCP
        return True

    def send(self, data):
        # Determine worker index by hashing patient id to a number
        # To ensure longitudinal support, all data for a given
        # patient must be processed by the same worker
        self._hash_function("patient-id", len(self._workers))

    @property
    def id(self):
        return self._id