#!/usr/bin/env python

"""

Show solace clients and counts

"""

import sys
import logging

from libsolace.SolaceReply import SolaceReplyHandler

logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',
                    stream=sys.stdout)
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from optparse import OptionParser
import simplejson as json
import sys
import ast

if __name__ == '__main__':
    """ parse opts, read site.xml, start provisioning vpns. """

    usage = "list all vpns in an environment"
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--env", "--environment", action="store", type="string", dest="env",
                      help="environment to run job in eg:[ dev | ci1 | si1 | qa1 | pt1 | prod ]")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="toggles solace debug mode")

    (options, args) = parser.parse_args()

    if not options.env:
        parser.print_help()
        sys.exit()
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # forces read-only
    options.testmode = True
    settings.env = options.env.lower()

    logging.info("Connecting to appliance in %s, testmode:%s" % (settings.env, options.testmode))
    connection = SolaceAPI(settings.env, testmode=options.testmode)
    connection.x = SolaceXMLBuilder("show clients")
    connection.x.show.client_username.name = '*'
    connection.x.show.client_username.detail
    # clients = SolaceReplyHandler(connection.rpc(str(connection.x)))
    clients = connection.rpc(str(connection.x), primaryOnly=True)

    # clients = []

    # class Client:
    #
    #     # def __init__(self, profile, aclProfile, maxEndpoints, clientUsername, enabled, messageVpn, passwordConfigured,
    #     #              numClients, numEndpoints, subscriptionManager, maxConnections, gmeo):
    #     #     self.gmeo = gmeo
    #     #     self.maxConnections = maxConnections
    #     #     self.subscriptionManager = subscriptionManager
    #     #     self.numEndpoints = numEndpoints
    #     #     self.numClients = numClients
    #     #     self.passwordConfigured = passwordConfigured
    #     #     self.messageVpn = messageVpn
    #     #     self.enabled = enabled
    #     #     self.clientUsername = clientUsername
    #     #     self.maxEndpoints = maxEndpoints
    #     #     self.aclProfile = aclProfile
    #     #     self.profile = profile
    #
    #     def __init__(self, js):
    #         j = json.loads(js)

    count = 0
    # logging.info(clients.primary)
    # for c in clients.primary.show.client_username.client_usernames.client_username:
    #
    #     logging.info(ast.literal_eval(c))
    #
    #     # for k, v in dict(c):
    #     #     logging.info("K %s: V: %s" % (k, v))
    #
    #     # logging.info(str(c))
    #     js = str(json.loads(str(c).replace("'", '"').replace('u"', '"').replace('None', '"None"')))
    #     logging.info(js)
    #
    #     lc = Client(js)



    for c in clients[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']:
        logging.info(str(json.loads(str(c).replace("'", '"').replace('u"', '"').replace('None', '"None"'))))
        logging.info(c['num-clients'])
        count = count + int(c['num-clients'])

    logging.info("Total Clients: %s" % count)
