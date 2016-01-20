__author__ = 'keghol'

import unittest2 as unittest
import libsolace
from libsolace.SolaceAPI import SolaceAPI


def getPlugin(plugin_name, **kwargs):
    """
    mimics the SolaceAPI manage method, creates a SolaceAPI instance also
    since the version detection is dependent on that.
    """
    plugin = libsolace.plugin_registry(plugin_name, **kwargs)
    solace_api = SolaceAPI("dev")
    return plugin(api=solace_api, **kwargs)


class TestSolaceClientProfile(unittest.TestCase):
    def setUp(self):
        self.plugin = getPlugin("SolaceClientProfile")

    def test_get_solace_client_profile_plugin(self):
        self.plugin = getPlugin("SolaceClientProfile", name="foo", vpn_name="bar")
        self.assertTrue(isinstance(self.plugin.commands.commands, list))

    def test_delete_profile(self):
        xml = self.plugin.delete(name="foo", vpn_name="bar")
        self.assertEqual(str(xml),
                         '<rpc semp-version="soltr/6_0"><no><client-profile><name>foo</name></client-profile></no></rpc>')
