import worker
from typing import List, Dict
import configuration
import logging
import routable

class WorkerSet:
    def __init__(self, config: configuration.WorkerSetConfiguration, all_workers: Dict[str, worker.Worker], hash_function) -> None:
        self._worker_ids = config.worker_ids
        self._workers: List[worker.Worker] = []
        self._accepted_scp_ids = config.accepted_scp_ids
        for worker_id in self._worker_ids:
            self._workers.append(all_workers[worker_id])
        self._hash_function = hash_function
        self._id = config.id
        self._logger = logging.getLogger(__name__)
        self._logger.info(f'Creating worker set {self._id} with {len(self._workers)} workers')

    def can_accept(self, r: routable.Routable):
        # FIXME Make decision based on DICOM header matching
        # FIXME and originating SCP
        self._logger.debug(f'Finding worker for routable from {r.scp_id} (acceping routables from {str(self._accepted_scp_ids)}')
        if r.scp_id in self._accepted_scp_ids:
            return True
        return False


    def consume(self, data: routable.Routable):
        # Determine worker index by hashing patient id to a number
        # To ensure longitudinal support, all data for a given
        # patient must be processed by the same worker
        worker_index = self._hash_function("patient-id", len(self._workers))
        worker = self._workers[worker_index]
        self._logger.debug(f'Allocating to worker {worker.id} at index {worker_index}')
        worker.process(data)

    @property
    def id(self):
        return self._id