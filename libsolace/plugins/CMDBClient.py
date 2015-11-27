import logging
import libsolace
from libsolace.plugin import Plugin

@libsolace.plugin_registry.register
class CMDBClient(Plugin):

    # the name used to call the plugin
    plugin_name = "CMDBClient"

    def __init__(self, *args, **kwargs):
        logging.info("Spawning instance of CMDBClient")
        pass

    def configure(self, settings=None, **kwargs):
        logging.info("Configuring")
        pass

    def get_vpns_by_owner(self, owner_name, environment='dev', **kwargs):
        vpns = []

        vpn1 = {}
        vpn1['owner'] = 'SolaceTest'
        vpn1['vpn_config'] = {}
        vpn1['vpn_config']['spool_size'] = '1024'
        vpn1['password'] = 'd0nt_u5e_th1s'
        vpn1['name'] = '%s_testvpn'

        vpns.append(vpn1)
        return vpns

    def get_users_of_vpn(self, vpn_name, environment='dev', **kwargs):
        users = []

        user1 = {}
        user1['username'] = '%s_testproductA'
        user1['password'] = 'somepassword'

        users.append(user1)
        return users

    def get_queues_of_vpn(self, vpn_name, environment='dev', **kwargs):
        queues = []

        queue1 = {}
        queue1['queue_config'] = {}
        queue1['queue_config']["exclusive"] = "true"
        queue1['queue_config']["queue_size"] = "4096"
        queue1['queue_config']["retries"] = 0
        queue1['queue_config']["exclusive"] = "false"
        queue1["name"] = "testqueue1"

        queues.append(queue1)
        return queues
