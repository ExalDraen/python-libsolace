#!/usr/bin/env python

"""

This script removes the following queues from Solace. Before doing so it will check 3 things
1. Does queue have clients connected?
2. Does queue have topic subscribers?
3. Does queue have messages in spool?

If any of them are true for any of the queues provided, the script will not proceed with the removal.
This behavior can be overridden by providing the --force flag

"""

import logging
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from optparse import OptionParser
import sys
import pprint

def generateXML(connection, options, vpn_name=None, queues=None):
    """
    :param vpn_name: string name of vpn
    :param queues: list of queues to manipulate
    :return: commands
    """
    # commandQueue is used to stack and validate solace commands
    commands = SolaceCommandQueue()

    if options.settings is None:
        settings_file = 'default'
    else:
        settings_file = options.settings

    print """============ Task details ============
Queues: %s
VPN: %s
Environment: %s
Settings file: %s
Force remove: %s
Shutdown only: %s
======================================""" % (",".join(queues), vpn_name, options.env, settings_file, str(options.force), str(options.shutdownonly))

    def shutdown_queue(queue):
        cmd = SolaceXMLBuilder("Full shutdown on queue: %s" % queue.strip())
        cmd.message_spool.vpn_name = vpn_name
        cmd.message_spool.queue.name = queue.strip()
        cmd.message_spool.queue.shutdown.full
        commands.enqueue(cmd)

    def delete_queue(queue):
        cmd = SolaceXMLBuilder("Deleting queue: %s" % queue.strip())
        cmd.message_spool.vpn_name = vpn_name
        cmd.message_spool.no.queue.name = queue.strip()
        commands.enqueue(cmd)

    def check_queue_in_use(queue):
        q = connection.get_queue(queue,vpn_name,detail=True)
        try:
            resp = q[0]['rpc-reply']['rpc']['show']['queue']['queues']['queue']['info']
            bind_count = int(resp['bind-count'])
            topic_subscription_count = int(resp['topic-subscription-count'])
            current_spool_usage_in_mb = float(resp['current-spool-usage-in-mb'])
            if bind_count > 0:
                print "WARNING: Queue %s is being used. Bind count: %s" % (queue,str(bind_count))
                return True
            if topic_subscription_count > 0:
                print "WARNING: Queue %s is being used. Topic subscription count: %s" % (queue,str(topic_subscription_count))
                return True
            if current_spool_usage_in_mb > 0:
                print "WARNING: Queue %s has messages in spool. Current spool usage: %sMB" % (queue,str(current_spool_usage_in_mb))
                return True
            return False
        except Exception, e:
            print "ERROR: Exception thrown: %s" % e
            print "ERROR: Queue '%s' does not exist, quitting...." % queue
            sys.exit(1)

    try:
        queue_status = []
        print "INFO: Checking if queues are being used"
        for queue in queues:
            if check_queue_in_use(queue): queue_status.append(queue)

        if len(queue_status) > 0:
            print "WARNING: %s queues were found being in use. These were the queues in use: %s" % (len(queue_status),",".join(queue_status))
            if options.force:
                print "WARNING: Force mode is enabled, proceeding with wiping the queues even though the seem to be in use"
            else:
                print "ERROR: Force mode is disabled and some of the queues were found being in use, will quit now"
                sys.exit(1)
        else:
            print "INFO: No queue found as being in use, that's good"

        for queue in queues:
            shutdown_queue(queue)
            if options.shutdownonly:
                print "INFO: Shutdown-only option is set, only adding queue %s to the list to shutdown" % queue
            else:
                print "INFO: Adding queue %s to the list of queues to remove" % queue
                delete_queue(queue)
    except Exception, e:
        print "[ERROR] Exception: %s" % e

    print "[INFO] Returning the plan"
    return commands

if __name__ == '__main__':
    """ deletes solace queues """

    usage = "./solace-delete-queue.py -e dev -V 'test_dev_keghol' -q queue.something"
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--env", "--environment", action="store", type="string", dest="env",
                      help="environment to run job in eg:[ dev | ci1 | si1 | qa1 | pt1 | prod ]")
    parser.add_option("-V", "--vpn", action="store", type="string", dest="vpn_name",
                      help="literal name of vpn, eg: pt1_domainevent")
    parser.add_option("-t", "--testmode", action="store_true", dest="testmode",
                      default=False, help="only test configuration and exit")
    parser.add_option("-q" , "--queues", action="store", dest="queues",
                      default=[], help="comma separated list of queues")
    parser.add_option("-f", "--force", action="store_true", dest="force",
                      default=False, help="force remove the queue(s) even if it is being used")
    parser.add_option("-s", "--shutdown-only", action="store_true", dest="shutdownonly",
                      default=False, help="shuts down queue(s) instead of removing them")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="toggles solace debug mode")
    parser.add_option("--settings", action="store", dest="settings",
                      default=None, help="path to settings file")

    (options, args) = parser.parse_args()

    if not options.env:
        parser.print_help()
        sys.exit()
    if not options.vpn_name:
        parser.print_help()
        sys.exit()
    if options.testmode:
        logging.info("TEST MODE ACTIVE!!!")
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.ERROR)
    if options.settings != None:
        import imp
        settings = imp.load_source('settings', options.settings)
        print "Using settings file: %s" % options.settings
    else:
        import libsolace.settingsloader as settings

    settings.env = options.env.lower()

    queues = options.queues.split(',')

    logging.info("Connecting to appliance in %s, testmode:%s" % (settings.env, options.testmode))
    connection = SolaceAPI(settings.env, testmode=options.testmode)
    commands = generateXML(connection, options, vpn_name=options.vpn_name, queues=queues)

    print("The following queues will be manipulated in %s environment! " % settings.env)
    pprint.pprint(queues)

    s = raw_input('Do you want to continue? N/y? ')

    if s.lower() == 'y':
        for cmd in commands.commands:
            connection.rpc(str(cmd))
    else:
        print("chickening out...")
