import unittest2 as unittest
from libsolace.util import *

class TestUtil(unittest.TestCase):

    def test_version_equal_or_greater_than(self):
        self.assertTrue(version_equal_or_greater_than('soltr/6_0', 'soltr/7_0'))
        self.assertTrue(version_equal_or_greater_than('soltr/6_0', 'soltr/6_0'))
        self.assertFalse(version_equal_or_greater_than('soltr/7_1_1', 'soltr/6_2'))
        self.assertFalse(version_equal_or_greater_than('soltr/7_1', 'soltr/6_2'))
        with self.assertRaisesRegexp(Exception, "Failed to parse version 6_2") as cm:
            version_equal_or_greater_than('6_2', 'soltr/7_0')
