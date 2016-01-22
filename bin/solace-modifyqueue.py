#!/usr/bin/env python

"""
This script changes the following queues permission to "modify-topic". It does so by disabling egress for the queues,
updating the property and re-enabling the queue!


"""

import logging
logging.basicConfig(level=logging.DEBUG, format='[gitti] %(asctime)s %(levelname)s %(message)s')
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from optparse import OptionParser
import sys
import pprint


queues = ['company.some.queue11']

def generateXML(vpn_name=None, queues=None):
    """
    :param vpn_name: string name of vpn
    :param queues: list of queues to manipulate
    :return: commands
    """
    # commandQueue is used to stack and validate solace commands
    commands = SolaceCommandQueue()

    try:
        for queue in queues:
            # Disable egress
            '''
            <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
              <message-spool>
                <vpn-name>test_dev_keghol</vpn-name>
                <queue>
                  <name>testqueue</name>
                  <shutdown>
                    <egress/>
                  </shutdown>
                </queue>
              </message-spool>
            </rpc>
            '''
            cmd = SolaceXMLBuilder("Shutttingdown egress for queue:%s" % queue)
            cmd.message_spool.vpn_name = vpn_name
            cmd.message_spool.queue.name = queue
            cmd.message_spool.queue.shutdown.egress
            commands.enqueue(cmd)

            # Open Access
            cmd = SolaceXMLBuilder("Settings Queue %s Permission to modify-topic" % queue)
            cmd.message_spool.vpn_name = vpn_name
            cmd.message_spool.queue.name = queue
            cmd.message_spool.queue.permission.all
            cmd.message_spool.queue.permission.modify_topic
            commands.enqueue(cmd)

            # Enable the Queue
            cmd = SolaceXMLBuilder("Enabling Queue %s" % queue)
            cmd.message_spool.vpn_name = vpn_name
            cmd.message_spool.queue.name = queue
            cmd.message_spool.queue.no.shutdown.full
            commands.enqueue(cmd)

    except Exception, e:
        print("Error %s" % e)

    print("Returning the plan")
    return commands

if __name__ == '__main__':
    """ parse opts, read site.xml, start provisioning vpns. """

    usage = ''
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--env", "--environment", action="store", type="string", dest="env",
                      help="environment to run job in eg:[ dev | ci1 | si1 | qa1 | pt1 | prod ]")
    parser.add_option("-V", "--vpn", action="store", type="string", dest="vpn_name",
                      help="literal name of vpn, eg: pt1_domainevent")
    parser.add_option("-t", "--testmode", action="store_true", dest="testmode",
                      default=False, help="only test configuration and exit")

    (options, args) = parser.parse_args()

    if not options.env:
        parser.print_help()
        sys.exit()
    if not options.vpn_name:
        parser.print_help()
        sys.exit()
    if options.testmode:
        logging.info("TEST MODE ACTIVE!!!")

    settings.env = options.env.lower()

    logging.info("Connecting to appliance in %s, testmode:%s" % (settings.env, options.testmode))
    connection = SolaceAPI(settings.env, testmode=options.testmode)
    commands = generateXML(vpn_name=options.vpn_name, queues=queues)

    print("The following queues will be manipulated in %s environment! " % settings.env)
    pprint.pprint(queues)

    s = raw_input('Do you want to continue? N/y? ')

    if s.lower() == 'y':
        for cmd in commands.commands:
            connection.rpc(str(cmd))
    else:
        print("chickening out...")
