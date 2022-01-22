import unittest
import hash_functions

class TestHashFunctions(unittest.TestCase):
    def test_random(self):
        # Ensure that we calculate the right value
        self.assertEqual(hash_functions.random(b"hest", 2), 1)
        # Ensure that calculated value is reproducible
        self.assertEqual(hash_functions.random(b"hest", 2), 1)
        # Ensure that a much larger module value can
        # provide a much larger result
        self.assertEqual(hash_functions.random(b"hest", 100), 21)
        # Ensure that excessively large values are rejected
        with self.assertRaises(BaseException):
            hash_functions.random(b'hest', 1000000)
        with self.assertRaises(BaseException):
            hash_functions.random(b'b'*1000000, 10)


unittest.main()