#!/usr/bin/env python

"""

Deletes messages from the spool within queue list

"""

import logging
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from optparse import OptionParser
import sys
import pprint

SOLACE_VPN_PLUGIN = "SolaceVPN"


def delete_msgs_request(connection=None, queue=None, vpn_name=None):
    connection.x = SolaceXMLBuilder("Delete messages in Queue: %s of VPN: %s" % (queue.strip(), vpn_name), version=connection.version)
    connection.x.admin.message_spool.vpn_name = vpn_name
    connection.x.admin.message_spool.delete_messages.queue_name = queue.strip()
    return connection.x


def validate_the_plan(connection=None, vpn_name=None, queues=None):
    """
    :param connection: the connection instance
    :param vpn_name: string name of vpn
    :param queues: list of queues to manipulate
    :return: commands
    """

    # commandQueue is used to stack and validate solace commands
    commands = SolaceCommandQueue(version=connection.version)

    try:
        for queue in queues:
            # Delete Messages
            '''

            <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
              <admin>
                <message-spool>
                  <vpn-name>dev_domainevent</vpn-name>
                  <delete-messages>
                    <queue-name>testqueue</queue-name>
                  </delete-messages>
                </message-spool>
              </admin>
            </rpc>

            '''
            cmd = delete_msgs_request(connection=connection, queue=queue, vpn_name=vpn_name)
            commands.enqueue(cmd)

    except Exception, e:
        print("Error %s" % e)
        raise


if __name__ == '__main__':
    """ parse opts, read site.xml, start provisioning vpns. """

    usage = "purge all messages in ALL queues in a VPN: ./solace-delete-messages.py -e dev -V test_dev_keghol -q '*' -r\n\
    purge all messages in queues matching a regex: ./solace-delete-messages.py -e dev -V test_dev_keghol -q '*.something*' -r"
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--env", "--environment", action="store", type="string", dest="env",
                      help="environment to run job in eg:[ dev | ci1 | si1 | qa1 | pt1 | prod ]")
    parser.add_option("-V", "--vpn", action="store", type="string", dest="vpn_name",
                      help="literal name of vpn, eg: pt1_domainevent")
    parser.add_option("-t", "--testmode", action="store_true", dest="testmode",
                      default=False, help="only test configuration and exit")
    parser.add_option("-q", "--queues", action="store", dest="queues",
                      default=[], help="comma separated list of queues")
    parser.add_option("-r", "--queueregex", action="store_true", dest="queue_filter",
                      default=False, help="queue is a search pattern, so search for queues named like 'queue'")

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

    print("Available VPNS are: %s" % connection.manage(SOLACE_VPN_PLUGIN).list_vpns(vpn_name='*'))

    if options.queue_filter:
        print("You have said that the queue mentioned is a filter, searching for queues")
        queues = connection.list_queues(options.vpn_name, queue_filter=options.queues)
    else:
        queues = options.queues.split(',')
    print("The following queues will be manipulated in %s environment! " % settings.env)
    pprint.pprint(queues)

    # validating the plan
    validate_the_plan(connection=connection, vpn_name=options.vpn_name, queues=queues)

    s = raw_input('Do you want to continue? N/y? ')

    if s.lower() == 'y':
        for queue in queues:
            x = delete_msgs_request(connection=connection, vpn_name=options.vpn_name, queue=queue)
            connection.rpc(x, primaryOnly=True)
    else:
        print("chickening out...")
