from libsolace.plugin import PluginResponse

__author__ = 'keghol'

import unittest2 as unittest
from libsolace.SolaceAPI import SolaceAPI
from test_util import get_plugin_from_api

__plugin_name__ = "SolaceACLProfile"


class TestSolaceACLProfile(unittest.TestCase):
    def setUp(self):
        self.api = SolaceAPI("dev")
        self.plugin = get_plugin_from_api(self.api, __plugin_name__)

    def test_batch_mode(self):
        self.plugin = get_plugin_from_api(self.api, __plugin_name__, name="default", vpn_name="default")
        self.assertTrue(isinstance(self.plugin.commands.commands, list))
        self.assertEqual(self.plugin.commands.commands[0], ('<rpc semp-version="%s"><create><acl-profile><name>default</name><vpn-name>default</vpn-name></acl-profile></create></rpc>' % self.api.version, {'vpn_name': 'default', 'name': 'default'}))

    def test_get_profile(self):
        xml = self.plugin.get(name="default", vpn_name="default")
        self.assertIsInstance(xml, list)
        self.assertEqual(str(xml[0]),
                         "{'HOST': 'http://solace1.swe1.unibet.com/SEMP', u'rpc-reply': {u'rpc': {u'show': {u'acl-profile': {u'acl-profiles': {u'acl-profile': {u'publish-topic': {u'num-exceptions': u'0', u'allow-default-action': u'true'}, u'client-connect': {u'num-exceptions': u'0', u'allow-default-action': u'true'}, u'vpn-name': u'default', u'profile-name': u'default', u'subscribe-topic': {u'num-exceptions': u'0', u'allow-default-action': u'true'}}}}}}, u'execute-result': {u'@code': u'ok'}, u'@semp-version': u'%s'}}" % self.api.version)

    def test_new_acl(self):
        xml = self.plugin.new_acl(name="myprofile", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><create><acl-profile><name>myprofile</name><vpn-name>default</vpn-name></acl-profile></create></rpc>' % self.api.version)

    def test_allow_publish(self):
        xml = self.plugin.allow_publish(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><acl-profile><name>default</name><vpn-name>default</vpn-name><publish-topic><default-action><allow/></default-action></publish-topic></acl-profile></rpc>' % self.api.version)

    def test_allow_subscribe(self):
        xml = self.plugin.allow_subscribe(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><acl-profile><name>default</name><vpn-name>default</vpn-name><subscribe-topic><default-action><allow/></default-action></subscribe-topic></acl-profile></rpc>' % self.api.version)

    def test_allow_connect(self):
        xml = self.plugin.allow_connect(name="default", vpn_name="default")
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><acl-profile><name>default</name><vpn-name>default</vpn-name><client-connect><default-action><allow/></default-action></client-connect></acl-profile></rpc>' % self.api.version)

