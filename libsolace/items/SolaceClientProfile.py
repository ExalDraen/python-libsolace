import logging
import libsolace
from libsolace.SolaceReply import SolaceReplyHandler
from libsolace.plugin import Plugin, PluginResponse
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.util import version_equal_or_greater_than
from libsolace.util import get_key_from_kwargs


@libsolace.plugin_registry.register
class SolaceClientProfile(Plugin):
    """Create / Manage client profiles

    This plugin manages Client Profiles within Solace. Typically you should invoke this plugin via :class:`libsolace.SolaceAPI.SolaceAPI`

    Please see :class:`libsolace.plugin.Plugin` for how plugins are instantiated and used.

    Example of direct instantiation and passing in a instance SolaceAPI

        >>> import libsolace.settingsloader as settings
        >>> import libsolace
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> clazz = libsolace.plugin_registry("SolaceClientProfile", settings=settings)
        >>> api = SolaceAPI("dev")
        >>> scp = clazz(settings=settings, api=api)
        >>> client_dict = scp.get(api=api, name="default", vpn_name="default")

    Example of Instantiation via the SolaceAPI manage method

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> api = SolaceAPI("dev")
        >>> scp = api.manage("SolaceClientProfile")
        >>> client_dict = scp.get(api=api, name="default", vpn_name="default")
        >>> list_xml = api.manage("SolaceClientProfile", name="myprofile", vpn_name="dev_testvpn").commands.commands

    """

    plugin_name = "SolaceClientProfile"

    defaults = {
        "max_clients": 1000
    }

    def __init__(self, **kwargs):
        """Initialize in Query or Batch mode

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> client = SolaceAPI("dev")
        >>> client.manage("SolaceClientProfile", name="myprofile", vpn_name="testvpn").commands.commands
        [XML, XML, XML]

        :param api: The instance of SolaceAPI if not called from SolaceAPI.manage

        Optional (Batch/Provision) Mode

        :param name: the name of the profile
        :param vpn_name: name of the VPN to scope the ACL to
        :param defaults: dictionary of defaults
        :param max_clients: max clients sharing a username connection limit
        :type api: SolaceAPI
        :type name: str
        :type vpn_name: str
        :type defaults: dict
        :type max_clients: int
        :returns: instance with batch requests on SolaceACLProfile.commands.commands
        :rtype: SolaceClientProfile
        """

        self.api = get_key_from_kwargs("api", kwargs)
        self.commands = SolaceCommandQueue(version=self.api.version)
        kwargs.pop("api")

        if kwargs == {}:
            return

        if not "name" in kwargs:
            logging.info("No name kwarg, assuming query mode")
            return

        self.name = get_key_from_kwargs('name', kwargs)
        self.vpn_name = get_key_from_kwargs('vpn_name', kwargs)
        self.defaults = get_key_from_kwargs('defaults', kwargs, default=self.defaults)
        self.max_clients = get_key_from_kwargs('max_clients', kwargs, default=self.defaults.get("max_clients"))

        if kwargs.get('options', None) is None:
            logging.warning(
                "No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            self.new_client_profile(**kwargs)
            self.allow_consume(**kwargs)
            self.allow_send(**kwargs)
            self.allow_endpoint_create(**kwargs)
            self.allow_transacted_sessions(**kwargs)

    def get(self, **kwargs):
        """Returns a ClientProfile immediately from both appliances

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> api = SolaceAPI("dev")
        >>> response = api.manage("SolaceClientProfile").get(name="default", vpn_name="default")

        :param name: name of the profile
        :param vpn_name: the name of the vpn to scope the request to
        :param details: get more details boolean
        :type name: str
        :type vpn_name: str
        :type details: bool
        :rtype: libsolace.SolaceReplyHandler
        :returns: dictionary representation of client profile

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        details = get_key_from_kwargs("details", kwargs, default=False)

        self.api.x = SolaceXMLBuilder("Get Client Profile", version=self.api.version)
        self.api.x.show.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.show.client_profile.vpn_name = vpn_name
        if details:
            self.api.x.show.client_profile.details
        # enqueue to validate
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return self.api.rpc(PluginResponse(str(self.api.x), **kwargs))

    # @only_if_not_exists('get', 'rpc-reply.rpc.show.message-vpn.vpn')
    def new_client_profile(self, **kwargs):
        """Create a new client profile

        Enqueues the request in self.commands and returns the SEMP request via PluginResponse.

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> api = SolaceAPI("dev")
        >>> plugin_response = api.manage("SolaceClientProfile").new_client_profile(name="default", vpn_name="default")

        :param name: name of the profile
        :param vpn_name: the name of the vpn to scope the request to
        :type name: str
        :type vpn_name: str
        :returns: dictionary representation of client profile
        :rtype: plugin.PluginResponse

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Create Client Profile", version=self.api.version)
        self.api.x.create.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.create.client_profile.vpn_name = vpn_name
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def delete(self, **kwargs):
        """Delete a client profile

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> api = SolaceAPI("dev")
        >>> plugin_response = api.manage("SolaceClientProfile").delete(name="default", vpn_name="default")

        :param name: name of the profile
        :param vpn_name: the name of the vpn to scope the request to
        :type name: str
        :type vpn_name: str
        :returns: SEMP request
        :rtype: plugin.PluginResponse
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        self.api.x = SolaceXMLBuilder("Delete Client Profile", version=self.api.version)
        self.api.x.no.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.no.client_profile.vpn_name = vpn_name
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def allow_consume(self, **kwargs):
        """Allow consume permission

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> api = SolaceAPI("dev")
        >>> plugin_response = api.manage("SolaceClientProfile").allow_consume(name="default", vpn_name="default")

        :param name: name of the profile
        :param vpn_name: the name of the vpn to scope the request to
        :type name: str
        :type vpn_name: str
        :returns: SEMP request
        :rtype: plugin.PluginResponse

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow profile consume", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_guaranteed_message_receive
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def allow_send(self, **kwargs):
        """Allow send permission

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> api = SolaceAPI("dev")
        >>> plugin_response = api.manage("SolaceClientProfile").allow_send(name="default", vpn_name="default")

        :param name: name of the profile
        :param vpn_name: the name of the vpn to scope the request to
        :type name: str
        :type vpn_name: str
        :returns: SEMP request
        :rtype: plugin.PluginResponse

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow profile send", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_guaranteed_message_send
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def allow_endpoint_create(self, **kwargs):
        """Allow endpoint creation permission

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceClientProfile").allow_endpoint_create(name="default", vpn_name="default")
        >>> # response = api.rpc(request)

        :param name: name of the profile
        :param vpn_name: the name of the vpn to scope the request to
        :type name: str
        :type vpn_name: str
        :returns: SEMP request
        :rtype: plugin.PluginResponse

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow profile endpoint create", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_guaranteed_endpoint_create
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def allow_transacted_sessions(self, **kwargs):
        """Allow transaction sessions permission

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceClientProfile").allow_transacted_sessions(name="default", vpn_name="default")
        >>> # response = api.rpc(request)

        :param name: name of the profile
        :param vpn_name: the name of the vpn to scope the request to
        :type name: str
        :type vpn_name: str
        :returns: SEMP request
        :rtype: plugin.PluginResponse

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow profile transacted sessions", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_transacted_sessions
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def set_max_clients(self, **kwargs):
        """Set max clients for profile

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceClientProfile").set_max_clients(name="default", vpn_name="default", max_clients=500)
        >>> # response = api.rpc(request)

        :param name: name of the profile
        :param vpn_name: the name of the vpn to scope the request to
        :param max_clients: max number of clients
        :type name: str
        :type vpn_name: str
        :type max_clients: int
        :returns: SEMP request
        :rtype: plugin.PluginResponse

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        max_clients = get_key_from_kwargs("max_clients", kwargs)

        self.api.x = SolaceXMLBuilder("Setting Max Clients", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.max_connections_per_client_username.value = max_clients
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def allow_bridging(self, **kwargs):
        """Allow bridging

        Example:

        >>> import libsolace.settingsloader as settings
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> plugin = SolaceAPI("dev", version="soltr/7_1_1").manage("SolaceClientProfile")
        >>> request = plugin.allow_bridging(name="default", vpn_name="default")
        >>> request.xml
        '<rpc semp-version="soltr/7_1_1"><client-profile><name>default</name><vpn-name>default</vpn-name><allow-bridge-connections/></client-profile></rpc>'
        >>> # api.rpc(request)

        :param name: name of the profile
        :param vpn_name: the name of the vpn to scope the request to
        :type name: str
        :type vpn_name: str
        :returns: SEMP request
        :rtype: plugin.PluginResponse

        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Setting Bridging", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.allow_bridge_connections
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)
