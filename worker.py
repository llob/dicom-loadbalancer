import threading
from unicodedata import name
import configuration
import threading
import logging

class Worker(threading.Thread):
    def __init__(self, config: configuration.WorkerConfiguration) -> None:
        threading.Thread.__init__(self)
        self._id = config.id
        self._logger = logging.getLogger(__name__)


    @property
    def id(self) -> str:
        return self._id

    def run(self):
        self._logger.info(f'Starting worker {self._id}')
