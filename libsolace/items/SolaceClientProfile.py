import logging
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder


def SolaceClientProfileFactory(name, options=None, version="soltr/6_0", vpn_name=None, **kwargs):
    """
    Factory method for creating SolaceClientProfiles
    Returns an instance of different classes depending on the version provided since 6_2 is not the same process as 6_0
    """
    objects = {
        "soltr/6_0": SolaceClientProfile60,
        "soltr/6_2": SolaceClientProfile62,
        "soltr/7_0": SolaceClientProfile62,
        "soltr/7_1_1": SolaceClientProfile62
    }
    return objects[version](name, options=options, version=version, vpn_name=vpn_name, **kwargs)


class SolaceClientProfileParent(object):
    """
    Parent class for creating SolaceClientProfiles
    Sub-class this class and add the implementing class
    to the SolaceClientProfile factory method
    """
    def __init__(self, name, options=None, max_clients=500, version="soltr/6_0", bridging=False, vpn_name=None, **kwargs):
        self.queue = SolaceCommandQueue(version=version)
        self.name = name
        self.vpn_name = vpn_name
        self.version = version
        self.max_clients = max_clients
        # backwards compatibility for None options passed to still execute "add" code
        if options == None:
            logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            self._new_client_profile()
            self._allow_consume()
            self._allow_send()
            self._allow_endpoint_create()
            self._allow_transacted_sessions()
            if bridging:
                self._bridging()


class SolaceClientProfile60(SolaceClientProfileParent):
    """
    Solace 6.0 SolaceClientProfile implementation, profiles are "global"
    """
    def _new_client_profile(self):
        # Create client_profile
        cmd = SolaceXMLBuilder("Create Client Profile", version=self.version)
        cmd.create.client_profile.name = self.name
        self.queue.enqueue(cmd)

    def _allow_send(self):
        # Allow send
        cmd = SolaceXMLBuilder("Allow profile send", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.message_spool.allow_guaranteed_message_send
        self.queue.enqueue(cmd)

    def _allow_consume(self):
        # allow consume
        cmd = SolaceXMLBuilder("Allow profile consume", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.message_spool.allow_guaranteed_message_receive
        self.queue.enqueue(cmd)

    def _allow_endpoint_create(self):
        # allow consume
        cmd = SolaceXMLBuilder("Allow profile endpoint create", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.message_spool.allow_guaranteed_endpoint_create
        self.queue.enqueue(cmd)

    def _allow_transacted_sessions(self):
        # allow TS
        cmd = SolaceXMLBuilder("Allow profile transacted sessions", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.message_spool.allow_transacted_sessions
        self.queue.enqueue(cmd)

    def _set_max_clients(self):
        cmd = SolaceXMLBuilder("Setting Max Clients", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.max_connections_per_client_username.value = self.max_clients
        self.queue.enqueue(cmd)

    def _bridging(self):
        cmd = SolaceXMLBuilder("Setting Bridging", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.allow_bridge_connections
        self.queue.enqueue(cmd)


class SolaceClientProfile62(SolaceClientProfileParent):
    """
    Solace 6.2+ SolaceClientProfile implementation, profiles are scoped to VPN
    """
    def _new_client_profile(self):
        # Create client_profile
        cmd = SolaceXMLBuilder("Create Client Profile", version=self.version)
        cmd.create.client_profile.name = self.name
        cmd.create.client_profile.vpn_name = self.vpn_name
        self.queue.enqueue(cmd)

    def _allow_send(self):
        # Allow send
        cmd = SolaceXMLBuilder("Allow profile send", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.vpn_name = self.vpn_name
        cmd.client_profile.message_spool.allow_guaranteed_message_send
        self.queue.enqueue(cmd)

    def _allow_consume(self):
        # allow consume
        cmd = SolaceXMLBuilder("Allow profile consume", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.vpn_name = self.vpn_name
        cmd.client_profile.message_spool.allow_guaranteed_message_receive
        self.queue.enqueue(cmd)

    def _allow_endpoint_create(self):
        # allow consume
        cmd = SolaceXMLBuilder("Allow profile endpoint create", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.vpn_name = self.vpn_name
        cmd.client_profile.message_spool.allow_guaranteed_endpoint_create
        self.queue.enqueue(cmd)

    def _allow_transacted_sessions(self):
        # allow TS
        cmd = SolaceXMLBuilder("Allow profile transacted sessions", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.vpn_name = self.vpn_name
        cmd.client_profile.message_spool.allow_transacted_sessions
        self.queue.enqueue(cmd)

    def _set_max_clients(self):
        cmd = SolaceXMLBuilder("Setting Max Clients", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.vpn_name = self.vpn_name
        cmd.client_profile.max_connections_per_client_username.value = self.max_clients
        self.queue.enqueue(cmd)

    def _bridging(self):
        cmd = SolaceXMLBuilder("Setting Bridging", version=self.version)
        cmd.client_profile.name = self.name
        cmd.client_profile.vpn_name = self.vpn_name
        cmd.client_profile.allow_bridge_connections
        self.queue.enqueue(cmd)
