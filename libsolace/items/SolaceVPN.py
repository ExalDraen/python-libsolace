import logging
import libsolace
from libsolace.Decorators import only_if_not_exists, only_if_exists, primary, backup
from libsolace.SolaceReply import SolaceReplyHandler
from libsolace.plugin import Plugin, PluginResponse
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.util import get_key_from_kwargs


@libsolace.plugin_registry.register
class SolaceVPN(Plugin):
    """Manage a Solace VPN

    If `vpn_name` is passed as a kwarg, this plugin enters provision/batch mode, if it is omitted, the plugin will go into
    single query mode.

    In provision/batch mode, this plugin generates all the neccesary SEMP requests to create a VPN. You also need to pass a
    `owner_name` and a existing `acl_profile` name. If these are omitted, the vpn_name property is used.

    In single query mode, this plugin creates single SEMP requests, you need only pass a SolaceAPI into `api`, or invoke
    via SolaceAPI("dev").manage("SolaceVPN")

    :param api: The instance of SolaceAPI if not called from SolaceAPI.manage
    :param vpn_name: name of the VPN to scope the ACL to
    :type api: SolaceAPI
    :type vpn_name: str
    :rtype: SolaceVPN

    Query/Single Mode Example Direct Access:

        >>> import libsolace.settingsloader as settings
        >>> import libsolace
        >>> from libsolace.SolaceAPI import SolaceAPI
        >>> clazz = libsolace.plugin_registry("SolaceVPN", settings=settings)
        >>> api = SolaceAPI("dev")
        >>> solaceVpnPlugin = clazz(settings=settings, api=api)
        >>> list_of_dicts = solaceVpnPlugin.get(vpn_name="default")

    Provision/Batch Mode Example via SolaceAPI

        >>> api = SolaceAPI("dev")
        >>> vpn = api.manage("SolaceVPN", vpn_name="my_vpn", owner_name="someuser", acl_profile="default", max_spool_usage=1024)
        >>> #for req in vpn.commands.commands:
        >>> #   api.rpc(str(req[0]), **req[1])

    """

    plugin_name = "SolaceVPN"
    api = "None"

    default_settings = {'max_spool_usage': 4096,
                        'large_message_threshold': 4096}

    def __init__(self, **kwargs):
        if kwargs == {}:
            return

        # decorator, for caching decorator creates and set this property, Missing exception is used also, so leave
        # completely unassigned. this line is just here for reference.
        # self.exists = None

        # get the connection SolaceAPI instance
        self.api = get_key_from_kwargs("api", kwargs)

        # create a commandqueue instance for queuing up XML and validating
        self.commands = SolaceCommandQueue(version=self.api.version)

        if not "vpn_name" in kwargs:
            logging.info("No vpn_name kwarg, assuming query mode")
        else:
            self.vpn_name = get_key_from_kwargs("vpn_name", kwargs)
            self.owner_username = get_key_from_kwargs("owner_username", kwargs, default=self.vpn_name)
            self.acl_profile = get_key_from_kwargs("acl_profile", kwargs, default=self.vpn_name)
            self.options = None

            logging.debug("Creating vpn in env: %s vpn: %s, kwargs: %s" % (self.api.environment, self.vpn_name, kwargs))

            # set defaults
            for k, v in self.default_settings.items():
                logging.info("Setting Key: %s to %s" % (k, v))
                setattr(self, k, v)

            # use kwargs to tune defaults
            for k, v in self.default_settings.items():
                if k in kwargs:
                    logging.info("Overriding Key: %s to %s" % (k, kwargs[k]))
                    setattr(self, k, kwargs[k])

            # backwards compatibility for None options passed to still execute "add" code
            if self.options is None:
                logging.warning(
                        "No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
                # stack the commands
                self.create_vpn(**kwargs)
                self.clear_radius(**kwargs)
                self.set_internal_auth(**kwargs)
                self.set_spool_size(**kwargs)
                self.set_large_message_threshold(**kwargs)
                self.set_logging_tag(**kwargs)
                self.enable_vpn(**kwargs)

    @only_if_not_exists("get", 'rpc-reply.rpc.show.message-vpn.vpn')
    def create_vpn(self, **kwargs):
        """New VPN SEMP Request generator.

        :param vpn_name: The name of the VPN
        :type vpn_name: str
        :return: tuple SEMP request and kwargs

        Example:

            >>> api = SolaceAPI("dev")
            >>> tuple_request = api.manage("SolaceVPN").create_vpn(vpn_name="my_vpn")
            >>> response = api.rpc(tuple_request)


        Example2:


            >>> api = SolaceAPI("dev")
            >>> response = api.rpc(api.manage("SolaceVPN").create_vpn(vpn_name="my_vpn"))

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Create domain-event VPN, this can fail if VPN exists, but thats ok.
        self.api.x = SolaceXMLBuilder('VPN Create new VPN %s' % vpn_name, version=self.api.version)
        self.api.x.create.message_vpn.vpn_name = vpn_name
        self.commands.enqueue(self.api.x, **kwargs)
        self.set_exists(True)
        return (str(self.api.x), kwargs)

    def get(self, **kwargs):
        """Returns a VPN from the appliance immediately. This method calls the api instance so it MUST be referenced through the SolaceAPI instance, or passed a `api` kwarg.

        :param vpn_name: The name of the VPN
        :param detail: return details
        :type vpn_name: str
        :type detail: bool
        :return: dict

        Example:

            >>> api = SolaceAPI("dev")
            >>> dict_vpn = api.manage("SolaceVPN").get(vpn_name="my_vpn", detail=True)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        detail = get_key_from_kwargs("detail", kwargs, default=False)
        logging.info("Getting VPN: %s" % vpn_name)

        self.api.x = SolaceXMLBuilder("Getting VPN %s" % vpn_name, version=self.api.version)
        self.api.x.show.message_vpn.vpn_name = vpn_name
        if detail:
            self.api.x.show.message_vpn.detail

        self.commands.enqueue(self.api.x, **kwargs)

        return self.api.rpc(str(self.api.x))

    @only_if_exists("get", 'rpc-reply.rpc.show.message-vpn.vpn')
    def clear_radius(self, **kwargs):
        """Clears radius authentication mechanism

        :param vpn_name: The name of the VPN
        :type vpn_name: str
        :return: tuple SEMP request and kwargs

    Example:

        >>> api = SolaceAPI("dev")
        >>> tuple_request = api.manage("SolaceVPN").clear_radius(vpn_name="my_vpn")
        >>> response = api.rpc(tuple_request)


    Example 2:

        >>> api = SolaceAPI("dev")
        >>> response = api.rpc(api.manage("SolaceVPN").clear_radius(vpn_name="my_vpn"))


        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Switch Radius Domain to nothing
        self.api.x = SolaceXMLBuilder("VPN %s Clearing Radius" % vpn_name, version=self.api.version)
        self.api.x.message_vpn.vpn_name = vpn_name
        self.api.x.message_vpn.authentication.user_class.client
        if self.api.version == "soltr/7_1_1" or self.api.version == "soltr/7_0" or self.api.version == "soltr/6_2":
            self.api.x.message_vpn.authentication.user_class.basic.radius_domain.radius_domain
        else:
            self.api.x.message_vpn.authentication.user_class.radius_domain.radius_domain
        self.commands.enqueue(self.api.x, **kwargs)
        return (str(self.api.x), kwargs)

    @only_if_exists("get", 'rpc-reply.rpc.show.message-vpn.vpn')
    def set_internal_auth(self, **kwargs):
        """Set authentication method to internal

        :param vpn_name: The name of the VPN
        :type vpn_name: str
        :return: tuple SEMP request and kwargs

        Example:

            >>> api = SolaceAPI("dev")
            >>> tuple_request = api.manage("SolaceVPN").set_internal_auth(vpn_name="my_vpn")
            >>> response = api.rpc(tuple_request)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Switch to Internal Auth
        if self.api.version == "soltr/7_1_1" or self.api.version == "soltr/7_0" or self.api.version == "soltr/6_2":
            self.api.x = SolaceXMLBuilder("VPN %s Enable Internal Auth" % vpn_name, version=self.api.version)
            self.api.x.message_vpn.vpn_name = vpn_name
            self.api.x.message_vpn.authentication.user_class.client
            self.api.x.message_vpn.authentication.user_class.basic.auth_type.internal
        else:
            self.api.x = SolaceXMLBuilder("VPN %s Enable Internal Auth" % vpn_name, version=self.api.version)
            self.api.x.message_vpn.vpn_name = vpn_name
            self.api.x.message_vpn.authentication.user_class.client
            self.api.x.message_vpn.authentication.user_class.auth_type.internal
        self.commands.enqueue(self.api.x, **kwargs)
        return (str(self.api.x), kwargs)

    @only_if_exists("get", 'rpc-reply.rpc.show.message-vpn.vpn')
    def set_spool_size(self, **kwargs):
        """Set the maximun spool size for the VPN

        :param vpn_name: The name of the VPN
        :param max_spool_usage: size in mb
        :type vpn_name: str
        :type max_spool_usage: int
        :return: tuple SEMP request and kwargs

        Example:

            >>> api = SolaceAPI("dev")
            >>> request_tuple = api.manage("SolaceVPN").set_spool_size(vpn_name="my_vpn", max_spool_usage=4096)
            >>> response = api.rpc(request_tuple)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        max_spool_usage = get_key_from_kwargs("max_spool_usage", kwargs, self.default_settings['max_spool_usage'])

        logging.debug("Setting spool size to %s" % max_spool_usage)
        # Set the Spool Size
        self.api.x = SolaceXMLBuilder("VPN %s Set spool size to %s" % (vpn_name, max_spool_usage),
                                      version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.max_spool_usage.size = max_spool_usage
        self.commands.enqueue(self.api.x, **kwargs)
        return (str(self.api.x), kwargs)

    @only_if_exists("get", 'rpc-reply.rpc.show.message-vpn.vpn')
    def set_large_message_threshold(self, **kwargs):
        """Sets the large message threshold

        :param vpn_name: The name of the VPN
        :param large_message_threshold: size in bytes
        :type vpn_name: str
        :type large_message_threshold: int
        :return: tuple SEMP request and kwargs

        Example:

            >>> api = SolaceAPI("dev")
            >>> request_tuple = api.manage("SolaceVPN").set_large_message_threshold(vpn_name="my_vpn", large_message_threshold=4096)
            >>> response = api.rpc(request_tuple)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        large_message_threshold = get_key_from_kwargs("large_message_threshold", kwargs,
                                                      self.default_settings["large_message_threshold"])

        # Large Message Threshold
        self.api.x = SolaceXMLBuilder(
                "VPN %s Settings large message threshold event to %s" % (vpn_name, large_message_threshold),
                version=self.api.version)
        self.api.x.message_vpn.vpn_name = vpn_name
        self.api.x.message_vpn.event.large_message_threshold.size = large_message_threshold
        self.commands.enqueue(self.api.x, **kwargs)
        return (str(self.api.x), kwargs)

    @only_if_exists("get", 'rpc-reply.rpc.show.message-vpn.vpn')
    def set_logging_tag(self, **kwargs):
        """Sets the VPN logging tag, default = vpn_name

        :param vpn_name: The name of the VPN
        :param tag: string to use in logging tag
        :type vpn_name: str
        :type tag: str
        :return: tuple SEMP request and kwargs

        Example:

            >>> api = SolaceAPI("dev")
            >>> request_tuple = api.manage("SolaceVPN").set_logging_tag(vpn_name="my_vpn", tag="my_vpn_string")
            >>> response = api.rpc(request_tuple)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        tag = get_key_from_kwargs("tag", kwargs, default=vpn_name)

        # Logging Tag for this VPN
        self.api.x = SolaceXMLBuilder("VPN %s Setting logging tag to %s" % (vpn_name, vpn_name),
                                      version=self.api.version)
        self.api.x.message_vpn.vpn_name = vpn_name
        self.api.x.message_vpn.event.log_tag.tag_string = tag
        self.commands.enqueue(self.api.x, **kwargs)
        return (str(self.api.x), kwargs)

    @only_if_exists("get", 'rpc-reply.rpc.show.message-vpn.vpn')
    def enable_vpn(self, **kwargs):
        """Enable a VPN

        :param vpn_name: The name of the VPN
        :type vpn_name: str
        :return: tuple SEMP request and kwargs

        Example:

            >>> api = SolaceAPI("dev")
            >>> request_tuple = api.manage("SolaceVPN").enable_vpn(vpn_name="my_vpn")
            >>> response = api.rpc(request_tuple)


        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Enable the VPN
        self.api.x = SolaceXMLBuilder("VPN %s Enabling the vpn" % vpn_name, version=self.api.version)
        self.api.x.message_vpn.vpn_name = vpn_name
        self.api.x.message_vpn.no.shutdown
        self.commands.enqueue(self.api.x, **kwargs)
        return (str(self.api.x), kwargs)

    def list_vpns(self, **kwargs):
        """Returns a list of vpns from first / primary node only

        :param vpn_name: the vpn_name or search pattern
        :type vpn_name: str
        :return:

        Example:

            >>> api = SolaceAPI("dev")
            >>> list_dict = api.manage("SolaceVPN").list_vpns(vpn_name="*")


        """
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Getting list of VPNS", version=self.api.version)
        self.api.x.show.message_vpn.vpn_name = vpn_name

        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        response = self.api.rpc(PluginResponse(str(self.api.x), **kwargs))

        # response = SolaceReplyHandler(self.api.rpc(str(self.api.x), primaryOnly=True))
        # logging.info(response)

        return [vpn['name'] for vpn in response[0]['rpc-reply']['rpc']['show']['message-vpn']['vpn']]

    def __getitem__(self, k):
        return self.__dict__[k]
