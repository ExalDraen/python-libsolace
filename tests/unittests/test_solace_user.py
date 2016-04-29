__author__ = 'keghol'

import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
from libsolace.plugin import PluginResponse
from tests.unittests.test_util import get_plugin_from_api, get_test_logger


import unittest2 as unittest


logging = get_test_logger()

__plugin_name__ = "SolaceUser"

test_kwargs = {
    "client_username": "my_componenet",
    "password": "passw",
    "vpn_name": "default",
    "client_profile": "default",
    "testmode": False,
    "shutdown_on_apply": False,
    "acl_profile": "default"
}

test_bad_kwargs = {
    "client_username": "my_componenet",
    "password": "passw",
    "vpn_name": "default",
    "client_profile": "doesnt_exist",
    "testmode": False,
    "shutdown_on_apply": False,
    "acl_profile": "not_default"
}


class TestSolaceUser(unittest.TestCase):
    def setUp(self):
        self.api = SolaceAPI("dev")
        self.plugin = get_plugin_from_api(self.api, __plugin_name__)

    def test_zzz_get_solace_client_profile_batch_provision(self):
        self.plugin = get_plugin_from_api(self.api, __plugin_name__, force=True, **test_kwargs)
        self.assertTrue(isinstance(self.plugin.commands.commands, list))
        self.assertEqual(self.plugin.commands.commands[0][0], '<rpc semp-version="%s"><create><client-username><username>my_componenet</username><vpn-name>default</vpn-name></client-username></create></rpc>' % self.api.version)

    def test_requirements(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).requirements(**test_kwargs)
        self.assertIsNone(xml)

    def test_bad_requirements(self):
        self.assertRaises(BaseException,
                          get_plugin_from_api(self.api, __plugin_name__).requirements(**test_bad_kwargs))

    def test_get(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).get(client_username="default", vpn_name="default")
        self.assertEqual(xml[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username'][
                             'message-vpn'], 'default')

    def test_zzx_delete(self):
        self.api.rpc(get_plugin_from_api(self.api, __plugin_name__).create_user(force=True, **test_kwargs))
        xml = get_plugin_from_api(self.api, __plugin_name__).delete(client_username="my_componenet", vpn_name="default",
                                                                    force=True, shutdown_on_apply=True,
                                                                    skip_before=True)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><no><client-username><username>my_componenet</username><vpn-name>default</vpn-name></client-username></no></rpc>' % self.api.version)

    def test_check_client_profile_exists(self):
        self.assertTrue(get_plugin_from_api(self.api, __plugin_name__).check_client_profile_exists(**test_kwargs))

    def test_check_client_profile_not_exists(self):
        self.assertFalse(get_plugin_from_api(self.api, __plugin_name__).check_client_profile_exists(**test_bad_kwargs))

    def test_check_acl_profile_exists(self):
        self.assertTrue(get_plugin_from_api(self.api, __plugin_name__).check_acl_profile_exists(**test_kwargs))

    def test_check_acl_profile_not_exists(self):
        self.assertFalse(get_plugin_from_api(self.api, __plugin_name__).check_acl_profile_exists(**test_bad_kwargs))

    def test_aaa_create_user(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).create_user(force=True, **test_kwargs)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><create><client-username><username>my_componenet</username><vpn-name>default</vpn-name></client-username></create></rpc>' % self.api.version)

    def test_ccc_shutdown(self):
        test_kwargs['shutdown_on_apply'] = True
        xml = get_plugin_from_api(self.api, __plugin_name__).shutdown(**test_kwargs)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><client-username><username>my_componenet</username><vpn-name>default</vpn-name><shutdown/></client-username></rpc>' % self.api.version)

    def test_ccd_set_client_profile(self):
        test_kwargs['shutdown_on_apply'] = True
        xml = get_plugin_from_api(self.api, __plugin_name__).set_client_profile(**test_kwargs)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><client-username><username>my_componenet</username><vpn-name>default</vpn-name><client-profile><name>default</name></client-profile></client-username></rpc>' % self.api.version)

    def test_cce_set_acl_profile(self):
        test_kwargs['shutdown_on_apply'] = True
        xml = get_plugin_from_api(self.api, __plugin_name__).set_acl_profile(**test_kwargs)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml,
                         '<rpc semp-version="%s"><client-username><username>my_componenet</username><vpn-name>default</vpn-name><acl-profile><name>default</name></acl-profile></client-username></rpc>' % self.api.version)

    def test_no_guarenteed_endpoint(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).no_guarenteed_endpoint(**test_kwargs)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml, '<rpc semp-version="%s"><client-username><username>my_componenet</username><vpn-name>default</vpn-name><no><guaranteed-endpoint-permission-override/></no></client-username></rpc>' % self.api.version)

    def test_no_subscription_manager(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).no_subscription_manager(**test_kwargs)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml, '<rpc semp-version="%s"><client-username><username>my_componenet</username><vpn-name>default</vpn-name><no><subscription-manager/></no></client-username></rpc>' % self.api.version)

    def test_set_password(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).set_password(**test_kwargs)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml, '<rpc semp-version="%s"><client-username><username>my_componenet</username><vpn-name>default</vpn-name><password><password>passw</password></password></client-username></rpc>' % self.api.version)

    def test_zzz_no_shutdown(self):
        xml = get_plugin_from_api(self.api, __plugin_name__).no_shutdown(**test_kwargs)
        self.assertIsInstance(xml, PluginResponse)
        self.assertEqual(xml.xml, '<rpc semp-version="%s"><client-username><username>my_componenet</username><vpn-name>default</vpn-name><no><shutdown/></no></client-username></rpc>' % self.api.version)