import unittest
import configuration

class TestConfiguration(unittest.TestCase):
    def test_read_configuration_file(self):
        c = configuration.Configuration('test/data/config/sample-config.json')
        self.assertEqual(len(c.workers()), 2)
        self.assertEqual(len(c.worker_sets()), 1)
        self.assertEqual(len(c.worker_sets()[0].header_requirements), 1)
        self.assertEqual(len(c.scps()), 1)
        self.assertIsNotNone(c.core())
        

    def test_read_configuration_dir(self):
        c = configuration.Configuration('test/data/config')
        self.assertEqual(len(c.workers()), 4)
        self.assertEqual(len(c.worker_sets()), 2)
        self.assertEqual(len(c.scps()), 2)
        self.assertIsNotNone(c.core())

if __name__ == "__main__":
    unittest.main()