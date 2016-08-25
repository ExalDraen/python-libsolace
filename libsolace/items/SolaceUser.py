import logging
import libsolace
from libsolace.Decorators import only_on_shutdown, before, only_if_not_exists
from libsolace.plugin import Plugin, PluginResponse
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.util import get_key_from_kwargs
from libsolace.Exceptions import *


@libsolace.plugin_registry.register
class SolaceUser(Plugin):
    """Manage a Solace Client User

    This plugin manages Client Users within Solace. Typically you should invoke this plugin via L{SolaceAPI.SolaceAPI}.

    Please see L{plugin.Plugin} for how plugins are instantiated and used.

    """

    plugin_name = "SolaceUser"
    api = "None"
    commands = None

    def __init__(self, **kwargs):
        """ Manage the SolaceUser ( client-username )

        :param client_username: the username of the client
        :type client_username: str
        :param password: the password to set ( plaintext )
        :type password: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :param client_profile: the client profile name to associate with, must exist!
        :type client_profile: str
        :param acl_profile: the acl_profile to associate with, must exist!
        :type acl_profile: str
        :param shutdown_on_apply: is shutdown permitted boolean or char
        :type shutdown_on_apply: bool or char b or char u
        :param options: not implemented yet
        :type options: Options
        :param version: if you want to override the SEMP version for some reason
        :type version: str
        :param api: the instance of the SolaceAPI if not instantiated via SolaceAPI.manage
        :type api: SolaceAPI
        :rtype: list
        :returns: list of requests that can be performed in a for loop.

        Example:

        >>> connection = SolaceAPI("dev")
        >>> self.users = [connection.manage("SolaceUser",
                                client_username = "%s_testuser",
                                password = "mypassword",
                                vpn_name = "%s_testvpn",
                                client_profile = "glassfish",
                                acl_profile = "%s_testvpn",
                                testmode = True,
                                shutdown_on_apply = False
                                version = self.version)]
        """

        logging.info("SolaceUser: kwargs: %s " % kwargs)

        # get the API and pop off the kwargs
        self.api = get_key_from_kwargs('api', kwargs)
        kwargs.pop('api')
        self.commands = SolaceCommandQueue(version=self.api.version)

        # settings section
        self.SOLACE_QUEUE_PLUGIN = get_key_from_kwargs("SOLACE_QUEUE_PLUGIN", self.api.settings.__dict__)

        if kwargs == {}:
            logging.debug("Query Mode")
            return

        self.options = None
        self.client_username = get_key_from_kwargs("client_username", kwargs)
        self.password = get_key_from_kwargs("password", kwargs)

        self.vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        self.acl_profile = get_key_from_kwargs("acl_profile", kwargs)

        self.client_profile = get_key_from_kwargs("client_profile", kwargs)
        self.testmode = get_key_from_kwargs("testmode", kwargs, default=False)
        self.shutdown_on_apply = get_key_from_kwargs("shutdown_on_apply", kwargs)

        logging.info("""UserCommands: %s, Environment: %s, Username: %s, Password: %s, vpn_name: %s,
            acl_profile: %s, client_profile: %s, testmode: %s, shutdown_on_apply: %s""" % (self.commands,
                                                                                           self.api.environment,
                                                                                           self.client_username,
                                                                                           self.password,
                                                                                           self.vpn_name,
                                                                                           self.acl_profile,
                                                                                           self.client_profile,
                                                                                           self.testmode,
                                                                                           self.shutdown_on_apply))

        if self.testmode:
            logging.info('TESTMODE ACTIVE')
            try:
                self.requirements(**kwargs)
            except Exception, e:
                logging.error("Tests Failed %s" % e)
                raise BaseException("Tests Failed")

        # backwards compatibility for None options passed to still execute "add" code
        if self.options is None:
            logging.warning(
                    "No options passed, assuming you meant 'add', please update usage of this class to pass a "
                    "OptionParser instance")
            try:
                # Check if user already exists, if not then shutdown immediately after creating the user
                self.get(**kwargs)[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']
            except (AttributeError, KeyError, MissingClientUser):
                logging.info("User %s doesn't exist, using shutdown_on_apply to True for user" % self.client_username)
                kwargs['shutdown_on_apply'] = True

            self.create_user(**kwargs)
            self.shutdown(**kwargs)
            self.set_client_profile(**kwargs)
            self.set_acl_profile(**kwargs)
            self.no_guarenteed_endpoint(**kwargs)
            self.no_subscription_manager(**kwargs)
            self.set_password(**kwargs)
            self.no_shutdown(**kwargs)

    def requirements(self, **kwargs):
        """ Call the tests before create is attempted, checks for profiles in this case

        :rtype: None
        :returns: nothing

        """
        logging.info('Pre-Provision Tests')
        self.check_client_profile_exists(**kwargs)
        self.check_acl_profile_exists(**kwargs)

    def get(self, **kwargs):
        """ Get a username from the appliance, return a dict

        Example

        >>> connection = SolaceAPI("dev")
        >>> reply = connection.manage("SolaceUser").get(client_username="default", vpn_name="default")
        >>> reply[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']['client-username']
        u'default'

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :rtype: list
        :returns: the user as a dict from the appliance

        """

        client_username = get_key_from_kwargs("client_username", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        logging.info("Getting user: %s vpn: %s" % (client_username, vpn_name))

        self.api.x = SolaceXMLBuilder("Getting user %s" % client_username, version=self.api.version)
        self.api.x.show.client_username.name = client_username
        self.api.x.show.client_username.vpn_name = vpn_name
        self.api.x.show.client_username.detail

        # enqueue to validate
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        self.commands.commands.pop()

        # do the request now
        response = self.api.rpc(PluginResponse(str(self.api.x), **kwargs))
        logging.debug("SRH: %s" % response[0])

        if response[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames'] == 'None':
            raise MissingClientUser("Primary: No such user %s" % client_username)
        elif response[1] is not None and response[1]['rpc-reply']['rpc']['show']['client-username']['client-usernames'] == 'None':
            raise MissingClientUser("Backup: No such user %s" % client_username)
        else:
            return response

    #only_on_shutdown('user')
    @before("shutdown")
    def delete(self, **kwargs):
        """
        Delete a client user

        Example

        >>> connection = SolaceAPI("dev")
        >>> connection.manage("SolaceUser").delete(client_username="foo", vpn_name="bar", force=True, skip_before=True).xml
        '<rpc semp-version="soltr/7_1_1"><no><client-username><username>foo</username><vpn-name>bar</vpn-name></client-username></no></rpc>'

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :rtype: plugin.PluginResponse
        :returns: SEMP request

        """
        client_username = get_key_from_kwargs("client_username", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Delete User %s" % client_username, version=self.api.version)
        self.api.x.no.client_username.username = client_username
        self.api.x.no.client_username.vpn_name = vpn_name
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def check_client_profile_exists(self, **kwargs):
        """
        Checks if a client_profile exists on the appliance.

        Example:

        >>> api = SolaceAPI("dev")
        >>> client = api.manage("SolaceUser")
        >>> client.check_client_profile_exists(client_profile="default")
        True

        :param client_profile: the client profile to check
        :type client_profile: str
        :rtype: bool
        :returns: true or false

        """

        client_profile = get_key_from_kwargs("client_profile", kwargs)

        logging.info('Checking if client_profile is present on devices')
        self.api.x = SolaceXMLBuilder("Checking client_profile %s is present on device" % client_profile,
                                      version=self.api.version)
        self.api.x.show.client_profile.name = client_profile
        response = self.api.rpc(str(self.api.x), allowfail=False)
        for v in response:
            if v['rpc-reply']['rpc']['show']['client-profile'] == None:
                logging.warning('client_profile: %s missing from appliance' % client_profile)
                return False
        return True

    def check_acl_profile_exists(self, **kwargs):
        """
        Checks if a acl_profiles exists on the appliance.

        Example:

        >>> api = SolaceAPI("dev")
        >>> client = api.manage("SolaceUser")
        >>> client.check_acl_profile_exists(acl_profile="myacl")
        False

        :param acl_profile: the client profile to check
        :type acl_profile: str
        :rtype: bool
        :returns: true or false
        """
        acl_profile = get_key_from_kwargs('acl_profile', kwargs)

        logging.info('Checking if acl_profile is present on devices')
        self.api.x = SolaceXMLBuilder("Checking acl_profile %s is present on device" % acl_profile,
                                      version=self.api.version)
        self.api.x.show.acl_profile.name = acl_profile
        response = self.api.rpc(str(self.api.x), allowfail=False)
        # logging.info(response)
        for v in response:
            if v['rpc-reply']['rpc']['show']['acl-profile']['acl-profiles'] == None:
                logging.warning('acl_profile: %s missing from appliance' % acl_profile)
                return False
        return True

    @only_if_not_exists('get', 'rpc-reply.rpc.show.client-username.client-usernames.client-username')
    def create_user(self, **kwargs):
        """
        Create client-user

        Example

        >>> api = SolaceAPI("dev")
        >>> xml = api.manage("SolaceUser").create_user(client_username="foo", vpn_name="bar", force=True)
        >>> xml.xml
        '<rpc semp-version="soltr/7_1_1"><create><client-username><username>foo</username><vpn-name>bar</vpn-name></client-username></create></rpc>'

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name:str
        :rtype: plugin.PluginResponse
        :returns: SEMP request

        """
        client_username = get_key_from_kwargs('client_username', kwargs)
        vpn_name = get_key_from_kwargs('vpn_name', kwargs)

        self.api.x = SolaceXMLBuilder("New User %s" % client_username, version=self.api.version)
        self.api.x.create.client_username.username = client_username
        self.api.x.create.client_username.vpn_name = vpn_name
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def shutdown(self, **kwargs):
        """
        Shutdown the user, this method will be called by anything decorated with the @shutdown decorator.
        The kwarg shutdown_on_apply needs to be either True or 'u' or 'b' for this method to fire.

        Example

        >>> connection.manage("SolaceUser").shutdown(client_username="foo", vpn_name="bar", shutdown_on_apply=True).xml
        '<rpc semp-version="soltr/7_1_1"><client-username><username>foo</username><vpn-name>bar</vpn-name><shutdown/></client-username></rpc>'

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :param shutdown_on_apply: bool / char
        :type shutdown_on_apply: bool / char
        :rtype: plugin.PluginResponse
        :returns: SEMP request

        """

        client_username = get_key_from_kwargs('client_username', kwargs)
        vpn_name = get_key_from_kwargs('vpn_name', kwargs)
        shutdown_on_apply = get_key_from_kwargs('shutdown_on_apply', kwargs)

        # b = both, u = user, True = forced
        if (shutdown_on_apply == 'b') or (shutdown_on_apply == 'u') or (shutdown_on_apply == True):
            self.api.x = SolaceXMLBuilder("Disabling User %s" % client_username, version=self.api.version)
            self.api.x.client_username.username = client_username
            self.api.x.client_username.vpn_name = vpn_name
            self.api.x.client_username.shutdown
            self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
            return PluginResponse(str(self.api.x), **kwargs)
        else:
            logging.warning(
                    "Not disabling User, commands could fail since shutdown_on_apply = %s" % shutdown_on_apply)
            return None

    #only_on_shutdown('user')
    def set_client_profile(self, **kwargs):
        """
        Set the ClientProfile

        Example

        >>> connection = SolaceAPI("dev")
        >>> requests = []
        >>> requests.append(connection.manage("SolaceUser").shutdown(client_username="default", vpn_name="default", shutdown_on_apply=True))
        >>> requests.append(connection.manage("SolaceUser").set_client_profile(client_username="default", vpn_name="default", client_profile="default"))
        >>> requests.append(connection.manage("SolaceUser").no_shutdown(client_username="default", vpn_name="default", shutdown_on_apply=True))
        >>> # [api.rpc(r) for r in requests]

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :param client_profile: the client profile to check
        :type client_profile: str
        :param shutdown_on_apply: bool / char
        :type shutdown_on_apply: bool / char
        :rtype: plugin.PluginResponse
        :returns: SEMP request

        """
        client_username = get_key_from_kwargs('client_username', kwargs)
        vpn_name = get_key_from_kwargs('vpn_name', kwargs)
        client_profile = get_key_from_kwargs('client_profile', kwargs)

        # Client Profile
        self.api.x = SolaceXMLBuilder("Setting User %s client profile to %s" % (client_username, client_profile),
                                      version=self.api.version)
        self.api.x.client_username.username = client_username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.client_profile.name = client_profile
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    #only_on_shutdown('user')
    def set_acl_profile(self, **kwargs):

        """
        Set the acl profile

        >>> connection = SolaceAPI("dev")
        >>> requests = []
        >>> requests.append(connection.manage("SolaceUser").shutdown(client_username="default", vpn_name="default", shutdown_on_apply=True))
        >>> requests.append(connection.manage("SolaceUser").set_acl_profile(client_username="default", vpn_name="default", acl_profile="default"))
        >>> requests.append(connection.manage("SolaceUser").no_shutdown(client_username="default", vpn_name="default", shutdown_on_apply=True))
        >>> # [api.rpc(r) for r in requests]

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :param client_profile: the client profile to check
        :type client_profile: str
        :param shutdown_on_apply: bool / char
        :type shutdown_on_apply: bool / char
        :rtype: plugin.PluginResponse
        :returns: SEMP request
        """

        client_username = get_key_from_kwargs('client_username', kwargs)
        vpn_name = get_key_from_kwargs('vpn_name', kwargs)
        acl_profile = get_key_from_kwargs('acl_profile', kwargs)

        # Set client user profile
        self.api.x = SolaceXMLBuilder("Set User %s ACL Profile to %s" % (client_username, vpn_name),
                                      version=self.api.version)
        self.api.x.client_username.username = client_username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.acl_profile.name = acl_profile
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def no_guarenteed_endpoint(self, **kwargs):
        """
        No guaranteed endpoint permission override

        Example:

        >>> api = SolaceAPI("dev", version="soltr/7_1_1")
        >>> request = api.manage("SolaceUser").no_guarenteed_endpoint(client_username="foo", vpn_name="bar")
        >>> request.xml
        '<rpc semp-version="soltr/7_1_1"><client-username><username>foo</username><vpn-name>bar</vpn-name><no><guaranteed-endpoint-permission-override/></no></client-username></rpc>'

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :rtype: plugin.PluginResponse
        :returns: SEMP request
        """

        client_username = get_key_from_kwargs('client_username', kwargs)
        vpn_name = get_key_from_kwargs('vpn_name', kwargs)

        # No Guarenteed Endpoint
        self.api.x = SolaceXMLBuilder("Default User %s guaranteed endpoint override" % client_username,
                                      version=self.api.version)
        self.api.x.client_username.username = client_username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.no.guaranteed_endpoint_permission_override
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def no_subscription_manager(self, **kwargs):
        """
        No subscription manager

        Example:

        >>> api = SolaceAPI("dev", version="soltr/7_1_1")
        >>> request = api.manage("SolaceUser").no_subscription_manager(client_username="foo", vpn_name="bar")
        >>> request.xml
        '<rpc semp-version="soltr/7_1_1"><client-username><username>foo</username><vpn-name>bar</vpn-name><no><subscription-manager/></no></client-username></rpc>'

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :rtype: plugin.PluginResponse
        :returns: SEMP request
        """

        client_username = get_key_from_kwargs('client_username', kwargs)
        vpn_name = get_key_from_kwargs('vpn_name', kwargs)

        # No Subscription Managemer
        self.api.x = SolaceXMLBuilder("Default User %s subscription manager" % client_username,
                                      version=self.api.version)
        self.api.x.client_username.username = client_username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.no.subscription_manager
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def set_password(self, **kwargs):
        """
        Sets the client-user's password

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :param password: the vpn name
        :type password: str
        :rtype: plugin.PluginResponse
        :returns: SEMP request
        """

        client_username = get_key_from_kwargs('client_username', kwargs)
        vpn_name = get_key_from_kwargs('vpn_name', kwargs)
        password = get_key_from_kwargs('password', kwargs)

        # Set User Password
        self.api.x = SolaceXMLBuilder("Set User %s password" % client_username, version=self.api.version)
        self.api.x.client_username.username = client_username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.password.password = password
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    def no_shutdown(self, **kwargs):
        """
        Enable the client-user

        :param client_username: the username
        :type client_username: str
        :param vpn_name: the vpn name
        :type vpn_name: str
        :rtype: plugin.PluginResponse
        :returns: SEMP request
        """
        client_username = kwargs.get('client_username')
        vpn_name = kwargs.get('vpn_name')

        # Enable User
        self.api.x = SolaceXMLBuilder("Enable User %s" % client_username, version=self.api.version)
        self.api.x.client_username.username = client_username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.no.shutdown
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)


