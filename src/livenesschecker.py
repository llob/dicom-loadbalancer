'''
Liveness checker module
'''
import threading
from abc import ABC, abstractmethod
from time import sleep
import logging
import enum

import pynetdicom

import configuration

class LivenessStatus(enum.Enum):
    LIVE = 0
    UNKNOWN = 1
    SOFT_FAIL = 2
    HARD_FAIL = 3

class LivenessCheckerStrategy:
    '''
    Abstract class for encapulating strategies for checking
    liveness of worker endpoints
    '''
    @abstractmethod
    def check(self):
        '''
        Perform the liveness check implemented by this
        liveness checker strategy
        '''

class DicomEchoLivenessCheckerStrategy(LivenessCheckerStrategy):
    '''
    Liveness checking strategy based on Dicom verification services.
    As such, this liveness checker checks connectivity as well as
    DICOM availability.
    '''
    def __init__(self, hostname: str, port: int) -> None:
        '''
        Construct a new DicomEchoLivenessCheckerStrategy
        '''
        self._hostname = hostname
        self._port = port
        self._logger = logging.getLogger(__name__)


    def check(self):
        '''
        Perform liveness check
        '''
        self._logger.debug('Checking liveness of {}:{}'.format(self._hostname, self._port))
        ae = pynetdicom.AE()
        ae.add_requested_context('1.2.840.10008.1.1')
        assoc = ae.associate(self._hostname, self._port)
        if assoc.is_established:
            assoc.release()
            return LivenessStatus.LIVE
        return LivenessStatus.HARD_FAIL

    @property
    def hostname(self) -> str:
        return self._hostname
    
    @property
    def port(self) -> int:
        return self._port

class LivenessChecker(threading.Thread):

    def __init__(
        self,
        id: str,
        strategy: LivenessCheckerStrategy,
        config: configuration.WorkerConfiguration,
        check_interval: int) -> None:

        threading.Thread.__init__(self)
        self._id = id
        self._check_interval = check_interval
        self._confg = config
        self._strategy = strategy
        self._liveness_status = LivenessStatus.UNKNOWN
        self._shutdown = False
        self._logger = logging.getLogger(__name__)

    def _set_liveness_status(self, status: LivenessStatus) -> None:
        self._logger.info('Setting liveness status to %s for %s', status, self._id)
        self._liveness_status = status

    def _check_liveness(self) -> None:
        self._set_liveness_status(self._strategy.check())

    def run(self):
        self._logger.info('Starting liveness checker %s. Checking liveness every %d seconds.', self._id, self._check_interval)
        while True:
            self._check_liveness()
            sleep(self._check_interval)
            if self._shutdown:
                return

    @property
    def status(self) -> LivenessStatus:
        return self._liveness_status

    def shutdown(self):
        self._shutdown = True
