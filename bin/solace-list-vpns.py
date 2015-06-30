#!/usr/bin/env python

"""

Deletes messages from the spool within queue list

"""

import logging
import libsolace.settingsloader as settings
from libsolace.solace import SolaceAPI
from libsolace.solacehelper import SolaceXMLBuilder, SolaceCommandQueue
from optparse import OptionParser
import sys
import pprint


if __name__ == '__main__':
    """ parse opts, read site.xml, start provisioning vpns. """

    usage = "list all vpns in an environment"
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--env", "--environment", action="store", type="string", dest="env",
                      help="environment to run job in eg:[ dev | ci1 | si1 | qa1 | pt1 | prod ]")

    (options, args) = parser.parse_args()

    if not options.env:
        parser.print_help()
        sys.exit()

    # forces read-only
    options.testmode = True
    settings.env = options.env.lower()

    logging.info("Connecting to appliance in %s, testmode:%s" % (settings.env, options.testmode))
    connection = SolaceAPI(settings.env, testmode=options.testmode)
    for vpn in connection.list_vpns('*'):
        print vpn
