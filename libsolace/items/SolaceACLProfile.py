import logging
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder

class SolaceACLProfile:
    """ Construct the ACLProfile which is specific for the VPN e.g: "si1_domainevent"
    """

    def __init__(self, environment, name, vpn_name, options=None, version="soltr/6_0", **kwargs):
        """
        :type environment: str
        :type name: str
        :type vpn: SolaceVPN

        :param environment: name of environment
        :param name: name of ACL
        :param vpn: instance of vpn to link to

        """
        self.queue = SolaceCommandQueue(version=version)
        self.environment = environment
        self.name = name % environment
        self.vpn_name = vpn_name

        logging.info("Queue: %s, Environment: %s, Name: %s, VPN: %s"
            % (self.queue, self.environment, self.name, self.vpn_name))

        # backwards compatibility for None options passed to still execute "add" code
        if options == None:
            logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            # queue up the commands
            self._new_acl()
            self._allow_publish()
            self._allow_subscribe()
            self._allow_connect()

    def _new_acl(self):
        cmd = SolaceXMLBuilder("Profile %s" % self.name)
        cmd.create.acl_profile.name = self.name
        cmd.create.acl_profile.vpn_name = self.vpn_name
        self.queue.enqueue(cmd)

    def _allow_publish(self):
        cmd = SolaceXMLBuilder("Allow Publish %s" % self.name)
        cmd.acl_profile.name = self.name
        cmd.acl_profile.vpn_name = self.vpn_name
        cmd.acl_profile.publish_topic.default_action.allow
        self.queue.enqueue(cmd)

    def _allow_subscribe(self):
        cmd = SolaceXMLBuilder("VPN %s Allowing ACL Profile to subscribe to VPN" % self.name)
        cmd.acl_profile.name = self.name
        cmd.acl_profile.vpn_name = self.vpn_name
        cmd.acl_profile.subscribe_topic.default_action.allow
        self.queue.enqueue(cmd)

    def _allow_connect(self):
        cmd = SolaceXMLBuilder("VPN %s Allowing ACL Profile to connect to VPN" % self.name)
        cmd.acl_profile.name = self.name
        cmd.acl_profile.vpn_name = self.vpn_name
        cmd.acl_profile.client_connect.default_action.allow
        self.queue.enqueue(cmd)
