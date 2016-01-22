__author__ = 'keghol'

import unittest2 as unittest
from libsolace.util import get_plugin
from libsolace.SolaceAPI import SolaceAPI

class TestSolaceVPN(unittest.TestCase):
    def setUp(self):
        self.plugin = get_plugin("SolaceVPN", SolaceAPI("dev"))

    def test_list_vpns(self):
        r = self.plugin.list_vpns(vpn_name='*')
        self.assertTrue(isinstance(r, list))
