#!/usr/bin/env python

import sys
import logging

logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',
                    stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)
from optparse import OptionParser
from libsolace.SolaceAPI import SolaceAPI
from libsolace.Naming import name

UTILITIES_PLUGIN = "Utilities"


def solace_delete_client_username(options):
    """ Deletes users / profiles / acl's where neccesary.

    Has a shutdown only mode which only shutdowns the user

    Has a force remove now mode which kills everything!

    Shutdown User
    Delete User

    """
    for environment in options.environment:

        solace = SolaceAPI(environment, testmode=options.testmode)

        try:
            vpnname = name(options.vpnname, environment)
        except Exception, e:
            vpnname = options.vpnname

        # Users
        usernames = []
        for username in options.username:
            try:
                usernames.append(username % environment)
            except Exception, e:
                usernames.append(username)
        for username in usernames:
            # Disable / Shutdown User ( else we cant change profiles if it already exists )
            try:
                try:
                    user = \
                    solace.manage("SolaceUser").get(client_username=username, vpn_name=vpnname)[0]['rpc-reply']['rpc'][
                        'show']['client-username']['client-usernames']['client-username']
                except KeyError, e:
                    logging.error("No such user exists: %s in vpn %s" % (username, vpnname))
                    raise

                logging.info("User: %s" % user)
                user_queue_list = solace.manage(UTILITIES_PLUGIN).get_user_queues(client_username=username,
                                                                                  vpn_name=vpnname)
                if len(user_queue_list) > 0:
                    logging.error(
                            "User %s owns queues, can not remove user without reassigning ownership. VPN name: %s. List of queues: %s - skipping" % (
                                username, vpnname, ",".join(user_queue_list)))
                    continue
                else:
                    logging.info(
                            "User %s does not own any queues within VPN %s, good - continuing" % (username, vpnname))
                if solace.manage(UTILITIES_PLUGIN).is_client_user_inuse(client_username=username, vpn_name=vpnname):
                    logging.error("User %s is in use - skipping" % username)
                    continue
                else:
                    logging.info("User %s is NOT in use, good - continuing" % username)
                if bool(solace.manage("SolaceUser").get(client_username=username, vpn_name=vpnname)
                                .reply.show.client_username.client_usernames.client_username.enabled):
                    logging.info("User %s is not disabled - disabling" % username)
                    # when calling shutdown, add the shutdown_on_apply = True to make it happen
                    cmd = solace.manage("SolaceUser").shutdown(client_username=username, vpn_name=vpnname,
                                                               shutdown_on_apply=True)
                    solace.rpc(str(cmd))
                else:
                    logging.info("User %s already disabled" % username)
                if options.remove:
                    cmd = solace.manage("SolaceUser").delete(client_username=username, vpn_name=vpnname)
                    solace.rpc(str(cmd))
            except Exception, e:
                logging.info(e.message)
                logging.info("User %s does not exist - skipping" % username)
                pass


if __name__ == "__main__":
    usage = """
    Delete a Solace Client User within a VPN

    Example:
		./solace-delete-client-user.py -e ci1,dev,si1,qa1,pt1 -v %s_domainevent -u %s_sitemq
		./solace-delete-client-user.py -e ci1,dev,si1,qa1,pt1 -v %s_domainevent -u %s_sitemq,%s_foo

    """
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--environment", action="store", type="string", dest="environment",
                      help="environment to apply changes to eg:[ qa1 | ci1 | si1 | prod | qa1,ci1,si1 ]")
    parser.add_option("-v", "--vpn", action="store", type="string", dest="vpnname",
                      help="vpn name to apply changes to eg: my_vpn or %s_domainevent, %s is literal and will be replaced with env!")
    parser.add_option("-u", "--user", action="store", type="string", dest="username",
                      help="username or comma separated list of usernames to delete, the %s is literal eg: [ somevpn | %s_sitemq,%s_foo ] and will be replaced with env")
    parser.add_option("-d", "--debug", action="store_true", dest="debugmode",
                      default=False, help="enable debug mode logging")
    parser.add_option("-r", "--remove", action="store_true", dest="remove",
                      default=False, help="actually removes the user, not just disabling it")
    parser.add_option("-t", "--testmode", action="store_true", dest="testmode",
                      default=False, help="only test configuration and exit")

    # Parse Opts
    (options, args) = parser.parse_args()

    # Lowecase the environment because GO seems to use uppercase
    try:
        options.environment = options.environment.lower().split(',')
    except:
        parser.print_help()

    if options.debugmode:
        logging.getLogger().setLevel(logging.DEBUG)
    if not options.environment:  # if filename is not given
        parser.error('Environment Not Given')
    if not options.vpnname:
        parser.error("Vpn Name Not Given")
    if not options.username:
        parser.error("Username Not Given")
    if options.testmode:
        logging.info("Test mode active")

    options.username = options.username.split(',')
    # call the provision function
    solace_delete_client_username(options)
