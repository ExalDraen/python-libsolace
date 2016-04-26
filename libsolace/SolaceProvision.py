"""

solacehelper is a class to construct solace commands and sets of commands.

"""

import logging
from libsolace.SolaceAPI import SolaceAPI

try:
    import simplejson as json
except ImportError:
    import json


class SolaceProvision:
    """ Provision the CLIENT_PROFILE, VPN, ACL_PROFILE, QUEUES and USERS

    :type vpn_dict: dictionary
        eg: {'owner': u'SolaceTest', 'spool_size': u'4096', 'password': u'd0nt_u5se_thIs', 'name': u'dev_testvpn'}
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
        eg: [{'username': u'dev_marcom3', 'password': u'dev_marcompass'}]
    :param testmode: only test, dont apply changes
    :param create_queues: disable queue creation, default = True
    :param shutdown_on_apply: force shutdown Queue and User for config change, default = False

    """

    def __init__(self, **kwargs):

        if kwargs == {}:
            return

        try:
            self.vpn_dict = kwargs['vpn_dict']
            self.vpn_name = self.vpn_dict['name']
            self.queue_dict = kwargs['queue_dict']
            self.environment_name = kwargs['environment']
            self.client_profile_name = kwargs['client_profile']
            self.users_dict = kwargs['users_dict']
            logging.debug("USERS_DICT: %s" % self.users_dict )
            self.testmode = kwargs['testmode']
            self.create_queues = kwargs['create_queues']
            self.shutdown_on_apply = kwargs['shutdown_on_apply']
            self.version = kwargs['version']
            self.detect_status = kwargs['detect_status']
        except Exception, e:
            raise KeyError('missing kwarg %s' % e)
        logging.info("vpn_dict: %s" % self.vpn_dict)
        logging.info("vpn_name: %s" % self.vpn_name)
        logging.info("Command line SolOS-TR version override: %s" % self.version)

        self.queueMgr = None

        if self.testmode:
            logging.info('TESTMODE ACTIVE')

        # create a connection for RPC calls to the environment
        self.connection = SolaceAPI(self.environment_name, testmode=self.testmode, version=self.version,
                                    detect_status=self.detect_status)

        # get version of semp TODO FIXME, this should not be needed after Plugin implemented
        if self.version is None:
            self.version = self.connection.version
        else:
            logging.warn("Overriding default semp version %s" % self.version)
            self.version = self.version

        logging.debug("VPN Data Node: %s" % json.dumps(str(self.vpn_dict), ensure_ascii=False))

        # prepare vpn commands
        self.vpn = self.connection.manage("SolaceVPN",
                                          vpn_name=self.vpn_name,
                                          owner_name=self.vpn_name,
                                          max_spool_usage=self.vpn_dict['vpn_config']['spool_size'])

        logging.info("Create VPN %s" % self.vpn_name)
        for cmd in self.vpn.commands.commands:
            logging.debug(str(cmd))
            if not self.testmode:
                self.connection.rpc(str(cmd[0]), **cmd[1])

        # prepare the client_profile commands
        self.client_profile = self.connection.manage("SolaceClientProfile", name=self.client_profile_name,
                                                     vpn_name=self.vpn_name, version=self.version)

        # prepare acl_profile commands, we create a profile named the same as the VPN for simplicity
        # self.acl_profile = SolaceACLProfile(self.environment_name, self.vpn_name, self.vpn_name, version=self.version)
        self.acl_profile = self.connection.manage("SolaceACLProfile", name=self.vpn_name, vpn_name=self.vpn_name)

        # prepare the user that owns this vpn
        logging.info("self.vpn_name: %s" % self.vpn_name)

        if not self._is_vpn_owner_user_present():
            logging.debug("VPN owner user %s for VPN %s not present in CMDB, appending to the list of users to be created" % (self.vpn_name, self.vpn_name))
            vpn_owner_user = [
                {
                    'username': self.vpn_name,
                    'password': self.vpn_dict['password']
                }
            ]

            self.users_dict.extend(vpn_owner_user)

        self.userMgr = self.connection.manage("SolaceUsers",
                                              users=self.users_dict,
                                              vpn_name=self.vpn_name,
                                              client_profile=self.client_profile.name,
                                              acl_profile=self.acl_profile.name,
                                              testmode=self.testmode,
                                              shutdown_on_apply=self.shutdown_on_apply)

        # self.users = [self.connection.manage("SolaceUser",
        #                             username = self.vpn_name,
        #                             password = self.vpn_dict['password'],
        #                             vpn_name = self.vpn_name,
        #                             client_profile = self.client_profile.name,
        #                             acl_profile = self.acl_profile.name,
        #                             testmode = self.testmode,
        #                             shutdown_on_apply = self.shutdown_on_apply)]
        #
        # logging.info("self.users: %s" % self.users)

        # prepare the queues for the vpn ( if any )
        try:
            logging.info("Queue datanodes %s" % self.queue_dict)
            if self.queue_dict is not None:
                try:
                    logging.info("Stacking queue commands for VPN: %s" % self.vpn_name)
                    self.queueMgr = self.connection.manage("SolaceQueue",
                                                           vpn_name=self.vpn_name,
                                                           queues=self.queue_dict,
                                                           shutdown_on_apply=self.shutdown_on_apply)
                except Exception, e:
                    raise
                    # raise BaseException("Something bad has happened which was unforseen by developers: %s" % e)
            else:
                logging.warning("No Queue dictionary was passed, disabling queue creation")
                self.create_queues = False
        except AttributeError:
            logging.warning("No queue declaration for this vpn in site-config, skipping")
            self.create_queues = False
            raise

        logging.info("Create Client Profile")
        # Provision profile now already since we need to link to it.
        for cmd in self.client_profile.commands.commands:
            logging.debug(str(cmd))
            if not self.testmode:
                self.connection.rpc(str(cmd[0]), **cmd[1])

        logging.info("Create ACL Profile for vpn %s" % self.vpn_name)
        for cmd in self.acl_profile.commands.commands:
            logging.debug(str(cmd))
            if not self.testmode:
                self.connection.rpc(str(cmd[0]), **cmd[1])

        logging.info("Creating users for vpn %s" % self.vpn_name)
        for cmd in self.userMgr.commands.commands:
            logging.debug(cmd)
            if not self.testmode:
                self.connection.rpc(str(cmd[0]), **cmd[1])

        logging.info("Create Queues Bool?: %s in %s" % (self.create_queues, self.vpn_name))
        if self.create_queues:
            logging.info("Create Queues for vpn %s" % self.vpn_name)
            for cmd in self.queueMgr.commands.commands:
                logging.debug(cmd)
                if not self.testmode:
                    self.connection.rpc(str(cmd[0]), **cmd[1])

    def __set_vpn_confg__(self):
        try:
            # Check if there is environment overide for VPN
            for e in self.vpn_dict.env:
                if e.name == self.environment_name:
                    logging.info('setting vpn_config to %s values' % e.name)
                    self.vpn_dict.vpn_config = e.vpn_config
                    logging.info("Spool Size: %s" % self.vpn_dict.vpn_config['spool_size'])
        except:
            logging.warning("No environment overides for vpn: %s" % self.vpn_dict.name)
            pass

    def _is_vpn_owner_user_present(self):
        """
        Checks if the special vpn_owner user is already configured in the CMDB
        Returns boolean
        """
        return True in [True for x in self.users_dict if x["username"] == self.vpn_name]
