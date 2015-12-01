#!/usr/bin/env python

import sys
import logging
logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)
from optparse import OptionParser
from libsolace.solace import SolaceAPI
from libsolace.solacehelper import SolaceXMLBuilder
import libsolace.settingsloader as settings


def solace_profile(options=None):
    """ Create / Update Profile

    """

    logging.info("Profile Options: %s" % options)

    for environment in options.environment:
        solace = SolaceAPI(environment,testmode=options.testmode)

        # try substitite environment into vpn_name if it is formated '%s_somename'
        try:
            vpnname = options.vpnname % environment
        except Exception, e:
            vpnname = options.vpnname

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

            '''
            <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
              <client-profile>
                <name>glassfish</name>
                <max-connections-per-client-username>
                  <value>500</value>
                </max-connections-per-client-username>
              </client-profile>
            </rpc>
            '''
            cmd = SolaceXMLBuilder("Setting Properties", version=options.soltr_version)
            cmd.client_profile.name = profile
            if options.soltr_version == "soltr/6_2":
                cmd.client_profile.vpn_name = vpnname
            cmd.client_profile.max_connections_per_client_username.value = options.max_clients
            solace.rpc(str(cmd))

if __name__ == "__main__":
    usage = """ Delete a Solace Client User within a VPN
		Example:
		./solace-profile.py -e ci1,dev,si1,qa1,pt1 -v %s_domainevent -p "%s_someprofile"
		./solace-profile.py -e ci1,dev,si1,qa1,pt1 -v %s_domainevent -p someprofile,%s_otherprofile

"""
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--environment", action="store", type="string", dest="environment",
                      help="environment to apply changes to eg:[ qa1 | ci1 | si1 | prod | qa1,ci1,si1 ]")
    parser.add_option("-v", "--vpn", action="store", type="string", dest="vpnname",
                      default=None, help="vpn name to apply changes to eg: my_vpn or %s_domainevent, %s is literal and will be replaced with env!")
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
    solace_profile(options=options)
