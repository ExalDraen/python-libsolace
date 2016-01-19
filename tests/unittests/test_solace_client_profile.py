__author__ = 'keghol'

import unittest2 as unittest
import libsolace.settingsloader as settings
import libsolace
from libsolace.SolaceAPI import SolaceAPI

def getPlugin(plugin_name, **kwargs):
    """
    mimics the SolaceAPI manage method, creates a SolaceAPI instance also
    since the version detection is dependent on that.
    """
    plugin = libsolace.plugin_registry(plugin_name, **kwargs)
    solace_api = SolaceAPI("dev")
    return plugin(api = solace_api, **kwargs)

class TestSolaceClientProfile(unittest.TestCase):
    def setUp(self):
        self.plugin = getPlugin("SolaceClientProfile", name="foo", vpn_name="bar")

    def test_get_solace_client_profile_plugin(self):
        self.assertTrue(isinstance(self.plugin.commands.commands, list))
