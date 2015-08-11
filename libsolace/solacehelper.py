"""

solacehelper is a class to construct solace commands and sets of commands.

"""

import os
import logging
from lxml import etree
from libsolace.util import d2x
from libsolace.solace import SolaceAPI
import re

try:
    from collections import OrderedDict
except ImportError, e:
    from ordereddict import OrderedDict


class SolaceNode:
    """ A data node / leaf. Implemented on demand within SolaceXMLBuilder
    """
    def __init__(self):
        self.__dict__ = OrderedDict()

    def __getattr__(self, name):
        name = re.sub("_", "-", name)
        try:
            return self.__dict__[name]
        except:
            self.__dict__[name] = SolaceNode()
            return self.__dict__[name]

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __call__(self, *args, **kwargs):
        return self.__dict__

    def __setattr__(self, name, value):
        name = re.sub("_", "-", name)
        self.__dict__[name] = value


class SolaceXMLBuilder(object):
    """ Builds Solace's SEMP XML Configuration Commands

    Any dot-name-space calling of a instance of SolaceXMLBuilder will create
    nested dictionary named the same. These are converted to XML when the instance
    is represented as str.

    >>> a=SolaceXMLBuilder(version="soltr/6_2")
    >>> a.foo.bar.baz=2
    >>> str(a)
    '<rpc semp-version="soltr/6_2">\n<foo><bar><baz>2</baz></bar></foo></rpc>'

    """

    def __init__(self, description=None, **kwargs):
        self.__dict__ = OrderedDict()
        self.__setattr__ = None
        if description is not None:
            self.description=description
        self.version = kwargs.get("version", "soltr/6_0")
    def __getattr__(self, name):
        name = re.sub("_", "-", name)
        try:
            return self.__dict__[name]
        except:
            self.__dict__[name] = SolaceNode()
            return self.__dict__[name]

    def __repr__(self):
        myxml = d2x(eval(str(self.__dict__)))
        # I had to conjur up my own header cause solace doesnt like </rpc> to have attribs
        complete_xml = str('<rpc semp-version="%s">%s</rpc>' % (self.version, myxml.display(version=self.version)))
        return complete_xml

    def __call__(self, *args, **kwargs):
        return self.__dict__


class SolaceCommandQueue:
    """ Solace Command Queue Class

    A simple queue which validates SEMP XML and then puts the command into a list.
    """

    schema_files = {
        None: os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr.xsd'),
        "soltr/6_0": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr.xsd'),
        "soltr/6_2": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_6_2.xsd'),
        "soltr/7_0": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_7_0.xsd')
    }

    def __init__(self, version="soltr/6_0"):
        """
        Initializes the queue as a list
        """
        schema_file = open(self.schema_files[version])
        schema_root = etree.XML(schema_file.read())
        schema = etree.XMLSchema(schema_root)
        self.parser = etree.XMLParser(schema=schema)
        self.commands = []

    def enqueue(self, command):
        """ Validate and append a command onto the command list.

        :type command: SolaceXMLBuilder
        :param command: SEMP command to validate
        :return: None
        """
        logging.debug("command %s" % str(command))

        try:
            root = etree.fromstring(str(command), self.parser)
            logging.debug('XML Validated')
            self.commands.append(command)
        except:
            logging.error('XML failed to validate')
            raise


def SolaceClientProfile(name, options=None, version="soltr/6_0", vpn_name=None):
    """
    Factory method for creating SolaceClientProfiles
    Returns an instance of different classes depending on the version provided since 6_2 is not the same process as 6_0
    """
    objects = {
        "soltr/6_0": SolaceClientProfile60,
        "soltr/6_2": SolaceClientProfile62,
        "soltr/7_0": SolaceClientProfile62
    }
    return objects[version](name, options=options, version=version, vpn_name=vpn_name)


class SolaceClientProfileParent(object):
    """
    Parent class for creating SolaceClientProfiles
    Sub-class this class and add the implementing class
    to the SolaceClientProfile factory method
    """
    def __init__(self, name, options=None, version="soltr/6_0", vpn_name=None):
        self.queue = SolaceCommandQueue(version=version)
        self.name = name
        self.vpn_name = vpn_name
        self.version = version
        # backwards compatibility for None options passed to still execute "add" code
        if options == None:
            logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            self._new_client_profile()
            self._allow_consume()
            self._allow_send()
            self._allow_endpoint_create()
            self._allow_transacted_sessions()


