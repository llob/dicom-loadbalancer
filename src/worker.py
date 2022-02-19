'''
Worker module
'''
import threading
import datetime
import threading
import logging
import queue
from typing import List
import abc
import os

from pynetdicom import AE
from pynetdicom.sop_class import CTImageStorage
from pynetdicom.sop_class import MRImageStorage

import configuration
import routable
import livenesschecker

class Worker(threading.Thread, metaclass=abc.ABCMeta):
    def __init__(self, config: configuration.WorkerConfiguration) -> None:
        threading.Thread.__init__(self)
        self._id = config.id
        self._logger = logging.getLogger(__name__)
        self._name = config.name
        self._queue = queue.Queue()
        
    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def process(self, data: routable.Routable):
        self._queue.put(data)

class LocalStorageWorker(Worker):
    def __init__(self, config: configuration.WorkerConfiguration) -> None:
        Worker.__init__(self, config)
        self._output_dir_path = self._path_replace(config.output_dir_path)
        if not os.path.isdir(self._output_dir_path):
            raise configuration.ConfigurationError(f'Local storage worker {self.name} ({self.id}) configured to store outputs in non-existant dir {self._output_dir_path}')

    def _path_replace(self, path: str):
        result = path.replace(r'%id%', self.id)
        return result

    def run(self):
        self._logger.info(f'Starting local storage worker {self._id}')
        while True:
            try:
                r = self._queue.get(block=True, timeout=5)
                self._write_routable(r)
            except queue.Empty as e:
                # Queue is empty, so go back to waiting on queue
                pass

    def _write_routable(self, r: routable.Routable) -> bool:
        instance_uid = str(r.dataset[0x0008, 0x0018].value)
        output_file_path = os.path.join(self._output_dir_path, instance_uid + '.dcm')

        if os.path.isfile(output_file_path):
            self._logger.debug(f'Skipping instance with id {instance_uid} as it is already stored in output dir')
            return True
            
        try:
            r.dataset.save_as(output_file_path, write_like_original=True)
            return True
        except BaseException as exception:
            self._logger.warn(f'Failed to write instance to {output_file_path}: {str(exception)}')
            return False


class SCUWorker(Worker):
    def __init__(self, config: configuration.WorkerConfiguration) -> None:
        Worker.__init__(self, config)
        self._address = config.address
        self._port = config.port
        self._ae_title = config.ae_title
        self._buffer: List[routable.Routable] = []
        self._last_send_time: datetime.datetime = datetime.datetime.now()
        self._liveness_checker = livenesschecker.LivenessChecker(
            self._id, 
            livenesschecker.DicomEchoLivenessCheckerStrategy(self._address, self._port), 
            config, 
            10)

    def _send_buffer(self):
        if not self._buffer:
            # Do nothing if buffer is empty
            return

        if (datetime.datetime.now() - self._last_send_time).seconds < 3:
            # We just stopped sending, so take a short break
            return

        # Nothing preventing us from sending, so let's go
        ae = AE()
        ae.add_requested_context(MRImageStorage)
        ae.add_requested_context(CTImageStorage)
        assoc = ae.associate(self._address, self._port)
        if assoc.is_established:
            self._logger.debug(f'Established association with {self._address}:{self._port}')
            while self._buffer:
                r = self._buffer.pop()
                status = assoc.send_c_store(r.data)
                if not status:
                    self._buffer.append(r)
                    self._logger.warn(f'Failed to send to peer at {self._address}:{self._port}')
                    return

            assoc.release()
        else:
            self._logger.warn(f'Failed to establish association with {self._address}:{self._port}')


    def run(self):
        self._logger.info(f'Starting SCU worker {self._id}')
        self._liveness_checker.start()
        while True:
            try:
                r = self._queue.get(block=True, timeout=5)
                self._buffer.append(r)
            except queue.Empty as e:
                # Queue is empty, so add nothing to buffer
                pass
            # Try to send, if something is in the buffer
            self._send_buffer()
