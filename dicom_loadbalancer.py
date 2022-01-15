import configuration
import worker
import router
import workerset
#import scp
from typing import Dict
import logging
import hash_functions

class DicomLoadBalancer:
    def __init__(self, config: configuration.Configuration) -> None:
        self._config: configuration.Configuration = config
        self._workers: Dict[str, worker.Worker] = {}
        self._routers: Dict[str, router.Router] =  {}
        self._worker_sets: Dict[str, workerset.WorkerSet] = {}
 #       self._scps: Dict[str, scp.Scp] = {}
        self._logger = logging.getLogger(__name__)

    def start(self):
        self._create_workers()
        self._create_worker_sets()
        self._create_routers()
#        self._create_scps()

    def _create_workers(self):
        self._logger.info('Creating workers')
        for worker_config in self._config.workers():
            w = worker.Worker(worker_config)
            w.start()
            self._workers[w.id] = w

    def _create_worker_sets(self):
        for worker_set_config in self._config.worker_sets():
            ws = workerset.WorkerSet(worker_set_config, self._workers, hash_functions.random)
            self._worker_sets[ws.id] = ws

    def _create_routers(self):
        pass

    def _create_scps(self):
        pass
 