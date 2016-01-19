"""

Mock implementation of what a CMDBClient should return, This is typically a simple HTTP client which
interacts with whatever Configuration Management system you have. It could also just interact with JSON
files if that is what you want.

"""

import logging
import libsolace
from libsolace.plugin import Plugin
from libsolace.Naming import name


@libsolace.plugin_registry.register
class CMDBClient(Plugin):

    # the name used to call the plugin
    plugin_name = "CMDBClient"

    # since we instantiate instances early on, call configure before use to
    # "init" the instance object of the Plugin
    def __init__(self, settings=None, **kwargs):
        logging.info("Configuring with settings: %s" % settings)
        url = settings.CMDB_URL

    def get_vpns_by_owner(self, owner_name, environment='dev', **kwargs):
        """
        return a LIST of vpns groups by some "owner", each VPN contains final config,
        so all environment overrides and that should be taken care of here!
        """
        vpns = []

        vpn1 = {}
        vpn1['owner'] = 'SolaceTest'
        vpn1['vpn_config'] = {}
        vpn1['vpn_config']['spool_size'] = '1024'
        vpn1['password'] = 'd0nt_u5e_th1s'
        vpn1['id'] = name('%s_testvpn' % environment)
        vpn1['name'] = name(vpn1['id'], environment)

        vpns.append(vpn1)
        return vpns

    def get_users_of_vpn(self, vpn_name, environment='dev', **kwargs):
        """
        Just return a list of users for a VPN
        """
        users = []

        user1 = {}
        user1['username'] = name('%s_testproductA', environment)
        user1['password'] = 'somepassword'

        users.append(user1)
        return users

    def get_queues_of_vpn(self, vpn_name, environment='dev', **kwargs):
        """
        As with VPN, all configs should be finalized before returned.
        """
        queues = []

        queue1 = {}
        queue1['queue_config'] = {}
        queue1['queue_config']["exclusive"] = "true"
        queue1['queue_config']["queue_size"] = "4096"
        queue1['queue_config']["retries"] = 0
        queue1['queue_config']['max_bind_count'] = 1000
        # %lsVPN is a special owner which sets the owner to the VPN itself
        queue1['queue_config']['owner'] = name("%s_testvpn" % environment)
        queue1['queue_config']["consume"] = "all"
        queue1["name"] = "testqueue1"

        queues.append(queue1)
        return queues
