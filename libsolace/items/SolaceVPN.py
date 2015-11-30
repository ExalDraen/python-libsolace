import logging
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder

class SolaceVPN:
    """

    Build up all the commands with SolaceXMLBuilder required to build this VPN,
    then append them to the command queue.

    """

    default_settings = {'max_spool_usage': 4096,
                        'large_message_threshold': 4096}

    def __init__(self, environment, vpn_name, options=None, version="soltr/6_0", **kwargs):
        """
        :type environment: str
        :type vpn_name: str
        :type max_spool_usage: int
        :type large_message_threshold: int

        :param environment: environment name
        :param vpn_name: vpn name
        :param max_spool_usage: size in MB of the spool
        :param large_message_threshold: size in bytes of the large_message_threshold

        """

        logging.debug("Creating vpn in env: %s vpn: %s, options: %s, kwargs: %s" % ( environment, vpn_name, options, kwargs ))

        self.queue = SolaceCommandQueue(version=version)
        self.vpn_name = vpn_name % environment
        self.owner_username = self.vpn_name
        self.environment = environment
        self.acl_profile = self.vpn_name

        # set defaults
        for k,v in self.default_settings.items():
            logging.debug("Setting Key: %s to %s" % (k,v))
            setattr(self, k, v)

        # use kwargs to tune defaults
        for k,v in self.default_settings.items():
            if k in kwargs:
                logging.debug("Overriding Key: %s to %s" % (k,kwargs[k]))
                setattr(self, k, kwargs[k])

        # backwards compatibility for None options passed to still execute "add" code
        if options == None:
            logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            # stack the commands
            self._create_vpn()
            self._clear_radius()
            self._set_internal_auth()
            self._set_spool_size()
            self._set_large_message_threshold()
            self._set_logging_tag()
            self._enable_vpn()

    def _create_vpn(self):
        # Create domain-event VPN, this can fail if VPN exists, but thats ok.
        cmd = SolaceXMLBuilder('VPN Create new VPN %s' % self.vpn_name)
        cmd.create.message_vpn.vpn_name = self.vpn_name
        self.queue.enqueue(cmd)

    def _clear_radius(self):
        # Switch Radius Domain to nothing
        cmd = SolaceXMLBuilder("VPN %s Clearing Radius" % self.vpn_name)
        cmd.message_vpn.vpn_name = self.vpn_name
        cmd.message_vpn.authentication.user_class.client
        cmd.message_vpn.authentication.user_class.radius_domain.radius_domain
        self.queue.enqueue(cmd)

    def _set_internal_auth(self):
        # Switch to Internal Auth
        cmd = SolaceXMLBuilder("VPN %s Enable Internal Auth" % self.vpn_name)
        cmd.message_vpn.vpn_name = self.vpn_name
        cmd.message_vpn.authentication.user_class.client
        cmd.message_vpn.authentication.user_class.auth_type.internal
        self.queue.enqueue(cmd)

    def _set_spool_size(self):
        logging.debug("Setting spool size to %s" % getattr(self, 'max_spool_usage'))
        # Set the Spool Size
        cmd = SolaceXMLBuilder("VPN %s Set spool size to %s" % (self.vpn_name, self.max_spool_usage))
        cmd.message_spool.vpn_name = self.vpn_name
        cmd.message_spool.max_spool_usage.size = getattr(self, 'max_spool_usage')
        self.queue.enqueue(cmd)

    def _set_large_message_threshold(self):
        # Large Message Threshold
        cmd = SolaceXMLBuilder("VPN %s Settings large message threshold event to %s" % (self.vpn_name, self.large_message_threshold))
        cmd.message_vpn.vpn_name = self.vpn_name
        cmd.message_vpn.event.large_message_threshold.size = self.large_message_threshold
        self.queue.enqueue(cmd)

    def _set_logging_tag(self):
        # Logging Tag for this VPN
        cmd = SolaceXMLBuilder("VPN %s Setting logging tag to %s" % (self.vpn_name, self.vpn_name))
        cmd.message_vpn.vpn_name = self.vpn_name
        cmd.message_vpn.event.log_tag.tag_string = self.vpn_name
        self.queue.enqueue(cmd)

    def _enable_vpn(self):
        # Enable the VPN
        cmd = SolaceXMLBuilder("VPN %s Enabling the vpn" % self.vpn_name)
        cmd.message_vpn.vpn_name = self.vpn_name
        cmd.message_vpn.no.shutdown
        self.queue.enqueue(cmd)
