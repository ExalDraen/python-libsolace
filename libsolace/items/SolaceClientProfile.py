import logging
import libsolace
from libsolace.plugin import Plugin
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.util import version_equal_or_greater_than

@libsolace.plugin_registry.register
class SolaceClientProfile(Plugin):

    plugin_name = "SolaceClientProfile"

    def __init__(self, *args, **kwargs):

        # if kwargs is not passed, then its a plugin load, return fast
        if kwargs == {}:
            logging.debug("Plugin Mode")
            return

        self.api = kwargs.get("api")
        self.commands = SolaceCommandQueue(version=self.api.version)
        self.name = kwargs.get('name')
        self.vpn_name = kwargs.get('vpn_name')
        self.max_clients = kwargs.get('max_clients')

        if kwargs.get('options', None) is None:
            logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            self.new_client_profile(**kwargs)
            self.allow_consume(**kwargs)
            self.allow_send(**kwargs)
            self.allow_endpoint_create(**kwargs)
            self.allow_transacted_sessions(**kwargs)

    def new_client_profile(self, **kwargs):
        """
        Create a new client profile

        Enqueues the semp request in self.commands and returns the SolaceXMLBuilder
        instance.

        :Parameters:
            - `name` (`string`) - Name of the Client Profile
            - `vpn_name` (`string`) - VPN Name for SolOS 6.2+
        :return: (`SolaceXMLBuilder`) The xml builder
        """
        name = kwargs.get("name")
        vpn_name = kwargs.get("vpn_name")

        self.api.x = SolaceXMLBuilder("Create Client Profile", version=self.api.version)
        self.api.x.create.client_profile.name = name
        logging.info(version_equal_or_greater_than('soltr/6_2', self.api.version))
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.create.client_profile.vpn_name = vpn_name
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_consume(self, **kwargs):
        """
        Allow consume permission

        Enqueues the semp request in self.commands and returns the SolaceXMLBuilder
        instance.

        :Parameters:
            - `name` (`string`) - Name of the Client Profile
            - `vpn_name` (`string`) - VPN Name for SolOS 6.2+
        :return: (`SolaceXMLBuilder`) The xml builder
        """
        name = kwargs.get("name")
        vpn_name = kwargs.get("vpn_name")

        self.api.x = SolaceXMLBuilder("Allow profile consume", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.create.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_guaranteed_message_receive
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_send(self, **kwargs):
        """
        Allow send permission

        Enqueues the semp request in self.commands and returns the SolaceXMLBuilder
        instance.

        :Parameters:
            - `name` (`string`) - Name of the Client Profile
            - `vpn_name` (`string`) - VPN Name for SolOS 6.2+
        """
        name = kwargs.get("name")
        vpn_name = kwargs.get("vpn_name")

        self.api.x = SolaceXMLBuilder("Allow profile send", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.create.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_guaranteed_message_send
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_endpoint_create(self, **kwargs):
        """
        Allow endpoint creation permission

        Enqueues the semp request in self.commands and returns the SolaceXMLBuilder
        instance.

        :Parameters:
            - `name` (`string`) - Name of the Client Profile
            - `vpn_name` (`string`) - VPN Name for SolOS 6.2+
        """
        name = kwargs.get("name")
        vpn_name = kwargs.get("vpn_name")

        self.api.x = SolaceXMLBuilder("Allow profile endpoint create", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.create.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_guaranteed_endpoint_create
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_transacted_sessions(self, **kwargs):
        """
        Allow transaction sessions permission

        Enqueues the semp request in self.commands and returns the SolaceXMLBuilder
        instance.

        :Parameters:
            - `name` (`string`) - Name of the Client Profile
            - `vpn_name` (`string`) - VPN Name for SolOS 6.2+
        """
        name = kwargs.get("name")
        vpn_name = kwargs.get("vpn_name")

        self.api.x = SolaceXMLBuilder("Allow profile transacted sessions", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.create.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_transacted_sessions
        self.commands.enqueue(self.api.x)
        return self.api.x

    def set_max_clients(self, **kwargs):
        """
        Set max clients for profile

        Enqueues the semp request in self.commands and returns the SolaceXMLBuilder
        instance.

        :Parameters:
            - `name` (`string`) - Name of the Client Profile
            - `vpn_name` (`string`) - VPN Name for SolOS 6.2+
            - `max_clients` (`integer`) - Max number of clients
        """
        name = kwargs.get("name")
        vpn_name = kwargs.get("vpn_name")
        max_clients = kwargs.get("max_clients")

        self.api.x = SolaceXMLBuilder("Setting Max Clients", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            cmd.create.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.max_connections_per_client_username.value = max_clients
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_bridging(self, **kwargs):
        """
        Allow bridging

        Enqueues the semp request in self.commands and returns the SolaceXMLBuilder
        instance.

        :Parameters:
            - `name` (`string`) - Name of the Client Profile
            - `vpn_name` (`string`) - VPN Name for SolOS 6.2+
        """
        name = kwargs.get("name")
        vpn_name = kwargs.get("vpn_name")

        self.api.x = SolaceXMLBuilder("Setting Bridging", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.create.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.allow_bridge_connections
        self.commands.enqueue(self.api.x)
        return self.api.x
