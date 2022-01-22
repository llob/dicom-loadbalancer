import threading


import threading
import logging
import routable
import queue
import workerset
from typing import Dict, List

class Router(threading.Thread):
    def __init__(self, id: str, worker_sets: Dict[str, workerset.WorkerSet]) -> None:
        threading.Thread.__init__(self)
        self._id: str = id
        self._logger = logging.getLogger(__name__)
        self._queue: queue.Queue[routable.Routable] = queue.Queue()
        self._worker_sets: List[workerset.WorkerSet] = list(worker_sets.values())

    def run(self):
        self._logger.info(f'Starting router {self._id}')
        while True:
            # Get the routable
            r = self._queue.get(block=True)
            self._logger.debug(f'Routing routable in {self.id}')
            # Find a workerset which will accept this routable
            routed = False
            for worker_set in self._worker_sets:
                if worker_set.can_accept(r):
                    # Asynchronously hand the routable off to the workerset
                    worker_set.consume(r)
                    routed = True
                    break
            if not routed:
                self._logger.warn(f'No worker sets accepting routable from {r.scp_id}. Dropping routable.')

    def route(self, r: routable.Routable) -> bool:
        # Asynchronously hand over routable to the router
        self._queue.put(r)

    @property
    def id(self):
        return self._id