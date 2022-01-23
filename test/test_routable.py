import unittest
import routable
import pydicom

class TestRoutable(unittest.TestCase):
    def test_ctor(self):
        dataset = pydicom.Dataset()
        scp_id = "id1"
        r = routable.Routable(scp_id, dataset)
        self.assertEqual(dataset, r.dataset)
        self.assertEqual(scp_id, r.scp_id)