class SolaceClientProfile60(SolaceClientProfileParent):
    """
    Solace 6.0 SolaceClientProfile implementation
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


class SolaceClientProfile62(SolaceClientProfileParent):
    """
    Solace 6.2 / 7.0 SolaceClientProfile implementation
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


class SolaceACLProfile:
    """ Construct the ACLProfile which is specific for the VPN e.g: "si1_domainevent"
    """

    def __init__(self, environment, name, vpn, options=None, version="soltr/6_0", **kwargs):
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
        self.vpn = vpn

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
        cmd.create.acl_profile.vpn_name = self.vpn.vpn_name
        self.queue.enqueue(cmd)

    def _allow_publish(self):
        cmd = SolaceXMLBuilder("Allow Publish %s" % self.name)
        cmd.acl_profile.name = self.name
        cmd.acl_profile.vpn_name = self.vpn.vpn_name
        cmd.acl_profile.publish_topic.default_action.allow
        self.queue.enqueue(cmd)

    def _allow_subscribe(self):
        cmd = SolaceXMLBuilder("VPN %s Allowing ACL Profile to subscribe to VPN" % self.name)
        cmd.acl_profile.name = self.name
        cmd.acl_profile.vpn_name = self.vpn.vpn_name
        cmd.acl_profile.subscribe_topic.default_action.allow
        self.queue.enqueue(cmd)

    def _allow_connect(self):
        cmd = SolaceXMLBuilder("VPN %s Allowing ACL Profile to connect to VPN" % self.name)
        cmd.acl_profile.name = self.name
        cmd.acl_profile.vpn_name = self.vpn.vpn_name
        cmd.acl_profile.client_connect.default_action.allow
        self.queue.enqueue(cmd)


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


