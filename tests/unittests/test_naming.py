import unittest
from libsolace.Naming import name


class TestNaming(unittest.TestCase):
    def test_valid(self):
        f = name("test_%s_test", "dev")
        self.assertEqual(f, "test_dev_test")

    def test_fail(self):
        with self.assertRaises(Exception):
            name("test", "test")


