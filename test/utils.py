from time import sleep
from typing import Tuple

import pynetdicom
import pydicom

class SimpleScp:
    def __init__(self) -> None:
        self._hostname = "127.0.0.1"
        self._port = 12345
        self._ae = pynetdicom.AE()
        self._ae.add_supported_context(
            pynetdicom.sop_class.CTImageStorage, 
            pydicom.uid.ExplicitVRLittleEndian)
        self._ae.add_supported_context(
            pynetdicom.sop_class.MRImageStorage, 
            pydicom.uid.ExplicitVRLittleEndian)
        self._ae.add_supported_context(
            '1.2.840.10008.1.1',
            pydicom.uid.ExplicitVRLittleEndian
        )


    def run(self):
        self._ae.start_server((self._hostname, self._port), block=False)
        sleep(3)

    @property
    def hostname(self) -> str:
        return self._hostname

    @property
    def port(self) -> int:
        return self._port

    def shutdown(self):
        self._ae.shutdown()

def start_scp() -> SimpleScp:
    ss = SimpleScp()
    ss.run()
    return ss
