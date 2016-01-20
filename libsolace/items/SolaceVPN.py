import logging
import libsolace
from libsolace.SolaceReply import SolaceReplyHandler
from libsolace.plugin import Plugin
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.util import get_key_from_kwargs


@libsolace.plugin_registry.register
class SolaceVPN(Plugin):
    """

    Creates a VPN

    """

    plugin_name = "SolaceVPN"
    api = "None"

    default_settings = {'max_spool_usage': 4096,
                        'large_message_threshold': 4096}

    def __init__(self, **kwargs):
        """
        Creates a VPN

        Parameters
        ----------
        vpn_name : str
            The name of the VPN to create
        max_spool_usage : int
            The optional max spool size, default in default_settings
        large_message_threshold: int
            The optional large message threshold, default in default_settings
        acl_profile: str
            The optional acl_profile to associate with, default is `vpn_name`

        """

        if kwargs == {}:
            return

        # get the connection SolaceAPI instance
        self.api = get_key_from_kwargs("api", kwargs)

        # create a commandqueue instance for queuing up XML and validating
        self.commands = SolaceCommandQueue(version=self.api.version)

        if not "vpn_name" in kwargs:
            logging.info("No vpn_name kwarg, assuming query mode")
        else:
            self.vpn_name = get_key_from_kwargs("vpn_name", kwargs)
            self.owner_username = get_key_from_kwargs("vpn_name", kwargs)
            self.environment = get_key_from_kwargs("environment", kwargs, default=self.api.environment)
            self.acl_profile = get_key_from_kwargs("vpn_name", kwargs, default=self.vpn_name)
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
            if self.options == None:
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

    def create_vpn(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Create domain-event VPN, this can fail if VPN exists, but thats ok.
        self.api.x = SolaceXMLBuilder('VPN Create new VPN %s' % vpn_name, version=self.api.version)
        self.api.x.create.message_vpn.vpn_name = vpn_name
        self.commands.enqueue(self.api.x)

    def clear_radius(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Switch Radius Domain to nothing
        self.api.x = SolaceXMLBuilder("VPN %s Clearing Radius" % vpn_name, version=self.api.version)
        self.api.x.message_vpn.vpn_name = self.vpn_name
        self.api.x.message_vpn.authentication.user_class.client
        if self.api.version == "soltr/7_1_1" or self.api.version == "soltr/7_0" or self.api.version == "soltr/6_2":
            self.api.x.message_vpn.authentication.user_class.basic.radius_domain.radius_domain
        else:
            self.api.x.message_vpn.authentication.user_class.radius_domain.radius_domain
        self.commands.enqueue(self.api.x)

    def set_internal_auth(self, **kwargs):

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
        self.commands.enqueue(self.api.x)

    def set_spool_size(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        max_spool_usage = get_key_from_kwargs("max_spool_usage", kwargs, getattr(self, "max_spool_usage"))

        logging.debug("Setting spool size to %s" % getattr(self, 'max_spool_usage'))
        # Set the Spool Size
        self.api.x = SolaceXMLBuilder("VPN %s Set spool size to %s" % (vpn_name, max_spool_usage),
                                      version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.max_spool_usage.size = max_spool_usage
        self.commands.enqueue(self.api.x)

    def set_large_message_threshold(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        large_message_threshold = get_key_from_kwargs("large_message_threshold", kwargs,
                                                      getattr(self, "large_message_threshold"))

        # Large Message Threshold
        self.api.x = SolaceXMLBuilder(
            "VPN %s Settings large message threshold event to %s" % (vpn_name, large_message_threshold),
            version=self.api.version)
        self.api.x.message_vpn.vpn_name = vpn_name
        self.api.x.message_vpn.event.large_message_threshold.size = large_message_threshold
        self.commands.enqueue(self.api.x)

    def set_logging_tag(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Logging Tag for this VPN
        self.api.x = SolaceXMLBuilder("VPN %s Setting logging tag to %s" % (vpn_name, vpn_name),
                                      version=self.api.version)
        self.api.x.message_vpn.vpn_name = vpn_name
        self.api.x.message_vpn.event.log_tag.tag_string = vpn_name
        self.commands.enqueue(self.api.x)

    def enable_vpn(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Enable the VPN
        self.api.x = SolaceXMLBuilder("VPN %s Enabling the vpn" % vpn_name, version=self.api.version)
        self.api.x.message_vpn.vpn_name = vpn_name
        self.api.x.message_vpn.no.shutdown
        self.commands.enqueue(self.api.x)

    def list_vpns(self, **kwargs):

        """
        Returns a list of vpns

        :param vpn_name: the vpn_name search pattern to apply.
        :return:
        """
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Getting list of VPNS", version=self.api.version)
        self.api.x.show.message_vpn.vpn_name = vpn_name
        response = SolaceReplyHandler(self.api.rpc(str(self.api.x), primaryOnly=True))

        return [vpn['name'] for vpn in response.reply.show.message_vpn.vpn]

    def __getitem__(self, k):
        return self.__dict__[k]
