import worker
from typing import List

class WorkerSet:
    def __init__(self, workers: List[Worker], hash_function) -> None:
        self._workers = workers
        self._hash_function = hash_function

    def can_accept(self):
        # FIXME Make decision based on DICOM header matching
        # FIXME and originating SCP
        return True

    def send(self, data):
        # Determine worker index by hashing patient id to a number
        # To ensure longitudinal support, all data for a given
        # patient must be processed by the same worker
        self._hash_function("patient-id", len(self._workers)