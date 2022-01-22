from abc import ABC, abstractmethod

class LivenessCheckerStrategy:

    @abstractmethod
    def check(self):
        pass

class DicomEchoLivenessCheckerStrategy:
    def __init__(self, hostname: str, port: int) -> None:
        self._hostname = hostname
        self._port = port

    def check(self):
        # FIXME
        pass