import logging

import libsolace
from libsolace import Plugin
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.plugin import PluginResponse
from libsolace.util import get_key_from_kwargs


@libsolace.plugin_registry.register
class SolaceACLProfile(Plugin):
    """ Plugin to manage AclProfiles

    Description
    ===========
        This plugin manages ACL Profiles within Solace. Typically you should invoke this plugin via :class:`libsolace.SolaceAPI.SolaceAPI`

        Please see :class:`libsolace.plugin.Plugin` for how plugins are instantiated and used.

    """

    plugin_name = "SolaceACLProfile"

    def __init__(self, *args, **kwargs):
        """Initialize in Query or Batch mode

        Example:

            >>> from libsolace.SolaceAPI import SolaceAPI
            >>> client = SolaceAPI("dev")
            >>> client.manage("SolaceACLProfile", name="myprofile", vpn_name="testvpn").commands.commands
            [XML, XML, XML]

        :type api: SolaceAPI
        :param api: the api (passed in automatically if instantiated via SolaceAPI.manage

        Optional (Batch/Provision) Mode

        :type name: str
        :param name: the name of the ACL Profile
        :type vpn_name: str
        :param vpn_name: the vpn name
        :rtype: SolaceACLProfile
        :returns: instance with batch requests on SolaceACLProfile.commands.commands

        """
        self.api = get_key_from_kwargs("api", kwargs)  #: SolaceAPI instance
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

    def get(self, **kwargs):
        """Returns the ACL immediately as a dictionary

        :param name: name of the profile
        :param vpn_name: vpn name
        :returns: tuple SEMP request and kwargs
        :rtype: dict
        :returns: the acl profile

        """

        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Profile %s" % name, version=self.api.version)
        self.api.x.show.acl_profile.name = name
        self.api.x.show.acl_profile.vpn_name = vpn_name
        self.commands.enqueue(self.api.x)
        return self.api.rpc(PluginResponse(str(self.api.x), **kwargs))

    def new_acl(self, **kwargs):
        """Returns a SEMP request for new ACL profile.

        Example:

            >>> api = SolaceAPI("dev")
            >>> request = api.manage("SolaceACLProfile").new_acl(name="myprofile", vpn_name="dev_testvpn")
            >>> # response = api.rpc(request)

        :param name: name of the profile
        :param vpn_name: vpn name
        :rtype: PluginResponse
        :returns: single SEMP request

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Profile %s" % name, version=self.api.version)
        self.api.x.create.acl_profile.name = name
        self.api.x.create.acl_profile.vpn_name = vpn_name
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def allow_publish(self, **kwargs):
        """Allow publish

        Example:

            >>> api = SolaceAPI("dev")
            >>> request = api.manage("SolaceACLProfile").allow_publish(name="myprofile", vpn_name="dev_testvpn")
            >>> # response = api.rpc(request)

        :param name: name of the profile
        :param vpn_name: vpn name
        :rtype: PluginResponse
        :returns: single SEMP request

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow Publish %s" % name, version=self.api.version)
        self.api.x.acl_profile.name = name
        self.api.x.acl_profile.vpn_name = vpn_name
        self.api.x.acl_profile.publish_topic.default_action.allow
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def allow_subscribe(self, **kwargs):
        """ Allow subscribe

        :param name: name of the profile
        :param vpn_name: vpn name
        :rtype: PluginResponse
        :returns: single SEMP request

        Example:

            >>> api = SolaceAPI("dev")
            >>> request = api.manage("SolaceACLProfile").allow_subscribe(name="myprofile", vpn_name="dev_testvpn")
            >>> # api.rpc(request)

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("VPN %s Allowing ACL Profile to subscribe to VPN" % name,
                                      version=self.api.version)
        self.api.x.acl_profile.name = name
        self.api.x.acl_profile.vpn_name = vpn_name
        self.api.x.acl_profile.subscribe_topic.default_action.allow
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def allow_connect(self, **kwargs):
        """ Allow Connect

        :param name: name of the profile
        :param vpn_name: vpn name
        :rtype: PluginResponse
        :returns: single SEMP request

        Example:
            
            >>> api = SolaceAPI("dev")
            >>> request = api.manage("SolaceACLProfile").allow_subscribe(name="myprofile", vpn_name="dev_testvpn")
            >>> # response = api.rpc(request)

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("VPN %s Allowing ACL Profile to connect to VPN" % name, version=self.api.version)
        self.api.x.acl_profile.name = name
        self.api.x.acl_profile.vpn_name = vpn_name
        self.api.x.acl_profile.client_connect.default_action.allow
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)


