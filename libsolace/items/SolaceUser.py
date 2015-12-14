import logging
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceAPI import SolaceAPI

class SolaceUser:
    """ Construct the ClientUser which is normally the application using a VPN. e.g: "si1_marcom" """

    def __init__(self, environment=None, username=None, password=None, vpn_name=None,
                 client_profile=None, acl_profile=None, testmode=False,
                 shutdown_on_apply=False, options=None, version="soltr/6_0", **kwargs):
        """ Init user object

        :type environment: str
        :type username: str
        :type password: str
        :type vpn_name: str
        :type client_profile: str

        :param environment: environment name
        :param username: username including %s placeholder: eg: %s_keghol
        :param password: password
        :param vpn: SolaceVPN instance
        :param client_profile: name of client_profile

        Example:
        users = [SolaceUser(environment = "dev",
                            username = "%s_someproduct",
                            password = "password",
                            vpn_name = "%s_MyVPN",
                            client_profile = "glassfish",
                            testmode=True,
                            shutdown_on_apply = True)]
        """


        if "document" in kwargs:
            logging.info("Reversing a document %s" % kwargs.get("document"))

        else:

            self.version = version
            self.commands = SolaceCommandQueue(version = self.version)
            self.environment = environment
            self.username = username % environment
            self.password = password
            logging.info("vpn_name: %s" % vpn_name)
            self.vpn_name = vpn_name % environment
            self.acl_profile = acl_profile
            self.client_profile = client_profile
            self.testmode = testmode
            self.shutdown_on_apply = shutdown_on_apply

            logging.info("""Commands: %s, Environment: %s, Username: %s, Password: %s, vpn_name: %s,
                acl_profile: %s, client_profile: %s, testmode: %s, shutdown_on_apply: %s""" % (self.commands,
                    self.environment, self.username, self.password, self.vpn_name, self.acl_profile, self.client_profile,
                    self.testmode, self.shutdown_on_apply))

            if self.testmode:
                logging.info('TESTMODE ACTIVE')
                try:
                    self._tests()
                except Exception, e:
                    logging.error("Tests Failed %s" % e)
                    raise BaseException("Tests Failed")

            # backwards compatibility for None options passed to still execute "add" code
            if options == None:
                logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
                self.new_user()
                self.disable_user()
                self.set_client_profile()
                self.set_acl_profile()
                self.no_guarenteed_endpoint()
                self.no_subscription_manager()
                self.set_password()
                self.no_shutdown_user()

    def _tests(self):
        logging.info('Pre-Provision Tests')
        self.check_client_profile_exists()
        self.check_acl_profile_exists()

    def _get_kwarg(self, **kwargs):
        """
        facilitates using default "kwargs" from self variables. returns kwargs
        """
        mykwargs = kwargs
        mykwargs.set('client_profile', kwargs.get('client_profile', self.client_profile))
        mykwargs.set('username', kwargs.get('username', self.username))
        mykwargs.set('vpn_name', kwargs.get('vpn_name', self.vpn_name))
        mykwargs.set('password', kwargs.get('password', self.password))
        mykwargs.set('acl_profile', kwargs.get('acl_profile', self.acl_profile))
        mykwargs.set('shutdown_on_apply', kwargs.get('shutdown_on_apply', self.shutdown_on_apply))
        return kwargs

    def check_client_profile_exists(self, **kwargs):

        kwargs = self._setkwargs(kwargs)

        client_profile = kwargs.get('client_profile')

        logging.info('Checking if client_profile is present on devices')
        cmd = SolaceXMLBuilder("Checking client_profile %s is present on device" % client_profile, version=self.version)
        cmd.show.client_profile.name=client_profile
        mysolace = SolaceAPI(self.environment, version=self.version)
        response = mysolace.rpc(str(cmd), allowfail=False)
        for v in response:
            if v['rpc-reply']['execute-result']['@code'] == 'fail':
                logging.warning('client_profile: %s missing from appliance' % client_profile)
                raise BaseException("no such client_profile")

    def check_acl_profile_exists(self, **kwargs):

        kwargs = self._setkwargs(kwargs)

        acl_profile = kwargs.get('acl_profile')

        logging.info('Checking if acl_profile is present on devices')
        cmd = SolaceXMLBuilder("Checking acl_profile %s is present on device" % acl_profile, version=self.version)
        cmd.show.acl_profile.name=kwargs.get('acl_profile')
        mysolace = SolaceAPI(self.environment, version=self.version)
        response = mysolace.rpc(str(cmd), allowfail=False)
        for v in response:
            if v['rpc-reply']['execute-result']['@code'] == 'fail':
                logging.warning('acl_profile: %s missing from appliance' % acl_profile)
                raise BaseException("no such acl_profile")

    def new_user(self, **kwargs):

        kwargs = self._setkwargs(kwargs)

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')

        cmd = SolaceXMLBuilder("New User %s" % username, version=self.version)
        cmd.create.client_username.username = username
        cmd.create.client_username.vpn_name = vpn_name
        self.commands.enqueue(cmd)
        return cmd;

    def disable_user(self, **kwargs):
        """
        Disable the user ( suspending pub/sub )

        """

        kwargs = self._setkwargs(kwargs)

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')
        shutdown_on_apply = kwargs.get('shutdown_on_apply')

        if ( shutdown_on_apply=='b' ) or ( shutdown_on_apply == 'u' ) or ( shutdown_on_apply == True ):
            # Disable / Shutdown User ( else we cant change profiles )
            cmd = SolaceXMLBuilder("Disabling User %s" % username, version=self.version)
            cmd.client_username.username = username
            cmd.client_username.vpn_name = vpn_name
            cmd.client_username.shutdown
            self.commands.enqueue(cmd)
            return cmd
        else:
            logging.warning("Not disabling User, commands could fail since shutdown_on_apply = %s" % self.shutdown_on_apply)
            return None

    def set_client_profile(self, **kwargs):

        kwargs = self._setkwargs(kwargs)

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')
        client_profile = kwargs.get('client_profile')

        # Client Profile
        cmd = SolaceXMLBuilder("Setting User %s client profile to %s" % (username, client_profile), version=self.version)
        cmd.client_username.username = username
        cmd.client_username.vpn_name = vpn_name
        cmd.client_username.client_profile.name = client_profile
        self.commands.enqueue(cmd)
        return cmd

    def set_acl_profile(self, **kwargs):
        kwargs = self._setkwargs(kwargs)

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')
        acl_profile = kwargs.get('acl_profile')

        # Set client user profile
        cmd = SolaceXMLBuilder("Set User %s ACL Profile to %s" % (username, vpn_name), version=self.version)
        cmd.client_username.username = username
        cmd.client_username.vpn_name = vpn_name
        cmd.client_username.acl_profile.name = acl_profile
        self.commands.enqueue(cmd)
        return cmd

    def no_guarenteed_endpoint(self, **kwargs):

        kwargs = self._setkwargs(kwargs)

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')

        # No Guarenteed Endpoint
        cmd = SolaceXMLBuilder("Default User %s guaranteed endpoint override" % username, version=self.version)
        cmd.client_username.username = username
        cmd.client_username.vpn_name = vpn_name
        cmd.client_username.no.guaranteed_endpoint_permission_override
        self.commands.enqueue(cmd)
        return cmd

    def no_subscription_manager(self, **kwargs):
        kwargs = self._setkwargs(kwargs)

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')

        # No Subscription Managemer
        cmd = SolaceXMLBuilder("Default User %s subscription manager" % username, version=self.version)
        cmd.client_username.username = username
        cmd.client_username.vpn_name = vpn_name
        cmd.client_username.no.subscription_manager
        self.commands.enqueue(cmd)
        return cmd

    def set_password(self, **kwargs):

        kwargs = self._setkwargs(kwargs)

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')
        password = kwargs.get('password')

        # Set User Password
        cmd = SolaceXMLBuilder("Set User %s password" % username, version=self.version)
        cmd.client_username.username = username
        cmd.client_username.vpn_name = vpn_name
        cmd.client_username.password.password = password
        self.commands.enqueue(cmd)
        return cmd

    def no_shutdown_user(self, **kwargs):
        kwargs = self._setkwargs(kwargs)

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')

        # Enable User
        cmd = SolaceXMLBuilder("Enable User %s" % username, version=self.version)
        cmd.client_username.username = username
        cmd.client_username.vpn_name = vpn_name
        cmd.client_username.no.shutdown
        self.commands.enqueue(cmd)
        return cmd

if __name__ == "__main__":
    import doctest
    import logging
    import sys
    logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
    logging.getLogger().setLevel(logging.INFO)
    doctest.testmod()
