import logging
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder

class SolaceUser:
    """ Construct the ClientUser which is normally the application using a VPN. e.g: "si1_marcom" """

    def __init__(self, environment, username, password, vpn, client_profile=None, testmode=False,
                 shutdown_on_apply=False, options=None, version="soltr/6_0", **kwargs):
        """ Init user object

        :type environment: str
        :type username: str
        :type password: str
        :type vpn: SolaceVPN
        :type client_profile: str

        :param environment: environment name
        :param username: username including %s placeholder: eg: %s_keghol
        :param password: password
        :param vpn: SolaceVPN instance
        :param client_profile: name of client_profile

        Example:
        users = [SolaceUser(self.environment_name, self.vpn_name , self.vpn_datanode.password, self.vpn,
            client_profile=self.client_profile.name, testmode=self.testmode, shutdown_on_apply=self.shutdown_on_apply)]

        """
        self.queue = SolaceCommandQueue(version=version)
        self.environment = environment
        self.username = username % environment
        self.password = password
        self.vpn = vpn
        self.acl_profile = self.vpn.acl_profile
        self.client_profile = client_profile
        self.testmode = testmode
        self.shutdown_on_apply = shutdown_on_apply

        if self.testmode:
            logging.info('TESTMODE ACTIVE')
            try:
                self._tests()
            except Exception, e:
                logging.error("Tests Failed")
                raise BaseException("Tests Failed")

        # backwards compatibility for None options passed to still execute "add" code
        if options == None:
            logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            self._new_user()
            self._disable_user()
            self._set_client_profile()
            self._set_acl_profile()
            self._guarenteed_endpoint()
            self._subscription_manager()
            self._password()
            self._enable_user()

    def _tests(self):
        logging.info('Pre-Provision Tests')
        self._check_client_profile()

    def _check_client_profile(self):
        logging.info('Checking if client_profile is present on devices')
        cmd = SolaceXMLBuilder("Checking client_profile %s is present on device" % self.client_profile)
        cmd.show.client_profile.name=self.client_profile
        mysolace = SolaceAPI(self.environment)
        response = mysolace.rpc(str(cmd), allowfail=False)
        for v in response:
            if v['rpc-reply']['execute-result']['@code'] == 'fail':
                logging.warning('client_profile: %s missing from appliance' % self.client_profile)
                raise BaseException("no such client_profile")

    def _new_user(self):
        cmd = SolaceXMLBuilder("New User %s" % self.username)
        cmd.create.client_username.username = self.username
        cmd.create.client_username.vpn_name = self.vpn.vpn_name
        self.queue.enqueue(cmd)

    def _disable_user(self):
        if ( self.shutdown_on_apply=='b' ) or ( self.shutdown_on_apply == 'u' ) or ( self.shutdown_on_apply == True ):
            # Disable / Shutdown User ( else we cant change profiles )
            cmd = SolaceXMLBuilder("Disabling User %s" % self.username)
            cmd.client_username.username = self.username
            cmd.client_username.vpn_name = self.vpn.vpn_name
            cmd.client_username.shutdown
            self.queue.enqueue(cmd)
        else:
            logging.warning("Not disabling User, commands could fail since shutdown_on_apply = %s" % self.shutdown_on_apply)

    def _set_client_profile(self):
        # Client Profile
        cmd = SolaceXMLBuilder("Setting User %s client profile to %s" % (self.username, self.client_profile))
        cmd.client_username.username = self.username
        cmd.client_username.vpn_name = self.vpn.vpn_name
        cmd.client_username.client_profile.name = self.client_profile
        self.queue.enqueue(cmd)

    def _set_acl_profile(self):
        # Set client user profile
        cmd = SolaceXMLBuilder("Set User %s ACL Profile to %s" % (self.username, self.vpn.vpn_name))
        cmd.client_username.username = self.username
        cmd.client_username.vpn_name = self.vpn.vpn_name
        cmd.client_username.acl_profile.name = self.vpn.vpn_name
        self.queue.enqueue(cmd)

    def _guarenteed_endpoint(self):
        # No Guarenteed Endpoint
        cmd = SolaceXMLBuilder("Default User %s guaranteed endpoint override" % self.username)
        cmd.client_username.username = self.username
        cmd.client_username.vpn_name = self.vpn.vpn_name
        cmd.client_username.no.guaranteed_endpoint_permission_override
        self.queue.enqueue(cmd)

    def _subscription_manager(self):
        # No Subscription Managemer
        cmd = SolaceXMLBuilder("Default User %s subscription manager" % self.username)
        cmd.client_username.username = self.username
        cmd.client_username.vpn_name = self.vpn.vpn_name
        cmd.client_username.no.subscription_manager
        self.queue.enqueue(cmd)

    def _password(self):
        # Set User Password
        cmd = SolaceXMLBuilder("Set User %s password" % self.username)
        cmd.client_username.username = self.username
        cmd.client_username.vpn_name = self.vpn.vpn_name
        cmd.client_username.password.password = self.password
        self.queue.enqueue(cmd)

    def _enable_user(self):
        # Enable User
        cmd = SolaceXMLBuilder("Enable User %s" % self.username)
        cmd.client_username.username = self.username
        cmd.client_username.vpn_name = self.vpn.vpn_name
        cmd.client_username.no.shutdown
        self.queue.enqueue(cmd)
