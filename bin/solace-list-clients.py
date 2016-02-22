#!/usr/bin/env python

"""

Show solace clients and counts

"""

import sys
import logging
logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from optparse import OptionParser
import sys
import pprint


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
    clients = connection.rpc(str(connection.x), primaryOnly=True)

    count = 0
    for c in clients[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']:
        count=count+int(c['num-clients'])

    pprint.pprint(count)
