class Routable:
    def __init__(self, scp_id: str, event) -> None:
        self._scp_id = scp_id
        self._event = event

    @property
    def scp_id(self):
        return self._scp_id