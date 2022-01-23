import unittest
import livenesschecker
import pydicom
import utils
import configuration

class TestLivenessStatus(unittest.TestCase):
    def test_enum_values(self):
        self.assertIsNotNone(livenesschecker.LivenessStatus.HARD_FAIL)
        self.assertIsNotNone(livenesschecker.LivenessStatus.SOFT_FAIL)
        self.assertIsNotNone(livenesschecker.LivenessStatus.LIVE)
        self.assertIsNotNone(livenesschecker.LivenessStatus.UNKNOWN)

class TestDicomEchoLivenessCheckerStrategy(unittest.TestCase):
    def test_ctor(self):
        hostname = "127.0.0.1"
        port = 12345
        s = livenesschecker.DicomEchoLivenessCheckerStrategy(hostname, port)
        self.assertEqual(s.hostname, hostname)
        self.assertEqual(s.port, port)

    def test_failed_check(self):
        hostname = "127.0.0.1"
        port = 12345
        s = livenesschecker.DicomEchoLivenessCheckerStrategy(hostname, port)
        self.assertEqual(livenesschecker.LivenessStatus.HARD_FAIL, s.check())

    def test_successful_check(self):
        ss: utils.SimpleScp = utils.start_scp()
        s = livenesschecker.DicomEchoLivenessCheckerStrategy(ss.hostname, ss.port)
        self.assertEqual(livenesschecker.LivenessStatus.LIVE, s.check())
        ss.shutdown()


class MockLivenessCheckerStrategy(livenesschecker.LivenessCheckerStrategy):
    def __init__(self, check_result):
        self._check_result = check_result

    def check(self):
        return self._check_result

class MockConfiguration(configuration.Configuration):
    def __init__(self):
        pass

class TestLivenessChecker(unittest.TestCase):

    def test_ctor(self):
        checker_id = "id1"
        strategy = MockLivenessCheckerStrategy(livenesschecker.LivenessStatus.LIVE)
        config = MockConfiguration()
        lc = livenesschecker.LivenessChecker(checker_id, strategy, config, 1)
        lc.start()
        self.assertEqual(livenesschecker.LivenessStatus.LIVE, lc.status)
        lc.shutdown()