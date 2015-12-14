"""

solacehelper is a class to construct solace commands and sets of commands.

"""

import logging
from lxml import etree
import libsolace
from libsolace.util import d2x
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.items.SolaceClientProfile import SolaceClientProfileFactory
from libsolace.items.SolaceACLProfile import SolaceACLProfile
from libsolace.items.SolaceVPN import SolaceVPN
from libsolace.items.SolaceQueue import SolaceQueue

try:
    import simplejson as json
except:
    import json


class SolaceProvision:
    """ Provision the CLIENT_PROFILE, VPN, ACL_PROFILE, QUEUES and USERS """
    def __init__(self, vpn_dict=None, queue_dict=None, environment=None, client_profile="glassfish",
                 users=None, testmode=False, create_queues=True, shutdown_on_apply=False, options=None,
                 version="soltr/6_0", **kwargs):
        """ Init the provisioning

        :type vpn_dict: dictionary
            eg: {'owner': u'SolaceTest', 'spool_size': u'4096', 'password': u'd0nt_u5se_thIs', 'name': u'%s_testvpn'}
        :type queue_dict: list
            eg: [
                  {"exclusive": u"true", "type": "", "name": u"testqueue1", "queue_size": u"4096"},
                  {"exclusive": u"false", "type": "", "name": u"testqueue2", "queue_size": u"4096"}
                ]
        :type environment: str
        :type client_profile: str
        :type users: list
        :type testmode: bool
        :type create_queues: bool
        :type shutdown_on_apply: bool

        :param vpn_dict: vpn dictionary
        :param queue_dict: queue dictionary list
        :param environment: name of environment
        :param client_profile: name of client_profile, default='glassfish'
        :param users: list of user dictionaries to provision
            eg: [{'username': u'%s_marcom3', 'password': u'%s_marcompass'}]
        :param testmode: only test, dont apply changes
        :param create_queues: disable queue creation, default = True
        :param shutdown_on_apply: force shutdown Queue and User for config change, default = False

        """

        self.vpn_dict = vpn_dict
        self.queue_dict = queue_dict
        self.environment_name = environment
        logging.info("environment: %s" % environment)
        self.vpn_name = vpn_dict['name']
        logging.info("vpn_dict: %s" % self.vpn_dict)
        logging.info("vpn_name: %s" % self.vpn_name)
        self.testmode = testmode
        self.create_queues = create_queues
        self.shutdown_on_apply = shutdown_on_apply
        self.queues = None
        self.version = version
        logging.info("Version: %s" % version)

        if self.testmode:
            logging.info('TESTMODE ACTIVE')

        if options == None:
            logging.warning("No options instance passed, running in legacy 'add' mode. This is because the script using")

        # create a connection for RPC calls to the environment
        self.connection = SolaceAPI(self.environment_name, testmode=self.testmode, version=self.version)

        # if the environment has any special vpn_config settings, bring them up
        # self._set_vpn_confg()

        # get version of semp
        if (version==None):
            self.version = self._get_version_from_appliance()
        else:
            logging.warn("Overriding default semp version %s" % version)
            self.version=version

        logging.debug("VPN Data Node: %s" % json.dumps(str(self.vpn_dict), ensure_ascii=False))
        # prepare vpn commands
        self.vpn = self.connection.manage("SolaceVPN", environment=self.environment_name,
                                vpn_name=self.vpn_name,
                                max_spool_usage=self.vpn_dict['vpn_config']['spool_size'])

        logging.info("Create VPN %s" % self.vpn_name)
        for cmd in self.vpn.commands.commands:
            logging.info(str(cmd))
            if not self.testmode:
                self.connection.rpc(str(cmd))

        # self.vpn = SolaceVPN(self.environment_name, self.vpn_name,
        #     max_spool_usage=self.vpn_dict['vpn_config']['spool_size'], version=self.version)

        # prepare the client_profile commands
        self.client_profile = SolaceClientProfileFactory(client_profile, vpn_name=self.vpn_name, version=self.version)

        # prepare acl_profile commands, we create a profile named the same as the VPN for simplicity
        self.acl_profile = SolaceACLProfile(self.environment_name, self.vpn_name, self.vpn_name, version=self.version)

        # prepare the user that owns this vpn
        logging.info("self.vpn_name: %s" % self.vpn_name)

        self.users = [self.connection.manage("SolaceUser",
                                    username = self.vpn_name,
                                    password = self.vpn_dict['password'],
                                    vpn_name = self.vpn_name,
                                    client_profile = self.client_profile.name,
                                    acl_profile = self.acl_profile.name,
                                    testmode = self.testmode,
                                    shutdown_on_apply = self.shutdown_on_apply)]

        # prepare the queues for the vpn ( if any )
        try:
            logging.info("Queue datanodes %s" % self.queue_dict)
            if self.queue_dict:
                try:
                    logging.info("Stacking queue commands for VPN: %s" % self.vpn_name)
                    self.queues = SolaceQueue(self.environment_name, self.vpn, self.queue_dict,
                        shutdown_on_apply=self.shutdown_on_apply, version=self.version)
                except Exception, e:
                    raise
                    # raise BaseException("Something bad has happened which was unforseen by developers: %s" % e)
            else:
                logginf.warning("No Queue dictionary was passed, disabling queue creation")
                self.create_queues = False
        except AttributeError:
            logging.warning("No queue declaration for this vpn in site-config, skipping")
            self.create_queues = False
            pass

        # create the client users
        for user in users:
            logging.info("Provision user: %s for vpn %s" % (user, self.vpn_name))
            self.users.append(self.connection.manage("SolaceUser",
                                         username = user['username'],
                                         password = user['password'],
                                         vpn_name = self.vpn_name,
                                         client_profile = self.client_profile.name,
                                         acl_profile = self.acl_profile.name,
                                         testmode=self.testmode,
                                         shutdown_on_apply = self.shutdown_on_apply))


        logging.info("Create Client Profile")
        # Provision profile now already since we need to link to it.
        for cmd in self.client_profile.queue.commands:
            logging.info(str(cmd))
            if not self.testmode:
                self.connection.rpc(str(cmd))

        logging.info("Create ACL Profile for vpn %s" % self.vpn_name)
        for cmd in self.acl_profile.queue.commands:
            logging.info(str(cmd))
            if not self.testmode:
                self.connection.rpc(str(cmd))

        for user in self.users:
            logging.info("Create user: %s for vpn %s" % (user.username, self.vpn_name))
            for cmd in user.commands.commands:
                logging.info(str(cmd))
                if not self.testmode:
                    self.connection.rpc(str(cmd))

        logging.info("Create Queues Bool?: %s in %s" % (self.create_queues, self.vpn_name))
        if self.create_queues:
            logging.info("Create Queues for vpn %s" % self.vpn_name)
            for cmd in self.queues.queue.commands:
                logging.info(cmd)
                if not self.testmode:
                    self.connection.rpc(str(cmd))

    def _get_version_from_appliance(self):
        self.xmlbuilder = SolaceXMLBuilder()
        self.xmlbuilder.show.version
        result = self.connection.rpc(str(self.xmlbuilder))
        return result[0]['rpc-reply']['@semp-version']

    def _set_vpn_confg(self):
        try:
            # Check if there is environment overide for VPN
            for e in self.vpn_dict.env:
                if e.name == self.environment_name:
                    logging.info('setting vpn_config to %s values' % e.name )
                    self.vpn_dict.vpn_config = e.vpn_config
                    logging.info("Spool Size: %s" % self.vpn_dict.vpn_config['spool_size'])
        except:
            logging.warning("No environment overides for vpn: %s" % self.vpn_dict.name)
            pass
