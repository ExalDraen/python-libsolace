#!/usr/bin/env python

import sys
import logging
logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)
from optparse import OptionParser
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.items.SolaceQueue import SolaceQueue
from libsolace.items.SolaceBridge import SolaceBridge
import libsolace.settingsloader as settings

def solace_bridge(options=None, **kwargs):
    """ Create / Update Profile """

    logging.info("Bridge Options: %s" % options)
    bridgeApi = SolaceBridge(options=options)

    for command in bridgeApi.cq.commands:
        logging.info("Command: %s kwargs: %s" % command)

if __name__ == "__main__":
    usage = """
    Create a bridge between two solace clusters

    This tool will link two identically named VPNS in two different solace
    appliance clusters.

    """
    parser = OptionParser(usage=usage)
    parser.add_option("--primary", action="store", type="string", dest="primary",
                      help="primary appliances environment name")
    parser.add_option("--primary_phys_intf", action="store", type="string", dest="primary_phys_intf",
                      default="1/1/lag1", help="Primary appliance interface, default: 1/1/lag1")
    parser.add_option("--primary_cluster_primary_node_name", action="store", type="string", dest="primary_cluster_primary_node_name",
                      default="solace1", help="Primary cluster primary router name, default: solace1")
    parser.add_option("--backup", action="store", type="string", dest="backup",
                      help="backup appliances environment name")
    parser.add_option("--backup_addr", action="store", type="string", dest="backup_addr",
                      help="Backup / DR appliance service address e.g. 10.96.12.6:55555")
    parser.add_option("-e", "--environment", action="store", type="string", dest="environment",
                      help="Environment prefix of VPN's, used in concert with vpn name %s place holder. e.g. qa1")
    parser.add_option("--password", action="store", type="string", dest="password",
                      default="password", help="Password for username of remote VPN ( the username is the vpn_name )")
    parser.add_option("-v", "--vpn", action="store", type="string", dest="vpnname",
                      default=None, help="VPN name(s) to bridge, eg: %s_event | %s_myvpn,othervpn")
    parser.add_option("-s", "--soltr_version", action="store", type="string", dest="soltr_version",
                      default="soltr/6_0", help="solOS TR version e.g. soltr/6_2 for 6.2+ appliances which uses VPN scoped profiles")
    parser.add_option("-d", "--debug", action="store_true", dest="debugmode",
                      default=False, help="enable debug mode logging")
    parser.add_option("-t", "--testmode", action="store_true", dest="testmode",
                      default=False, help="only test configuration and exit")

    # Parse Opts
    (options, args) = parser.parse_args()


    if not options.environment:   # if filename is not given
        parser.error('Environment Not Given')
    if not options.primary:
        parser.error('Primary cluster environment name not provided')
    if not options.backup:
        parser.error('Backup cluster environment name not provided')

    if options.testmode:
        logging.info("Test Mode")
    if options.debugmode:
        logging.getLogger().setLevel(logging.DEBUG)

    options.vpns = options.vpnname.split(',')

    solace_bridge(options=options, testmode=options.testmode, version=options.soltr_version)
