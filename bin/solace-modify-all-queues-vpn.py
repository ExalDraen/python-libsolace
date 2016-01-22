#!/usr/bin/env python

"""

This script changes all the queues within a VPN affecting the reject-msg-to-sender-on-discard setting.

"""

import sys
sys.path.append("/opt/pipeline")
import logging
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from optparse import OptionParser
import pprint
settings.debugmode = False

queues = []

def generateXMLForManagingRejectMsgToSenderOnDiscard(vpn_name=None, queues=None, reject_msg_to_sender_on_discard=False):
    """
    :param vpn_name: string name of vpn
    :param queues: list of queues to manipulate
    :return: commands
    """
    # commandQueue is used to stack and validate solace commands
    commands = SolaceCommandQueue()

    try:
        for queue in queues:
            # Disable reject-msg-to-sender-on-discard
            '''
            <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
              <message-spool>
                <vpn-name>dev_domainevent</vpn-name>
                <queue>
                  <name>unibet.TestStatusChangedEvents.customertest</name>
                  <no>
                    <reject-msg-to-sender-on-discard/>
                  </no>
                </queue>
              </message-spool>
            </rpc>
            '''
            if reject_msg_to_sender_on_discard:
                prefix = "Enabling"
            else:
                prefix = "Disabling"
            cmd = SolaceXMLBuilder("%s reject-msg-to-sender-on-discard for queue: %s" % (prefix,queue))
            cmd.message_spool.vpn_name = vpn_name
            cmd.message_spool.queue.name = queue
            if reject_msg_to_sender_on_discard:
                cmd.message_spool.queue.reject_msg_to_sender_on_discard
            else:
                cmd.message_spool.queue.no.reject_msg_to_sender_on_discard
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
    parser.add_option("-r", "--reject_msg_to_sender_on_discard", action="store_true", dest="reject_msg_to_sender_on_discard",
                      default=False, help="set to enable reject-msg-to-sender-on-discard")
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
    queues = connection.list_queues(options.vpn_name)
    commands = generateXMLForManagingRejectMsgToSenderOnDiscard(vpn_name=options.vpn_name, queues=queues,
                                                                reject_msg_to_sender_on_discard=options.reject_msg_to_sender_on_discard)

    print("The following queues will be manipulated in %s environment! " % settings.env)
    pprint.pprint(queues)

    s = raw_input('Do you want to continue? N/y? ')

    if s.lower() == 'y':
        for cmd in commands.commands:
            connection.rpc(str(cmd))
    else:
        print("chickening out...")
