import logging

from libsolace.plugin import PluginResponse

__author__ = 'keghol'

import unittest2 as unittest
from libsolace.SolaceAPI import SolaceAPI
from test_util import get_plugin_from_api

__plugin_name__ = "SolaceQueue"


class TestSolaceQueue(unittest.TestCase):
    def setUp(self):
        self.api = SolaceAPI("dev")
        self.plugin = get_plugin_from_api(self.api, __plugin_name__)
        self.queue_config = {
            "retries": 0,
            "consume": "all",
            "exclusive": "true",
            "max_bind_count": 10,
            "queue_size": 1024,
            "owner": "default"
        }

    def test_zzz_batch_mode(self):
        self.plugin = get_plugin_from_api(self.api, __plugin_name__,
                                          queues=[{"name": "solacetest.prov.queue", "queue_config": self.queue_config}],
                                          vpn_name="default")
        self.assertTrue(isinstance(self.plugin.commands.commands, list))
        print(self.plugin.commands.commands[0])
        self.assertEqual(self.plugin.commands.commands[0], (
        '<rpc semp-version="%s"><show><queue><name>solacetest.prov.queue</name><vpn-name>default</vpn-name></queue></show></rpc>' % self.api.version,
        {'queues': [{'name': 'solacetest.prov.queue',
                     'queue_config': {'retries': 0, 'consume': 'all', 'exclusive': 'true', 'max_bind_count': 10,
                                      'queue_size': 1024, 'owner': 'default'}}], 'queue_name': 'solacetest.prov.queue',
         'primaryOnly': True, 'vpn_name': 'default'}))

    def test_get_queue(self):
        xml = self.plugin.get(queue_name="please.dont.exist", vpn_name="default")
        self.assertIsInstance(xml, list)
        self.assertEqual(str(xml[0]),
                         "{'HOST': 'http://solace1.swe1.unibet.com/SEMP', u'rpc-reply': {u'rpc': {u'show': {u'queue': {u'queues': None}}}, u'execute-result': {u'@code': u'ok'}, u'@semp-version': u'%s'}}" % self.api.version)

    # testing overlaying config empty = class defaults
    def test_get_queue_config_defaults(self):
        config = self.plugin.get_queue_config({"name": "testqueue1",
                                               "env":
                                                   [
                                                       {"name": "dev", "queue_config": {}}
                                                   ]
                                               }
                                              )
        self.assertEqual(config, self.plugin.defaults)

    # test setting config to specific values
    def test_get_queue_config(self):
        config = self.plugin.get_queue_config({"name": "testqueue1",
                                               "env":
                                                   [
                                                       {"name": "dev", "queue_config": {
                                                           "retries": 1,
                                                           "exclusive": "false",
                                                           "max_bind_count": 10,
                                                           "owner": "somebody",
                                                           "queue_size": 1,
                                                           "consume": "not_all"
                                                       }}
                                                   ]
                                               }
                                              )
        self.assertEqual(config, {"retries": 1,
                                  "exclusive": "false",
                                  "max_bind_count": 10,
                                  "owner": "somebody",
                                  "queue_size": 1,
                                  "consume": "not_all"
                                  })

    def test_create_queue(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).create_queue(queue_name="some_new_queue",
                                                                          vpn_name="default", force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><create><queue><name>some_new_queue</name></queue></create></message-spool></rpc>' % self.api.version)

    def test_shutdown_egress(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).shutdown_egress(queue_name="somequeue_name",
                                                                             vpn_name="default", shutdown_on_apply=True,
                                                                             force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><shutdown><egress/></shutdown></queue></message-spool></rpc>' % self.api.version)

    def test_shutdown_egress_without_shutdown(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).shutdown_egress(queue_name="somequeue_name",
                                                                             vpn_name="default")
        self.assertIs(xml, None)

    def test_shutdown_ingress(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).shutdown_ingress(queue_name="somequeue_name",
                                                                              vpn_name="default",
                                                                              shutdown_on_apply=True, force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><shutdown><ingress/></shutdown></queue></message-spool></rpc>' % self.api.version)

    def test_shutdown_ingress_without_shutdown(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).shutdown_ingress(queue_name="somequeue_name",
                                                                              vpn_name="default")
        self.assertIs(xml, None)

    def test_exclusive(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).exclusive(queue_name="somequeue_name", vpn_name="default",
                                                                       shutdown_on_apply=True, exclusive=True,
                                                                       force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><access-type><exclusive/></access-type></queue></message-spool></rpc>' % self.api.version)

    def test_owner(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).owner(queue_name="somequeue_name", vpn_name="default",
                                                                   owner_username="someuser", force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><owner><owner>someuser</owner></owner></queue></message-spool></rpc>' % self.api.version)

    def test_max_bind_count(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).max_bind_count(queue_name="somequeue_name",
                                                                            vpn_name="default", max_bind_count=10,
                                                                            force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><max-bind-count><value>10</value></max-bind-count></queue></message-spool></rpc>' % self.api.version)

    def test_consume(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).consume(queue_name="somequeue_name", vpn_name="default",
                                                                     consume="all", force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><permission><all/><consume/></permission></queue></message-spool></rpc>' % self.api.version)

    def test_permission_consume(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).permission(queue_name="somequeue_name", vpn_name="default",
                                                                        permission="consume", force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><permission><all/><consume/></permission></queue></message-spool></rpc>' % self.api.version)

    def test_permission_delete(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).permission(queue_name="somequeue_name", vpn_name="default",
                                                                        permission="delete", force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><permission><all/><delete/></permission></queue></message-spool></rpc>' % self.api.version)

    def test_permission_modify_topic(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).permission(queue_name="somequeue_name", vpn_name="default",
                                                                        permission="modify-topic", force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><permission><all/><modify-topic/></permission></queue></message-spool></rpc>' % self.api.version)

    def test_permission_readonly(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).permission(queue_name="somequeue_name", vpn_name="default",
                                                                        permission="read-only", force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><permission><all/><read-only/></permission></queue></message-spool></rpc>' % self.api.version)

    def test_spool_size(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).spool_size(queue_name="somequeue_name", vpn_name="default",
                                                                        queue_size=10, force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><max-spool-usage><size>10</size></max-spool-usage></queue></message-spool></rpc>' % self.api.version)

    def test_retries(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).retries(queue_name="somequeue_name", vpn_name="default",
                                                                     retries=9, force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><max-redelivery><value>9</value></max-redelivery></queue></message-spool></rpc>' % self.api.version)

    def test_enable(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).enable(queue_name="somequeue_name", vpn_name="default",
                                                                    force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><no><shutdown><full/></shutdown></no></queue></message-spool></rpc>' % self.api.version)

    def test_reject_on_discard(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).reject_on_discard(queue_name="somequeue_name",
                                                                               vpn_name="default", force=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><message-spool><vpn-name>default</vpn-name><queue><name>somequeue_name</name><reject-msg-to-sender-on-discard/></queue></message-spool></rpc>' % self.api.version)