class SolaceVPN:
    """

    Build up all the commands with SolaceXMLBuilder required to build this VPN, then append them to the command queue.

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
        self.queue = SolaceCommandQueue(version=version)
        self.vpn_name = vpn_name % environment
        self.owner_username = self.vpn_name
        self.environment = environment
        self.acl_profile = self.vpn_name

        # set defaults
        for k,v in self.default_settings.items():
            setattr(self, k, v)

        # use kwargs to tune defaults
        for k,v in self.default_settings.items():
            if k in kwargs:
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
        # Set the Spool Size
        cmd = SolaceXMLBuilder("VPN %s Set spool size to %s" % (self.vpn_name, self.max_spool_usage))
        cmd.message_spool.vpn_name = self.vpn_name
        cmd.message_spool.max_spool_usage.size = self.max_spool_usage
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


class SolaceQueue:
    """ Construct Queues """
    def __init__(self, environment, vpn, queues, testmode=False, shutdown_on_apply=False, options=None, version="soltr/6_0"):
        """ Creates queue commands

        :type environment: str
        :type vpn: SolaceVPN
        :type queues: libsolace.gfmisc.DataNode

        :param environment: environment name
        :param vpn: Datanode instance
        :param queues: queues to create:

        """
        self.queue = SolaceCommandQueue(version=version)
        self.environment = environment
        self.vpn = vpn
        self.testmode = testmode
        self.queues = queues
        self.shutdown_on_apply = shutdown_on_apply

        logging.info("Queues: %s" % self.queues)
        # backwards compatibility for None options passed to still execute "add" code
        if options == None:
            logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            self._create_queue()

    def _get_queue_confg(self, queue):
        """ Returns a queue config for the queue and overrides where neccesary

        :type queue: libsolace.gfmisc.DataNode
        :param queue: single queue datanode object

        """
        try:
            for e in queue.env:
                if e.name == self.environment:
                    logging.info('setting queue_config to environment %s values' % e.name )
                    return e.queue_config
        except:
            logging.warn("No environment overides for queue %s" % queue.name)
            pass
        try:
            return queue.queue_config
        except:
            logging.warning("No queue_config for queue: %s found, please check site-config" % queue.name)
            raise

    def _create_queue(self):
        for queue in self.queues:
            logging.info("Preparing to build queue: %s" % queue.name)
            queue_config = self._get_queue_confg(queue)
            # Create some queues now
            cmd = SolaceXMLBuilder("Creating Queue %s" % queue.name)
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.create.queue.name=queue.name
            self.queue.enqueue(cmd)

            if ( self.shutdown_on_apply=='b' ) or ( self.shutdown_on_apply == 'q' ) or ( self.shutdown_on_apply == True):
                # Lets only shutdown the egress of the queue
                cmd = SolaceXMLBuilder("Shutting down egress for queue:%s" % queue.name)
                cmd.message_spool.vpn_name = self.vpn.vpn_name
                cmd.message_spool.queue.name = queue.name
                cmd.message_spool.queue.shutdown.egress
                self.queue.enqueue(cmd)
            else:
                logging.warning("Not disabling Queue, commands could fail since shutdown_on_apply = %s" % self.shutdown_on_apply)

            # Default to NON Exclusive queue
            cmd = SolaceXMLBuilder("Set Queue %s to Non Exclusive " % queue.name )
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue.name
            cmd.message_spool.queue.access_type.non_exclusive
            self.queue.enqueue(cmd)

            if queue_config.exclusive == "true":
                # Non Exclusive queue
                cmd = SolaceXMLBuilder("Set Queue %s to Exclusive " % queue.name )
                cmd.message_spool.vpn_name = self.vpn.vpn_name
                cmd.message_spool.queue.name = queue.name
                cmd.message_spool.queue.access_type.exclusive
                self.queue.enqueue(cmd)

            # Queue Owner
            cmd = SolaceXMLBuilder("Set Queue %s owner to %s" % (queue.name, self.vpn.vpn_name))
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue.name
            cmd.message_spool.queue.owner.owner = self.vpn.owner_username
            self.queue.enqueue(cmd)

            cmd = SolaceXMLBuilder("Settings Queue %s max bind count to %s" % (queue.name, str(1000)))
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue.name
            cmd.message_spool.queue.max_bind_count.value = 1000
            self.queue.enqueue(cmd)

            # Open Access
            cmd = SolaceXMLBuilder("Settings Queue %s Permission to Consume" % queue.name)
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue.name
            cmd.message_spool.queue.permission.all
            cmd.message_spool.queue.permission.consume
            self.queue.enqueue(cmd)

            # Configure Queue Spool Usage
            cmd = SolaceXMLBuilder("Set Queue %s spool size: %s" % (queue.name, queue_config.queue_size))
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue.name
            cmd.message_spool.queue.max_spool_usage.size = queue_config.queue_size
            self.queue.enqueue(cmd)

            if queue_config.retries:
                cmd = SolaceXMLBuilder("Tuning max-redelivery retries for %s to %s" % (queue.name, queue_config.retries))
                cmd.message_spool.vpn_name = self.vpn.vpn_name
                cmd.message_spool.queue.name = queue.name
                cmd.message_spool.queue.max_redelivery.value = queue_config.retries
                self.queue.enqueue(cmd)
            else:
                cmd = SolaceXMLBuilder("Tuning max-redelivery retries for %s to infinite" % queue.name)
                cmd.message_spool.vpn_name = self.vpn.vpn_name
                cmd.message_spool.queue.name = queue.name
                cmd.message_spool.queue.max_redelivery.value = 0
                self.queue.enqueue(cmd)

            # Enable the Queue
            cmd = SolaceXMLBuilder("Enabling Queue %s" % queue.name)
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue.name
            cmd.message_spool.queue.no.shutdown.full
            self.queue.enqueue(cmd)

            # Queue Reject on Drop
            """
            <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
              <message-spool>
                <vpn-name>prod_testvpn</vpn-name>
                <queue>
                  <name>testqueue1</name>
                  <reject-msg-to-sender-on-discard/>
                </queue>
              </message-spool>
            </rpc>
            """
            cmd = SolaceXMLBuilder("Setting Queue to Reject Drops")
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue.name
            cmd.message_spool.queue.reject_msg_to_sender_on_discard
            self.queue.enqueue(cmd)


class SolaceProvisionVPN:
    """ Provision the CLIENT_PROFILE, VPN, ACL_PROFILE, QUEUES and USERS """
    def __init__(self, vpn_datanode=None, environment=None, client_profile="glassfish", users=None, testmode=False,
                 create_queues=True, shutdown_on_apply=False, options=None, **kwargs):
        """ Init the provisioning

        :type vpn_datanode: libsolace.util.xml2obj.DataNode
        :type environment: str
        :type client_profile: str
        :type users: list
        :type testmode: bool
        :type create_queues: bool
        :type shutdown_on_apply: bool

        :param vpn_datanode: instance of libsolace.util.xml2obj.DataNode
        :param environment: name of environment
        :param client_profile: name of client_profile, default='glassfish'
        :param users: list of user dictionaries to provision
            eg: [{'username': u'%s_marcom3', 'password': u'%s_marcompass'}]
        :param testmode: only test, dont apply changes
        :param create_queues: disable queue creation, default = True
        :param shutdown_on_apply: force shutdown Queue and User for config change, default = False

        """

        self.vpn_datanode = vpn_datanode
        self.environment_name = environment
        self.vpn_name = vpn_datanode.name
        self.testmode = testmode
        self.create_queues = create_queues
        self.shutdown_on_apply = shutdown_on_apply
        self.queues = None

        if self.testmode:
            logging.info('TESTMODE ACTIVE')

        if options == None:
            logging.warning("No options instance passed, running in legacy 'add' mode. This is because the script using")

        # create a connection for RPC calls to the environment
        self.connection = SolaceAPI(self.environment_name, testmode=self.testmode)

        # if the environment has any special vpn_config settings, bring them up
        self._set_vpn_confg()

        # get version of semp
        self.version = self._get_version_from_appliance()

        # prepare vpn commands
        self.vpn = SolaceVPN(self.environment_name, self.vpn_name,
            max_spool_usage=self.vpn_datanode.vpn_config.spool_size)

        # prepare the client_profile commands
        self.client_profile = SolaceClientProfile(client_profile, version=self.version, vpn_name=self.vpn.vpn_name)

        # Provision profile now already since we need to link to it.
        for cmd in self.client_profile.queue.commands:
            self.connection.rpc(str(cmd))

        # prepare acl_profile commands
        self.acl_profile = SolaceACLProfile(self.environment_name, self.vpn_name, self.vpn)

        # prepare the user that owns this vpn
        self.users = [SolaceUser(self.environment_name, self.vpn_name , self.vpn_datanode.password, self.vpn,
            client_profile=self.client_profile.name, testmode=self.testmode, shutdown_on_apply=self.shutdown_on_apply)]

        # prepare the queues for the vpn ( if any )
        try:
            logging.info("Queue datanode %s" % self.vpn_datanode.queue)
            if self.vpn_datanode.queue:
                try:
                    logging.info("Stacking queue commands for VPN: %s" % self.vpn_name)
                    self.queues = SolaceQueue(self.environment_name, self.vpn, self.vpn_datanode.queue,
                        shutdown_on_apply=self.shutdown_on_apply)
                except Exception, e:
                    raise BaseException("Something bad has happened which was unforseen by developers: %s" % e)
            else:
                self.create_queues = False
        except AttributeError:
            logging.warning("No queue declaration for this vpn in site-config, skipping")
            self.create_queues = False
            pass

        # create the client users
        for user in users:
            logging.info("Provision user: %s for vpn %s" % (user, self.vpn_name))
            self.users.append(SolaceUser(self.environment_name, user['username'], user['password'], self.vpn,
                client_profile=self.client_profile.name, testmode=self.testmode, shutdown_on_apply=self.shutdown_on_apply))

        logging.info("Create VPN %s" % self.vpn_name)
        for cmd in self.vpn.queue.commands:
            logging.info(str(cmd))
            self.connection.rpc(str(cmd))

        logging.info("Create ACL Profile for vpn %s" % self.vpn_name)
        for cmd in self.acl_profile.queue.commands:
            logging.info(str(cmd))
            self.connection.rpc(str(cmd))

        logging.info("Create User for vpn %s" % self.vpn_name)
        for user in self.users:
            for cmd in user.queue.commands:
                logging.info(str(cmd))
                self.connection.rpc(str(cmd))

        logging.info("create queues: %s" % self.create_queues)
        if self.create_queues:
            logging.info("Create Queues for vpn %s" % self.vpn_name)
            for cmd in self.queues.queue.commands:
                logging.info(cmd)
                self.connection.rpc(str(cmd))

    def _get_version_from_appliance(self):
        self.xmlbuilder = SolaceXMLBuilder()
        self.xmlbuilder.show.version
        result = self.connection.rpc(str(self.xmlbuilder))
        return result[0]['rpc-reply']['@semp-version']

    def _set_vpn_confg(self):
        try:
            # Check if there is environment overide for VPN
            for e in self.vpn_datanode.env:
                if e.name == self.environment_name:
                    logging.info('setting vpn_config to %s values' % e.name )
                    self.vpn_datanode.vpn_config = e.vpn_config
                    logging.info("Spool Side: %s" % self.vpn_datanode.vpn_config.spool_size)
        except:
            logging.warning("No environment overides for vpn: %s" % self.vpn_datanode.name)
            pass
