import sys
import logging
import libsolace
from libsolace.plugin import Plugin
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceReply import SolaceReplyHandler
from libsolace.items.SolaceUser import SolaceUser
from libsolace.util import get_key_from_kwargs
from libsolace.Exceptions import *
from libsolace.Decorators import only_on_shutdown


@libsolace.plugin_registry.register
class SolaceUsers(Plugin):
    """ Manage dict of client-users within Solace """

    plugin_name = "SolaceUsers"
    api = "None"

    def __init__(self, **kwargs):
        """ Init user object

        :type users: dict
        :type vpn_name: str
        :type client_profile: str
        :type acl_profile: str
        :type shutdown_on_apply: bool / char b / char u
        :type options: Options
        :type version: str
        :type api: SolaceAPI

        Example:
            >>> connection = SolaceAPI("dev")
            >>> self.users = [connection.manage("SolaceUsers",
                                    users = users_dict,
                                    vpn_name = "dev_testvpn",
                                    client_profile = "glassfish",
                                    acl_profile = "dev_testvpn",
                                    testmode = True,
                                    shutdown_on_apply = False
                                    version = self.version)]
        """

        logging.info("SolaceUsers: kwargs: %s " % kwargs)

        if kwargs == {}:
            logging.info("No kwargs, factory mode")
        else:
            logging.info("kwargs: %s" % kwargs)
            self.api = get_key_from_kwargs('api', kwargs)
            self.commands = SolaceCommandQueue(version=self.api.version)
            self.options = None  # not implemented
            self.users = get_key_from_kwargs("users", kwargs)
            self.vpn_name = get_key_from_kwargs("vpn_name", kwargs)
            self.acl_profile = get_key_from_kwargs("acl_profile", kwargs)

            self.client_profile = get_key_from_kwargs("client_profile", kwargs)
            self.testmode = get_key_from_kwargs("testmode", kwargs)
            self.shutdown_on_apply = get_key_from_kwargs("shutdown_on_apply", kwargs)

            logging.info("""UsersCommands: %s, Environment: %s, Users: %s, vpn_name: %s,
                acl_profile: %s, client_profile: %s, testmode: %s, shutdown_on_apply: %s""" % (self.commands,
                                                                                               self.api.environment,
                                                                                               self.users,
                                                                                               self.vpn_name,
                                                                                               self.acl_profile,
                                                                                               self.client_profile,
                                                                                               self.testmode,
                                                                                               self.shutdown_on_apply))

            if self.testmode:
                logging.info('TESTMODE ACTIVE')
                try:
                    self._tests(**kwargs)
                except Exception, e:
                    logging.error("Tests Failed %s" % e)
                    raise BaseException("Tests Failed")

            # backwards compatibility for None options passed to still execute "add" code
            if self.options == None:
                logging.warning(
                    "No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
                for user in self.users:
                    user_kwargs = dict(kwargs)
                    user_kwargs['username'] = user['username']
                    user_kwargs['password'] = user['password']
                    try:
                        # Check if user already exists, if not then shutdown immediately after creating the user
                        self.get(**user_kwargs).reply.show.client_username.client_usernames.client_username
                    except (AttributeError, KeyError, MissingClientUser):
                        logging.info(
                            "User %s doesn't exist, using shutdown_on_apply to True for user" % user_kwargs['username'])
                        user_kwargs['shutdown_on_apply'] = True
                    self.create_user(**user_kwargs)
                    self.disable_user(**user_kwargs)
                    self.set_client_profile(**user_kwargs)
                    self.set_acl_profile(**user_kwargs)
                    self.no_guarenteed_endpoint(**user_kwargs)
                    self.no_subscription_manager(**user_kwargs)
                    self.set_password(**user_kwargs)
                    self.no_shutdown_user(**user_kwargs)

    #
    # remaining methods are copy pasted from SolaceUser, metaclass conflict when inheriting Plugin and SolaceUser
    #

    def _tests(self, **kwargs):
        """
        Call the tests before create is attempted, checks for profiles in this case
        """
        logging.info('Pre-Provision Tests')
        self.check_client_profile_exists(**kwargs)
        self.check_acl_profile_exists(**kwargs)

    def get(self, **kwargs):
        """ Get a username from solace, return a dict """

        username = get_key_from_kwargs("username", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Getting user %s" % username, version=self.api.version)
        self.api.x.show.client_username.name = username
        self.api.x.show.client_username.vpn_name = vpn_name
        self.api.x.show.client_username.detail

        response = SolaceReplyHandler(self.api.rpc(str(self.api.x)))
        logging.info(response.reply.show.client_username.client_usernames)
        if response.reply.show.client_username.client_usernames == 'None':
            raise MissingClientUser("No such user %s" % username)
        else:
            return response

    def check_client_profile_exists(self, **kwargs):
        """
        Checks if a client_profile exists on the appliance for linking.

        Example:
            >>> foo = SolaceUser(username="joe", environment="dev", client_profile="glassfish")
            >>> foo.check_client_profile_exists()
            >>> from libsolace.SolaceAPI import SolaceAPI
            >>> apic = SolaceAPI("dev")
            >>> foo = SolaceUser(api=apic)
            >>> foo.check_client_profile_exists(client_profile="glassfish")

        """

        client_profile = kwargs.get('client_profile')

        logging.info('Checking if client_profile is present on devices')
        self.api.x = SolaceXMLBuilder("Checking client_profile %s is present on device" % client_profile,
                                      version=self.api.version)
        self.api.x.show.client_profile.name = client_profile
        response = self.api.rpc(str(self.api.x), allowfail=False)
        for v in response:
            if v['rpc-reply']['execute-result']['@code'] == 'fail':
                logging.warning('client_profile: %s missing from appliance' % client_profile)
                raise BaseException("no such client_profile %s" % client_profile)
                return False
        return True

    def check_acl_profile_exists(self, **kwargs):
        acl_profile = kwargs.get('acl_profile')

        logging.info('Checking if acl_profile is present on devices')
        self.api.x = SolaceXMLBuilder("Checking acl_profile %s is present on device" % acl_profile,
                                      version=self.api.version)
        self.api.x.show.acl_profile.name = kwargs.get('acl_profile')
        response = self.api.rpc(str(self.api.x), allowfail=False)
        for v in response:
            if v['rpc-reply']['execute-result']['@code'] == 'fail':
                logging.warning('acl_profile: %s missing from appliance' % acl_profile)
                raise BaseException("no such acl_profile")
                return False
        return True

    def create_user(self, **kwargs):
        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')

        self.api.x = SolaceXMLBuilder("Creating User %s" % username, version=self.api.version)
        self.api.x.create.client_username.username = username
        self.api.x.create.client_username.vpn_name = vpn_name
        self.commands.enqueue(self.api.x)
        return self.api.x;

    @only_on_shutdown('user')
    def disable_user(self, **kwargs):
        """
        Disable the user ( suspending pub/sub )

        """

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')
        shutdown_on_apply = kwargs.get('shutdown_on_apply')

        if (shutdown_on_apply == 'b') or (shutdown_on_apply == 'u') or (shutdown_on_apply == True):
            # Disable / Shutdown User ( else we cant change profiles )
            self.api.x = SolaceXMLBuilder("Disabling User %s" % username, version=self.api.version)
            self.api.x.client_username.username = username
            self.api.x.client_username.vpn_name = vpn_name
            self.api.x.client_username.shutdown
            self.commands.enqueue(self.api.x)
            return self.api.x
        else:
            logging.warning(
                "Not disabling User, commands could fail since shutdown_on_apply = %s" % self.shutdown_on_apply)
            return None

    @only_on_shutdown('user')
    def set_client_profile(self, **kwargs):

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')
        client_profile = kwargs.get('client_profile')

        # Client Profile
        self.api.x = SolaceXMLBuilder("Setting User %s client profile to %s" % (username, client_profile),
                                      version=self.api.version)
        self.api.x.client_username.username = username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.client_profile.name = client_profile
        self.commands.enqueue(self.api.x)
        return self.api.x

    @only_on_shutdown('user')
    def set_acl_profile(self, **kwargs):

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')
        acl_profile = kwargs.get('acl_profile')

        # Set client user profile
        self.api.x = SolaceXMLBuilder("Set User %s ACL Profile to %s" % (username, vpn_name), version=self.api.version)
        self.api.x.client_username.username = username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.acl_profile.name = acl_profile
        self.commands.enqueue(self.api.x)
        return self.api.x

    def no_guarenteed_endpoint(self, **kwargs):

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')

        # No Guarenteed Endpoint
        self.api.x = SolaceXMLBuilder("Default User %s guaranteed endpoint override" % username,
                                      version=self.api.version)
        self.api.x.client_username.username = username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.no.guaranteed_endpoint_permission_override
        self.commands.enqueue(self.api.x)
        return self.api.x

    def no_subscription_manager(self, **kwargs):

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')

        # No Subscription Managemer
        self.api.x = SolaceXMLBuilder("Default User %s subscription manager" % username, version=self.api.version)
        self.api.x.client_username.username = username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.no.subscription_manager
        self.commands.enqueue(self.api.x)
        return self.api.x

    def set_password(self, **kwargs):

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')
        password = kwargs.get('password')

        # Set User Password
        self.api.x = SolaceXMLBuilder("Set User %s password" % username, version=self.api.version)
        self.api.x.client_username.username = username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.password.password = password
        self.commands.enqueue(self.api.x)
        return self.api.x

    def no_shutdown_user(self, **kwargs):

        username = kwargs.get('username')
        vpn_name = kwargs.get('vpn_name')

        # Enable User
        self.api.x = SolaceXMLBuilder("Enable User %s" % username, version=self.api.version)
        self.api.x.client_username.username = username
        self.api.x.client_username.vpn_name = vpn_name
        self.api.x.client_username.no.shutdown
        self.commands.enqueue(self.api.x)
        return self.api.x


if __name__ == "__main__":
    logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',
                        stream=sys.stdout)
    logging.getLogger().setLevel(logging.INFO)
    import doctest

    doctest.testmod()
