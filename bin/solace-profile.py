#!/usr/bin/env python

import sys
import logging
logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)
from optparse import OptionParser
from libsolace.solace import SolaceAPI
from libsolace.solacehelper import SolaceXMLBuilder
import libsolace.settingsloader as settings


def solace_profile(options=None, vpn=None):
    """ Create / Update Profile

    """

    logging.info("Profile Options: %s" % options)

    for environment in options.environment:
        solace = SolaceAPI(environment,testmode=options.testmode)

        # try substitite environment into vpn_name if it is formated '%s_somename'
        try:
            vpnname = vpn % environment
        except Exception, e:
            vpnname = vpn

        logging.info("VPN Name: %s" % vpnname)

        # Users
        profiles = []
        for profile in options.profile:
            try:
                profiles.append(profile % environment)
            except Exception, e:
                profiles.append(profile)

        for profile in profiles:
            cmd = SolaceXMLBuilder("Creating Profile %s" % profile, version=options.soltr_version)
            cmd.create.client_profile.name = profile
            if options.soltr_version == "soltr/6_2":
                cmd.create.client_profile.vpn_name = vpnname
            solace.rpc(str(cmd))


            cmd = SolaceXMLBuilder("Setting Properties", version=options.soltr_version)
            cmd.client_profile.name = profile
            if options.soltr_version == "soltr/6_2":
                cmd.client_profile.vpn_name = vpnname
            cmd.client_profile.max_connections_per_client_username.value = options.max_clients
            solace.rpc(str(cmd))

if __name__ == "__main__":
    usage = """ Create / Update a Solace Client Profile

		Example:

		solace-profile.py -e ci1,dev,si1,qa1,pt1 -v %s_domainevent -p "%s_someprofile"
		solace-profile.py -e ci1,dev,si1,qa1,pt1 -v %s_domainevent -p someprofile,%s_otherprofile
        solace-profile.py -e si1 -v %s_domainevent,%s_bonus -p glassfish -s "soltr/6_2"

"""
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--environment", action="store", type="string", dest="environment",
                      help="environment(s) to apply changes to eg:[ qa1 | prod | qa1,ci1,si1 ]")
    parser.add_option("-v", "--vpn", action="store", type="string", dest="vpnname",
                      default=None, help="VPN name for 6.2+ appliances %s is rewritten to env-name at provision time, eg: %s_event | %s_myvpn,othervpn")
    parser.add_option("-p", "--profile", action="store", type="string", dest="profile",
                      help="profile or comma separated list of profiles to delete, the %s is literal eg: [ somevpn | %s_sitemq,%s_foo ] and will be replaced with env")
    parser.add_option("-s", "--soltr_version", action="store", type="string", dest="soltr_version",
                      default="soltr/6_0", help="solOS TR version e.g. soltr/6_2")
    parser.add_option('-m', "--max-clients", action="store", type="string", dest="max_clients",
                      default="500", help="max clients per username")
    parser.add_option("-d", "--debug", action="store_true", dest="debugmode",
                      default=False, help="enable debug mode logging")
    parser.add_option("-t", "--testmode", action="store_true", dest="testmode",
                      default=False, help="only test configuration and exit")

    # Parse Opts
    (options, args) = parser.parse_args()

    # Lowecase the environment because GO seems to use uppercase
    try:
        options.environment = options.environment.lower().split(',')
    except:
        parser.print_help()

    try:
        options.vpnname = options.vpnname.lower().split(',')
    except:
        parser.print_help()

    if options.debugmode:
        logging.getLogger().setLevel(logging.DEBUG)
    if not options.environment:   # if filename is not given
        parser.error('Environment Not Given')
    if not options.profile:
        parser.error("Profile Not Given")
    if options.testmode:
        logging.info("Test mode active")

    options.profile = options.profile.split(',')

    # call the provision function
    for vpn in options.vpnname:
        logging.info("VPN: %s" % vpn)
        solace_profile(options=options, vpn=vpn)
