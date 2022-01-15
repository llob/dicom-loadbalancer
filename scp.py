# TCP -> AE Server1 -> StoreHandler -> Router1 -> WorkerClient1 -> SCU Client -> TCP
# TCP -> AE Server2 -> StoreHandler -> Router2 -> WorkerClient2 -> SCU Client -> TCP
#                                              -> WorkerClient3 -> SCU Client -> TCP


from pydicom.uid import ExplicitVRLittleEndian

from pynetdicom import AE, debug_logger, evt
from pynetdicom.sop_class import CTImageStorage
from pynetdicom.sop_class import MRImageStorage
import configuration

debug_logger()

config = configuration.Configuration('test/data/config')

def handle_store(event):
    return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store)]

ae = AE()
ae.add_supported_context(CTImageStorage, ExplicitVRLittleEndian)
ae.start_server(("127.0.0.1", 11112), block=True, evt_handlers=handlers)