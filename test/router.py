# Class which consumes and routes
# DICOMs received by the SCPs

import queue
import threading
import workerset 
from typing import List

class Router(threading.Thread):
    def __init__(self, worker_sets: List[workerset.WorkerSet]) -> None:
        # Thread safe synchronizing queue
        self._queue = queue.Queue()
        self._worker_sets = worker_sets

    def run(self):
        while True: 
            # Blocking call to read from queue
            element = self._queue.get()
            # Make routing decision
            for worker_set in self._worker_sets:
                if worker_set.can_accept(element):
                    # Hand off DICOM to worker set
                    # which takes care of distributing 
                    # to the appropriate worker
                    worker_set.send(element)
                    continue
            print('Failed to find a worker set to send data. Dropping data.')


    def route(self, element):
        # Non-blocking insertion into queue
        self._queue.put(element)

    