'''
Liveness checker module
'''
import threading
from time import sleep
import logging
import enum

import configuration
import livenesscheckerstrategy

class LivenessStatus(enum.Enum):
    LIVE = 0
    UNKNOWN = 1
    SOFT_FAIL = 2
    HARD_FAIL = 3


class LivenessChecker(threading.Thread):

    def __init__(
        self,
        id: str,
        strategy: livenesscheckerstrategy.LivenessCheckerStrategy
        config: configuration.WorkerConfiguration,
        check_interval: int) -> None:

        threading.Thread.__init__(self)
        self._id = id
        self._check_interval = check_interval
        self._confg = config
        self._liveness_status = LivenessStatus.UNKNOWN
        self._logger = logging.getLogger(__name__)

    def _set_liveness_status(self, status: LivenessStatus) -> None:
        self._logger.info('Setting liveness status to %s for %s', status, self._id)
        self._liveness_status(status)

    def _check_liveness(self) -> None:
        self._set_liveness_status(LivenessStatus.LIVE)

    def run(self):
        self._logger.info('Starting liveness checker %s. Checking liveness every %d seconds.', self._id, self._check_interval)
        while True:
            self._check_liveness()
            sleep(self._check_interval)

    @property
    def status(self) -> LivenessStatus:
        return self._liveness_status
