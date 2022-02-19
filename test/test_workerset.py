import unittest
import unittest.mock
import logging
import workerset
import configuration
import routable

class MockWorkerSetConfiguration(configuration.WorkerSetConfiguration):
    def __init__(self) -> None:
        pass

class TestWorkerSet(unittest.TestCase):
    def test_ctor(self):
        config = unittest.mock.Mock(spec=configuration.WorkerSetConfiguration)
        config.worker_ids = []
        config.accepted_scp_ids = []
        workers = {}
        hash_function = lambda x: x
        ws = workerset.WorkerSet(config, workers, hash_function)

    def test_can_accept1(self):
        logging.basicConfig(
            level=logging.DEBUG, 
            format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s')

        mock_routable = unittest.mock.Mock(spec=routable.Routable)
        mock_routable.scp_id = 'scp1'
        mock_config = unittest.mock.Mock(spec=configuration.WorkerSetConfiguration)
        mock_config.worker_ids = []
        mock_config.accepted_scp_ids = []
        mock_config.header_requirements = []
        workers = {}
        hash_function = lambda x: x
        ws = workerset.WorkerSet(mock_config, workers, hash_function)        
        # Should always be False, as no workers can accept the routable
        self.assertEqual(False, ws.can_accept(mock_routable))