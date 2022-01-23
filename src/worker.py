'''
Worker module
'''
import threading
import datetime
import threading
import logging
import queue
from typing import List

from pynetdicom import AE
from pynetdicom.sop_class import CTImageStorage
from pynetdicom.sop_class import MRImageStorage

import configuration
import routable
import livenesschecker

class Worker(threading.Thread):
    def __init__(self, config: configuration.WorkerConfiguration) -> None:
        threading.Thread.__init__(self)
        self._id = config.id
        self._logger = logging.getLogger(__name__)
        self._address = config.address
        self._port = config.port
        self._ae_title = config.ae_title
        self._name = config.name
        self._queue = queue.Queue()
        self._buffer: List[routable.Routable] = []
        self._last_send_time: datetime.datetime = datetime.datetime.now()
        self._liveness_checker = livenesschecker.LivenessChecker(
            self._id, 
            livenesschecker.DicomEchoLivenessCheckerStrategy(self._address, self._port), 
            config, 
            10)

    @property
    def id(self) -> str:
        return self._id

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
        self._logger.info(f'Starting worker {self._id}')
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

    def process(self, data: routable.Routable):
        self._queue.put(data)