import worker
from typing import List, Dict, Tuple
import configuration
import logging
import routable
import pynetdicom
import pydicom
import re

class WorkerSet:
    def __init__(self, config: configuration.WorkerSetConfiguration, all_workers: Dict[str, worker.Worker], hash_function) -> None:
        self._worker_ids = config.worker_ids
        self._header_requirements = config.header_requirements
        self._workers: List[worker.Worker] = []
        self._accepted_scp_ids = config.accepted_scp_ids
        for worker_id in self._worker_ids:
            self._workers.append(all_workers[worker_id])
        self._hash_function = hash_function
        self._id = config.id
        self._logger = logging.getLogger(__name__)
        self._logger.info(f'Creating worker set {self._id} with {len(self._workers)} workers')

    def _evaluate_header_absent(self, tag: Tuple[int, int], dataset: pydicom.Dataset) -> bool:
        return tag not in dataset

    def _evaluate_header_regexp_match(self, tag: Tuple[int, int], dataset: pydicom.Dataset, regexp: str) -> bool:
        if not self._evaluate_header_present(tag, dataset):
            return False
        header_value = dataset[tag]
        header_value = str(dataset[tag].value)
        match = re.match(regexp, header_value)
        if match:
            return True
        else:
            return False

    def _evaluate_header_present(self, tag: Tuple[int, int], dataset: pydicom.Dataset) -> bool:
        return tag in dataset

    def can_accept(self, r: routable.Routable):
        # If accepted SCP ids were specified and not empty
        # reject if source SCP not in list
        self._logger.debug(f'Finding worker for routable from {r.scp_id} (acceping routables from {str(self._accepted_scp_ids)}')
        if self._accepted_scp_ids and r.scp_id not in self._accepted_scp_ids:
            return False

        # Check specified header requirements
        # if any
        if self._header_requirements:
            can_accept = True
            for header_requirement in self._header_requirements:
                tag = header_requirement.tag
                if header_requirement.requirement == configuration.HeaderRequirementConfiguration.ABSENT:
                    can_accept &= self._evaluate_header_absent(tag, r.dataset)
                elif header_requirement.requirement == configuration.HeaderRequirementConfiguration.PRESENT:
                    can_accept &= self._evaluate_header_present(tag, r.dataset)
                elif header_requirement.requirement == configuration.HeaderRequirementConfiguration.REGEXP_MATCH:
                    can_accept &= self._evaluate_header_regexp_match(tag, r.dataset, header_requirement.regexp)
                else:
                    self._logger.warn(f'Unknown header requirement type {header_requirement.requirement}')
            return can_accept
        return True


    def consume(self, data: routable.Routable):
        # Determine worker index by hashing patient id to a number
        # To ensure longitudinal support, all data for a given
        # patient must be processed by the same worker
        patient_id_tag = (0x0010,0x0020)
        if patient_id_tag not in data.dataset:
            self._logger.warn('Dropping DICOM instance due to missing patient id')
            return
        patient_id = str(data.dataset[patient_id_tag].value)

        worker_index = self._hash_function(patient_id, len(self._workers))
        worker = self._workers[worker_index]
        self._logger.debug(f'Allocating to worker {worker.id} at index {worker_index}')
        worker.process(data)

    @property
    def id(self):
        return self._id