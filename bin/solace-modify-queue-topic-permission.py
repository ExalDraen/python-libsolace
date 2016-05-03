#!/usr/bin/env python

"""
This script changes the following queues permission to "modify-topic". It does so by disabling egress for the queues,
updating the property and re-enabling the queue!


"""
import sys
import logging

logging.basicConfig(format='%(filename)s:%(lineno)s %(levelname)s %(message)s', stream=sys.stdout)
logging.getLogger("urllib3").setLevel(logging.WARNING)
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
from optparse import OptionParser
import sys
import pprint

queues = []


def generateXML(vpn_name=None, queues=None, api=None):
    """
    @keyword api:
    @type api: SolaceAPI
    @keyword vpn_name: string name of vpn
    @keyword queues: list of queues to manipulate
    :return: commands
    """
    # commandQueue is used to stack and validate solace commands
    commands = []


    try:
        for queue in queues:

            commands.append(api.manage(settings.SOLACE_QUEUE_PLUGIN).shutdown_egress(shutdown_on_apply=True,
                                                                               vpn_name=vpn_name,
                                                                               queue_name=queue))


            commands.append(api.manage(settings.SOLACE_QUEUE_PLUGIN).permission(permission="modify-topic",
                                                                          shutdown_on_apply=True,
                                                                          vpn_name=vpn_name,
                                                                          queue_name=queue))

            commands.append(api.manage(settings.SOLACE_QUEUE_PLUGIN).enable(vpn_name=vpn_name,
                                                                            queue_name=queue))


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
    parser.add_option("-q", "--queues", action="store", type="string", dest="queues",
                      help="comma separated list of queues")

    (options, args) = parser.parse_args()

    if not options.env:
        parser.print_help()
        sys.exit()
    if not options.vpn_name:
        parser.print_help()
        sys.exit()
    if not options.queues:
        parser.print_help()
        sys.exit()
    if options.testmode:
        logging.info("TEST MODE ACTIVE!!!")

    settings.env = options.env.lower()
    queues = options.queues.split(',')

    logging.info("Connecting to appliance in %s, testmode:%s" % (settings.env, options.testmode))
    connection = SolaceAPI(settings.env, testmode=options.testmode)
    commands = generateXML(vpn_name=options.vpn_name, queues=queues, api=connection)

    print("The following queues will be manipulated in %s environment! " % settings.env)
    pprint.pprint(queues)

    s = raw_input('Do you want to continue? N/y? ')

    if s.lower() == 'y':
        for cmd in commands:
            connection.rpc(cmd)
    else:
        print("chickening out...")
