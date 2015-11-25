#!/usr/bin/env python
import sys
import logging
logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',
                    stream=sys.stdout)

from optparse import OptionParser
import pprint
from libsolace.solace import SolaceAPI
from libsolace.solacehelper import SolaceXMLBuilder
import libsolace.settingsloader as settings
settings.debugmode = False


def shutdown_vpn(connection, vpn_name):
    s_cmd = SolaceXMLBuilder("Shutdown the VPN")
    s_cmd.message_vpn.vpn_name = vpn_name
    s_cmd.message_vpn.shutdown
    connection.rpc(str(s_cmd))


def check_queue_in_use(connection, vpn_name, queue):
    q = connection.get_queue(queue, vpn_name, detail=True)
    try:
        resp = q[0]['rpc-reply']['rpc']['show']['queue']['queues']['queue']['info']
        bind_count = int(resp['bind-count'])
        topic_subscription_count = int(resp['topic-subscription-count'])
        current_spool_usage_in_mb = float(resp['current-spool-usage-in-mb'])
        if bind_count > 0:
            logging.warn("Queue %s is being used. Bind count: %s" % (queue, str(bind_count)))
            return True
        if topic_subscription_count > 0:
            logging.warn("Queue %s is being used. Topic subscription count: %s" % (queue, str(topic_subscription_count)))
            return True
        if current_spool_usage_in_mb > 0:
            logging.warn("Queue %s has messages in spool. Current spool usage: %sMB" % (queue, str(current_spool_usage_in_mb)))
            return True
        return False
    except Exception, e:
        logging.error("Exception thrown: %s" % e)
        logging.error("Queue '%s' does not exist, quitting...." % queue)
        sys.exit(1)


def verify_queues(connection, vpn_name):
    result = dict()
    s_cmd = SolaceXMLBuilder("Retrieving list of queues")
    s_cmd.show.queue.name = '*'
    s_cmd.show.queue.vpn_name = vpn_name
    reply = connection.rpc(str(s_cmd))
    for host in reply:
        try:
            host['rpc-reply']['rpc']['show']['queue']['queues']['queue']
        except:
            continue
        for queue in host['rpc-reply']['rpc']['show']['queue']['queues']['queue']:
            try:
                queue_name = queue['name']
                logging.info("Checking Queue: %s" % queue_name)
                result[queue_name] = check_queue_in_use(connection, vpn_name, queue_name)
            except:
                logging.warn("No queue could be processed, probably standby box")
                pass
    if True in result.values():
        logging.error("Queues are still in use: %s" % ",".join([x for x in result.keys() if result[x] is True]))
        sys.exit(1)
    logging.info("No queues are being used")


def verify_users(connection, vpn_name):
    """
    :param connection: instance of SolaceAPI
    :type connection: SolaceAPI
    :param vpn_name: name of vpn
    :type vpn_name: str
    """
    result = dict()
    s_cmd = SolaceXMLBuilder("Retrieving list of client-usernames")
    s_cmd.show.client_username.name = '*'
    s_cmd.show.client_username.vpn_name = vpn_name
    reply = connection.rpc(str(s_cmd))
    for host in reply:
        try:
            host['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']
        except:
            continue
        for user in host['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']:
            client_username = user['client-username']
            result[client_username] = connection.is_client_username_inuse(client_username, vpn_name)
    if True in result.values():
        logging.error("Users are still in use: %s" % ",".join([x for x in result.keys() if result[x] is True]))
        sys.exit(1)
    logging.info("No users found in use")


