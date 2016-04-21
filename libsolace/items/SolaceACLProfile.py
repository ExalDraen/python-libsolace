import logging

import libsolace
from libsolace import Plugin
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.util import get_key_from_kwargs


@libsolace.plugin_registry.register
class SolaceACLProfile(Plugin):
    """ Construct the ACLProfile which is specific for the VPN e.g: "si1_domainevent"
    """

    plugin_name = "SolaceACLProfile"

    def __init__(self, *args, **kwargs):
        """
        Manage ACLProfiles

        Example:

        >>> import libsolace.settingsloader as settings
        >>> import libsolace
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> client = SolaceAPI("dev")
        >>> client.manage("SolaceACLProfile", name="myprofile", vpn_name="testvpn").commands.commands

        :type api: SolaceAPI
        :type name: str
        :type vpn_name: str

        :param api: The instance of SolaceAPI if not called from SolaceAPI.manage
        :param name: name of ACL
        :param vpn_name: name of the VPN to scope the ACL to

        """

        self.api = get_key_from_kwargs("api", kwargs)
        self.commands = SolaceCommandQueue(version=self.api.version)
        kwargs.pop("api")

        if kwargs == {}:
            return
        self.name = get_key_from_kwargs('name', kwargs)
        self.vpn_name = get_key_from_kwargs('vpn_name', kwargs)

        if kwargs.get('options', None) is None:
            logging.warning(
                    "No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            # queue up the commands
            self.new_acl(**kwargs)
            self.allow_publish(**kwargs)
            self.allow_subscribe(**kwargs)
            self.allow_connect(**kwargs)

    def new_acl(self, **kwargs):
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Profile %s" % name, version=self.api.version)
        self.api.x.create.acl_profile.name = name
        self.api.x.create.acl_profile.vpn_name = vpn_name
        self.commands.enqueue(self.api.x)
        return self.api.x


    def allow_publish(self, **kwargs):
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow Publish %s" % name, version=self.api.version)
        self.api.x.acl_profile.name = name
        self.api.x.acl_profile.vpn_name = vpn_name
        self.api.x.acl_profile.publish_topic.default_action.allow
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_subscribe(self, **kwargs):
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("VPN %s Allowing ACL Profile to subscribe to VPN" % name, version=self.api.version)
        self.api.x.acl_profile.name = name
        self.api.x.acl_profile.vpn_name = vpn_name
        self.api.x.acl_profile.subscribe_topic.default_action.allow
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_connect(self, **kwargs):
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("VPN %s Allowing ACL Profile to connect to VPN" % name, version=self.api.version)
        self.api.x.acl_profile.name = name
        self.api.x.acl_profile.vpn_name = vpn_name
        self.api.x.acl_profile.client_connect.default_action.allow
        self.commands.enqueue(self.api.x)
        return self.api.x
