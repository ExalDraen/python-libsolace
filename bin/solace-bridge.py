#!/usr/bin/env python

import sys
import logging
logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)
from optparse import OptionParser
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
import libsolace.settingsloader as settings

def solace_bridge(options=None, **kwargs):
    """ Create / Update Profile """

    logging.info("Bridge Options: %s" % options)
    primaryCluster = SolaceAPI(options.primary, testmode=options.testmode)
    drCluster = SolaceAPI(options.backup, testmode=options.testmode)

    # VPN's to bridge
    vpns = []
    for vpn in options.vpns:
        try:
            vpns.append(vpn % options.environment)
        except Exception, e:
            vpns.append(vpn)

    logging.info("VPNs to bridge, %s" % vpns)

    for vpn in vpns:
        # try substitite environment into vpn_name if it is formated '%s_somename'
        try:
            bridgeName = vpn % options.environment
        except Exception, e:
            bridgeName = vpn

        logging.info("Bridge Name: %s" % bridgeName)

        primaryBridgeName = "%s_%s" % ("primary", bridgeName)
        backupBridgeName = "%s_%s" % ("backup", bridgeName)

        # primary cluster, primary bridge QCOK
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Creating Primary Primary Bridge %s" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.create.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.create.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.create.bridge.primary
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), primaryOnly=True)

        # primary cluster, backup bridge QCOK
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Creating Primary Backup Bridge %s" % backupBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.create.bridge.bridge_name = backupBridgeName
        primaryCluster.xmlbuilder.create.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.create.bridge.backup
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), backupOnly=True)

        # backup cluster, primary bridge QCOK
        drCluster.xmlbuilder = SolaceXMLBuilder("Creating DR Primary Bridge %s" % primaryBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.create.bridge.bridge_name = primaryBridgeName
        drCluster.xmlbuilder.create.bridge.vpn_name = vpn
        drCluster.xmlbuilder.create.bridge.primary
        drCluster.rpc(str(drCluster.xmlbuilder), primaryOnly=True)

        # backup cluster, backup bridge QCOK
        drCluster.xmlbuilder = SolaceXMLBuilder("Creating DR Backup Bridge %s" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.create.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.create.bridge.vpn_name = vpn
        drCluster.xmlbuilder.create.bridge.backup
        drCluster.rpc(str(drCluster.xmlbuilder), backupOnly=True)

        # primary cluster, primary bridge remote QCOK
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Creating Primary Cluster, Primary remote %s" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.create.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.create.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.create.bridge.primary
        primaryCluster.xmlbuilder.remote.create.message_vpn.vpn_name = vpn
        primaryCluster.xmlbuilder.remote.create.connect_via
        primaryCluster.xmlbuilder.remote.addr = options.backup_addr
        primaryCluster.xmlbuilder.remote.interface
        primaryCluster.xmlbuilder.phys_intf = options.primary_phys_intf
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), primaryOnly=True)

        # primary cluster, backup bridge remote QCOK
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Creating Primary Cluster, Backup remote %s" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.create.bridge.bridge_name = backupBridgeName
        primaryCluster.xmlbuilder.create.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.create.bridge.backup
        primaryCluster.xmlbuilder.remote.create.message_vpn.vpn_name = vpn
        primaryCluster.xmlbuilder.remote.create.connect_via
        primaryCluster.xmlbuilder.remote.addr = options.backup_addr
        primaryCluster.xmlbuilder.remote.interface
        primaryCluster.xmlbuilder.phys_intf = options.primary_phys_intf
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), backupOnly=True)

        # backup cluster, primary bridge remote QCOK
        drCluster.xmlbuilder = SolaceXMLBuilder("Creating DR Primary Bridge remote %s" % primaryBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.create.bridge.bridge_name = primaryBridgeName
        drCluster.xmlbuilder.create.bridge.vpn_name = vpn
        drCluster.xmlbuilder.create.bridge.primary
        drCluster.xmlbuilder.remote.create.message_vpn.vpn_name = vpn
        drCluster.xmlbuilder.remote.create.router
        drCluster.xmlbuilder.remote.create.virtual_router_name = "v:%s" % options.primary_cluster_primary_node_name
        drCluster.rpc(str(drCluster.xmlbuilder), primaryOnly=True)

        # backup cluster, backup bridge remote
        drCluster.xmlbuilder = SolaceXMLBuilder("Creating DR Primary Bridge remote %s" % primaryBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.create.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.create.bridge.vpn_name = vpn
        drCluster.xmlbuilder.create.bridge.primary
        drCluster.xmlbuilder.remote.create.message_vpn.vpn_name = vpn
        drCluster.xmlbuilder.remote.create.router
        drCluster.xmlbuilder.remote.create.virtual_router_name = "v:%s" % options.primary_cluster_primary_node_name
        drCluster.rpc(str(drCluster.xmlbuilder), backupOnly=True)


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

    solace_bridge(options=options)