def delete_queues(connection, vpn_name):
    logging.info("Deleting Queues")
    s_cmd = SolaceXMLBuilder("Retrieving list of queues")
    s_cmd.show.queue.name = '*'
    s_cmd.show.queue.vpn_name = vpn_name
    reply = connection.rpc(str(s_cmd))
    for host in reply:
        logging.debug("Checking Reply: %s" % reply)
        try:
            host['rpc-reply']['rpc']['show']['queue']['queues']['queue']
        except:
            # skip passive node
            continue
        for queue in host['rpc-reply']['rpc']['show']['queue']['queues']['queue']:
            # Shutdown the Queue
            logging.debug("Found Queue: %s" % queue)
            queue_name = queue['name']
            logging.debug("Queue to delete: %s" % queue_name)
            s_cmd = SolaceXMLBuilder("Shutdown Queue %s" % queue_name)
            s_cmd.message_spool.vpn_name = vpn_name
            s_cmd.message_spool.queue.name = queue_name
            s_cmd.message_spool.queue.shutdown
            connection.rpc(str(s_cmd))
            s_cmd = SolaceXMLBuilder("Delete Queue %s" % queue_name)
            s_cmd.message_spool.vpn_name = vpn_name
            s_cmd.message_spool.no.queue.name = queue_name
            connection.rpc(str(s_cmd))

def delete_users(connection, vpn_name):
    s_cmd = SolaceXMLBuilder("Retrieving list of client-usernames")
    s_cmd.show.client_username.name = '*'
    s_cmd.show.client_username.vpn_name = vpn_name
    reply = connection.rpc(str(s_cmd))
    for host in reply:
        try:
            host['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']
        except:
            # skip passive node
            continue
        for user in host['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']:
            client_username = user['client-username']
            # Shutdown the user
            s_cmd = SolaceXMLBuilder("Shutdown User %s" % client_username)
            s_cmd.client_username.username = client_username
            s_cmd.client_username.vpn_name = vpn_name
            s_cmd.client_username.shutdown
            connection.rpc(str(s_cmd))
            # Delete the user
            s_cmd = SolaceXMLBuilder("Delete User %s" % client_username)
            s_cmd.no.client_username.username = client_username
            s_cmd.no.client_username.vpn_name = vpn_name
            connection.rpc(str(s_cmd))


def delete_acl_profile(connection, vpn_name, acl_profile):
    s_cmd = SolaceXMLBuilder("VPN %s Deleting ACL Profile %s" % (vpn_name, acl_profile))
    s_cmd.no.acl_profile.name = acl_profile
    s_cmd.no.acl_profile.vpn_name = vpn_name
    connection.rpc(str(s_cmd))


def delete_vpn(connection, vpn_name):
    s_cmd = SolaceXMLBuilder()
    s_cmd.no.message_vpn.vpn_name=vpn_name
    connection.rpc(str(s_cmd))


usage = "%s -e dev -V 'bonus'" % (sys.argv[0])
parser = OptionParser(usage=usage)
parser.add_option("-e", "--env", "--environment", action="store", type="string", dest="env",
                  help="environment to run job in eg:[ dev | ci1 | si1 | qa1 | pt1 | prod ]")
parser.add_option("-V", "--vpn", action="store", type="string", dest="vpn_name",
                  help="name of vpn, eg: domainevent")
parser.add_option("-t", "--testmode", action="store_true", dest="testmode",
                  default=False, help="only test configuration and exit")
parser.add_option("-f", "--force", action="store_true", dest="force",
                  default=False, help="force remove the queue(s) even if it is being used")
parser.add_option("-d", "--debug", action="store_true", dest="debug",
                  default=False, help="toggles solace debug mode")

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
    logging.getLogger().setLevel(logging.INFO)

# Details for VPN that we should discard, including
# * VPN
# * ACL profile
# * User
environment = options.env
vpn = options.vpn_name
vpn_name = vpn # '%s_%s' % (environment, vpn)
username = vpn # '%s_%s' % (environment, vpn)
acl_profile = vpn_name
solace = SolaceAPI(options.env, testmode=options.testmode)

# Shutdown the VPN
shutdown_vpn(solace, vpn_name)

# Verify queue usage
verify_queues(solace, vpn_name)

# Verify users
try:
    verify_users(solace, vpn_name)
except AttributeError, ex:
    logging.warn("Verify users threw an exception: %s" % str(ex))

# Delete queues
delete_queues(solace, vpn_name)

# Delete users
delete_users(solace, vpn_name)

# Delete acl profile
delete_acl_profile(solace, vpn_name, acl_profile)

# Delete a VPN
delete_vpn(solace, vpn_name)
