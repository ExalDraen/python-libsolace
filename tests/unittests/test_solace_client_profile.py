from libsolace.plugin import PluginResponse

__author__ = 'keghol'

import unittest2 as unittest
import libsolace
from libsolace.SolaceAPI import SolaceAPI
from test_util import get_plugin_from_api

__plugin_name__ = "SolaceClientProfile"

class TestSolaceClientProfile(unittest.TestCase):
    def setUp(self):
        self.api = SolaceAPI("dev")
        self.plugin = get_plugin_from_api(self.api, __plugin_name__)

    def test_batch_mode(self):
        self.plugin = get_plugin_from_api(self.api, __plugin_name__, name="default", vpn_name="bar")
        self.assertTrue(isinstance(self.plugin.commands.commands, list))

    def test_get_profile(self):
        dict_response = self.plugin.get(name="default", vpn_name="default")
        self.assertIsInstance(dict_response, dict)
        self.assertEqual(dict['reply']['show']['client-profile']['profiles']['profile'['name']], 'default')
                         # "{'reply': {'show': {'client-profile': {'profiles': {'profile': {'name': 'default', 'num-users': '1', 'message-vpn': 'default'}}}}}, 'backup': {'show': {'client-profile': {'profiles': {'profile': {'name': 'default', 'num-users': '1', 'message-vpn': 'default'}}}}}, 'primary': {'show': {'client-profile': {'profiles': {'profile': {'name': 'default', 'num-users': '1', 'message-vpn': 'default'}}}}}}")

    def test_new_client_profile(self):
        xml = self.plugin.new_client_profile(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><create><client-profile><name>default</name><vpn-name>default</vpn-name></client-profile></create></rpc>' % self.api.version)

    def test_delete_profile(self):
        xml = self.plugin.delete(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><no><client-profile><name>default</name><vpn-name>default</vpn-name></client-profile></no></rpc>' % self.api.version)

    def test_allow_consume(self):
        xml = self.plugin.allow_consume(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><client-profile><name>default</name><vpn-name>default</vpn-name><message-spool><allow-guaranteed-message-receive/></message-spool></client-profile></rpc>' % self.api.version)

    def test_allow_send(self):
        xml = self.plugin.allow_send(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><client-profile><name>default</name><vpn-name>default</vpn-name><message-spool><allow-guaranteed-message-send/></message-spool></client-profile></rpc>' % self.api.version)

    def test_allow_endpoint_create(self):
        xml = self.plugin.allow_endpoint_create(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><client-profile><name>default</name><vpn-name>default</vpn-name><message-spool><allow-guaranteed-endpoint-create/></message-spool></client-profile></rpc>' % self.api.version)

    def test_allow_transacted_sessions(self):
        xml = self.plugin.allow_transacted_sessions(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><client-profile><name>default</name><vpn-name>default</vpn-name><message-spool><allow-transacted-sessions/></message-spool></client-profile></rpc>' % self.api.version)

    def test_set_max_clients(self):
        xml = self.plugin.set_max_clients(name="default", vpn_name="default", max_clients=10)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><client-profile><name>default</name><vpn-name>default</vpn-name><max-connections-per-client-username><value>10</value></max-connections-per-client-username></client-profile></rpc>' % self.api.version)

    def test_allow_bridging(self):
        xml = self.plugin.allow_bridging(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><client-profile><name>default</name><vpn-name>default</vpn-name><allow-bridge-connections/></client-profile></rpc>' % self.api.version)
