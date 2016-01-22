"""

Mock implementation of what a CMDBClient should return, This is typically a simple HTTP client which
interacts with whatever Configuration Management system you have. It could also just interact with JSON
files if that is what you want.

All object names should be finalized by this plugin, so utilize Naming.name to to set final names.

"""

import logging
import libsolace
from libsolace.plugin import Plugin
from libsolace.Naming import name
from libsolace.util import get_key_from_settings
from libsolace.util import get_key_from_kwargs

@libsolace.plugin_registry.register
class CMDBClient(Plugin):

    # the name used to call the plugin
    plugin_name = "CMDBClient"

    def __init__(self, settings=None, **kwargs):
        """
        Example:
        >>> cmdbapi =
        :param settings:
        :param kwargs:
        :return:
        """
        logging.debug("Configuring with settings: %s" % settings)
        self.settings = settings.__dict__  # type: dict
        self.url = get_key_from_settings("CMDB_URL", self.settings)

    def get_vpns_by_owner(self, *args, **kwargs):
        """
        return a LIST of vpns groups by some "owner", each VPN contains final config,
        so all environment overrides and that should be taken care of here!
        :param environment: the name of the environment
        """

        owner_name = args[0]  # type: str
        environment = get_key_from_kwargs("environment", kwargs)  # type: str

        vpns = []

        vpn1 = {}
        vpn1['owner'] = owner_name
        vpn1['vpn_config'] = {}
        vpn1['vpn_config']['spool_size'] = '1024'
        vpn1['password'] = 'd0nt_u5e_th1s'
        vpn1['id'] = '%s_testvpn'
        vpn1['name'] = name(vpn1['id'], environment)

        vpns.append(vpn1)
        return vpns

    def get_users_of_vpn(self, *args, **kwargs):
        """
        Just return a list of users for a VPN
        """

        vpn_name = args[0]  # type: str
        environment = get_key_from_kwargs("environment", kwargs)  # type: str

        users = []

        user1 = {}
        user1['username'] = name('%s_testproductA', environment)
        user1['password'] = 'somepassword'

        users.append(user1)
        return users

    def get_queues_of_vpn(self, *args, **kwargs):
        """
        As with VPN, all configs should be finalized before returned.
        """

        vpn_name = args[0]  # type: str
        environment = get_key_from_kwargs("environment", kwargs)  # type: str

        queues = []

        queue1 = {}
        queue1['queue_config'] = {}
        queue1['queue_config']["exclusive"] = "true"
        queue1['queue_config']["queue_size"] = "4096"
        queue1['queue_config']["retries"] = 0
        queue1['queue_config']['max_bind_count'] = 1000
        queue1['queue_config']['owner'] = name("%s_testproductA", environment)
        queue1['queue_config']["consume"] = "all"
        queue1["name"] = "testqueue1"

        queues.append(queue1)
        return queues
