__author__ = 'keghol'

import unittest2 as unittest
from libsolace.util import get_plugin


class TestSolaceClientProfile(unittest.TestCase):
    def setUp(self):
        self.plugin = get_plugin("SolaceClientProfile", name="foo", vpn_name="bar")

    def test_get_solace_client_profile_plugin(self):
        self.assertTrue(isinstance(self.plugin.commands.commands, list))
