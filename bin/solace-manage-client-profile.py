#!/usr/bin/env python

import sys
import logging

logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',
                    stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

from optparse import OptionParser
from libsolace.SolaceAPI import SolaceAPI
from libsolace.Naming import name


def solace_manage_profile(run_options):
    """
    Deletes profile, solace 6.2+ needs to be scoped to VPN, prior versions
    are global.

    :param run_options: the Options Parser instance
    :return:
    """

    logging.info("Options: %s" % run_options)

    for environment in run_options.environment:
        solace = SolaceAPI(environment, testmode=run_options.testmode)

        # try substitute environment into vpn_name if it is formated '%s_somename'
        try:
            vpnname = name(run_options.vpnname, environment)
        except Exception, e:
            vpnname = run_options.vpnname

        # profiles
        profiles = []
        for profile in run_options.profile:
            try:
                profiles.append(profile % environment)
            except Exception, e:
                profiles.append(profile)

        if run_options.list_profiles:
            for profile in profiles:
                profile = solace.manage("SolaceClientProfile").get(name=profile, vpn_name=vpnname)
                logging.info("Profile: %s" % profile)

        if run_options.delete_profiles:
            for profile in profiles:
                cmd = SolaceXMLBuilder("Deleting Profile %s" % profile)
                cmd.no.client_profile.name = profile
                solace.rpc(str(cmd))



if __name__ == "__main__":
    usage = """ Delete a Solace Client User within a VPN
        Example:
        ./solace-manage-client-profile.py -e ci1,dev,si1,qa1,pt1 -v %s_domainevent -p "%s_someprofile"
        ./solace-manage-client-profile.py -e ci1,dev,si1,qa1,pt1 -v %s_domainevent -p someprofile,%s_otherprofile

    """
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--environment", action="store", type="string", dest="environment",
                      help="environment to apply changes to eg:[ qa1 | ci1 | si1 | prod | qa1,ci1,si1 ]")
    parser.add_option("-v", "--vpn", action="store", type="string", dest="vpnname",
                      default=None,
                      help="vpn name to apply changes to eg: my_vpn or %s_domainevent, %s is literal and will be replaced with env!")
    parser.add_option("-p", "--profile", action="store", type="string", dest="profile",
                      help="profile or comma separated list of profiles to delete, the %s is literal eg: [ somevpn | %s_sitemq,%s_foo ] and will be replaced with env")
    parser.add_option("-d", "--debug", action="store_true", dest="debugmode",
                      default=False, help="enable debug mode logging")
    parser.add_option("-t", "--testmode", action="store_true", dest="testmode",
                      default=False, help="only test configuration and exit")
    parser.add_option("-l", "--list-profiles", action="store_true", dest="list_profiles",
                      help="List all profiles on the appliance cluster")
    parser.add_option("-D", "--delete", action="store_true", dest="delete_profiles",
                      help="Delete profiles on the appliance cluster")

    # Parse Opts
    (options, args) = parser.parse_args()

    # Lowercase the environment because GO seems to use uppercase
    try:
        options.environment = options.environment.lower().split(',')
    except AttributeError, e:
        parser.print_help()

    if options.debugmode:
        logging.getLogger().setLevel(logging.DEBUG)
    if not options.environment:  # if filename is not given
        parser.error('Environment Not Given')
    if not options.profile:
        parser.error("Profile Not Given")
    if options.testmode:
        logging.info("Test mode active")
    if options.list_profiles:
        logging.info("Will show profiles matching %s" % options.profile)
    if options.delete_profiles:
        logging.info("Will delete profiles matching %s" % options.profile)

    options.profile = options.profile.split(',')

    # call the provision function
    solace_manage_profile(options)
