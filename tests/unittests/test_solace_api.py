__author__ = 'keghol'

from libsolace.plugin import PluginResponse
from libsolace.SolaceAPI import SolaceAPI

import unittest2 as unittest

class TestSolaceAPI(unittest.TestCase):
    def setUp(self):
        self.solace = SolaceAPI('dev')

    def test_connect(self):
        self.assertIsInstance(self.solace, SolaceAPI)

    def test_testmode(self):
        self.solace = SolaceAPI("dev", testmode=True)
        self.assertTrue(self.solace.testmode)

    def test_testmode(self):
        self.solace = SolaceAPI("dev", testmode=False)
        self.assertFalse(self.solace.testmode)

    def test_bad_config(self):
        with self.assertRaises(Exception):
            self.solace = SolaceAPI("bad")

    def test_single_node_bad_config(self):
        with self.assertRaises(Exception):
            self.solace = SolaceAPI("bad", detect_status=False)

    def test_single_appliance(self):
        self.solace = SolaceAPI("single", detect_status=False)
        self.assertEqual(self.solace.primaryRouter, "http://solace1.swe1.unibet.com/SEMP")

    def test_failed_detection(self):
        with self.assertRaises(Exception):
            self.solace = SolaceAPI("backup_only")

    def test_failed_detection2(self):
        with self.assertRaises(Exception):
            self.solace = SolaceAPI("primary_only")

    def test_bad_config_no_mgmt(self):
        with self.assertRaises(Exception):
            self.solace = SolaceAPI("bad_no_mgmt", detect_status=False)

    def test_backup_only_rpc(self):
        self.solace = SolaceAPI("dev")
        self.solace.rpc('<rpc semp-version="soltr/6_0"><show><message-spool/></show></rpc>', backupOnly=True)

    def test_get_redundancy(self):
        response = SolaceAPI("dev").get_redundancy()
        self.assertIsInstance(response, list)

    def test_get_redundancy_error(self):
        with self.assertRaises(Exception):
            response = SolaceAPI("dev", version="foo").get_redundancy()

    def test_get_memory(self):
        memory = SolaceAPI("dev").get_memory()
        self.assertIsInstance(memory, list)

    def test_plugin_response_rpc(self):
        p = PluginResponse('<rpc semp-version="soltr/6_0"><show><message-spool/></show></rpc>', primaryOnly=True)
        x = self.solace.rpc(p)
        self.assertIsInstance(x, list)

    def test_plugin_rpc_tuple(self, **kwargs):
        res = ('<rpc semp-version="soltr/6_0"><show><message-spool/></show></rpc>', kwargs)
        x = self.solace.rpc(res)
        self.assertIsInstance(x, list)

    def test_plugin_rpc_bad_request_object(self):
        res = []
        with self.assertRaises(Exception):
            x = self.solace.rpc(res)

    def test_manage(self):
        x = self.solace.manage("SolaceUser")
        self.assertEqual(str(x.__class__), "<class 'libsolace.items.SolaceUser.SolaceUser'>")