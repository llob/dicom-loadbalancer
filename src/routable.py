import pydicom

class Routable:
    def __init__(self, scp_id: str, dataset: pydicom.Dataset) -> None:
        self._scp_id = scp_id
        self._dataset = dataset

    @property
    def scp_id(self) -> str:
        return self._scp_id

    @property
    def dataset(self) -> pydicom.Dataset:
        return self._dataset