# TCP -> AE Server1 -> StoreHandler -> Router1 -> WorkerClient1 -> SCU Client -> TCP
# TCP -> AE Server2 -> StoreHandler -> Router2 -> WorkerClient2 -> SCU Client -> TCP
#                                              -> WorkerClient3 -> SCU Client -> TCP


import threading
from typing import Dict
from pydicom.uid import ExplicitVRLittleEndian

from pynetdicom import AE, debug_logger, evt
import pynetdicom.sop_class
import pynetdicom
import configuration
import logging
import router
import routable

#debug_logger()

#config = configuration.Configuration('test/data/config')

#def handle_store(event):
#    return 0x0000

#handlers = [(evt.EVT_C_STORE, handle_store)]

#ae = AE()
#ae.add_supported_context(CTImageStorage, ExplicitVRLittleEndian)
#ae.start_server(("127.0.0.1", 11112), block=True, evt_handlers=handlers)

class SCP(threading.Thread):
    def __init__(self, config: configuration.SCPConfiguration, routers: Dict[str, router.Router]) -> None:
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(__name__)
        self._id = config.id
        self._name = config.name
        self._ae_title = config.ae_title
        self._address = config.address
        self._port = config.port
        self._routers = list(routers.values())
        self._ae = None
        self._current_router_index = 0

    def _next_router(self) -> router.Router:
        # Round robin over available routers
        self._current_router_index = (self._current_router_index + 1) % len(self._routers)
        return self._routers[self._current_router_index]

    def _handle_store(self, event: pynetdicom.events.Event):
        # Create a routable to encapsulate DICOM
        # and required meta data
        r = routable.Routable(self._id, event.dataset)
        router = self._next_router()
        # Hand routable off to router in a buffered
        # non-blocking way
        self._logger.debug(f'Routing via {router.id}')
        router.route(r)
        return 0x0000

    def _handle_echo(self):
        return 0x0000

    def run(self):
        self._logger.info(f'Starting SCP {self._id} on {self._address}:{self._port}')
        handlers = [
            (evt.EVT_C_STORE, self._handle_store),
            (evt.EVT_C_ECHO, self._handle_echo)
            ]

        self._ae = AE()
        self._ae.add_supported_context("1.2.840.10008.1.1")
        self._ae.add_supported_context(pynetdicom.sop_class.MRImageStorage, ExplicitVRLittleEndian)
        self._ae.add_supported_context(pynetdicom.sop_class.CTImageStorage, ExplicitVRLittleEndian)
        self._ae.add_supported_context(pynetdicom.sop_class.EnhancedCTImageStorage, ExplicitVRLittleEndian)
        self._ae.add_supported_context(pynetdicom.sop_class.EnhancedMRImageStorage, ExplicitVRLittleEndian)
        self._ae.start_server((self._address, self._port), block=True, evt_handlers=handlers)        

    @property
    def id(self):
        return self._id
