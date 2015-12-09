#!/usr/bin/env python

import sys
import logging
logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)
from optparse import OptionParser
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceCommandQueue import SolaceCommandQueue
import libsolace.settingsloader as settings

def solace_bridge(options=None, **kwargs):
    """ Create / Update Profile """

    logging.info("Bridge Options: %s" % options)
    primaryCluster = SolaceAPI(options.primary, testmode=options.testmode)
    drCluster = SolaceAPI(options.backup, testmode=options.testmode)
    cq = SolaceCommandQueue()

    # VPN's to bridge
    vpns = []
    for vpn in options.vpns:
        try:
            vn = vpn % options.environment
            logging.info("Environment substituted VPN name: %s" % vn)
            vpns.append(vn)
        except Exception, e:
            logging.warn("No environment name substitution, using literal VPN name: %s" % vpn)
            vpns.append(vpn)

    logging.info("VPNs to bridge, %s" % vpns)

    for vpn in vpns:
        # try substitite environment into vpn_name if it is formated '%s_somename'
        try:
            bridgeName = vpn % options.environment
        except Exception, e:
            bridgeName = vpn

        logging.info("Creating Bridge: %s" % bridgeName)

        primaryBridgeName = "%s_%s" % ("primary", bridgeName)
        backupBridgeName = "%s_%s" % ("backup", bridgeName)

        logging.info("Primary Bridge Name: %s" % primaryBridgeName)
        logging.info("Backup Bridge Name: %s" % backupBridgeName)

        # primary cluster, primary bridge QCOK
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Primary Bridge %s on Primary Appliance" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.create.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.create.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.create.bridge.primary
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), primaryOnly=True)

        # primary cluster, backup bridge QCOK
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Backup Bridge %s on Backup Appliance" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.create.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.create.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.create.bridge.backup
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), backupOnly=True)

        # backup cluster, primary bridge QCOK
        drCluster.xmlbuilder = SolaceXMLBuilder("DR Cluster, Primary Bridge %s on Primary Appliance" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.create.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.create.bridge.vpn_name = vpn
        drCluster.xmlbuilder.create.bridge.primary
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
        drCluster.rpc(str(drCluster.xmlbuilder), primaryOnly=True)

        # backup cluster, backup bridge QCOK
        drCluster.xmlbuilder = SolaceXMLBuilder("DR Cluster, Backup Bridge %s on Backup Appliance" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.create.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.create.bridge.vpn_name = vpn
        drCluster.xmlbuilder.create.bridge.backup
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
        drCluster.rpc(str(drCluster.xmlbuilder), backupOnly=True)

        # primary cluster, primary bridge remote QCOK
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Primary Remote %s on Primary Appliance" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.primary
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.connect_via
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.addr = options.backup_addr
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.interface
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.phys_intf = options.primary_phys_intf
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), primaryOnly=True)

        # primary cluster, primary bridge remote USERNAME
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Primary Bridge Remote %s on Primary Appliance Username" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.primary
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.connect_via
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.addr = options.backup_addr
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.interface
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.phys_intf = options.primary_phys_intf
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.client_username.name = vpn
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.client_username.password = options.password
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), primaryOnly=True)

        # primary cluster, backup bridge remote QCOK
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Backup Remote %s on Primary Appliance" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.backup
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.connect_via
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.addr = options.backup_addr
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.interface
        primaryCluster.xmlbuilder.bridge.remote.create.message_vpn.phys_intf = options.primary_phys_intf
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), backupOnly=True)

        # primary cluster, backup bridge remote username
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Backup Bridge Remote %s on Backup Appliance Username" % backupBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.backup
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.connect_via
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.addr = options.backup_addr
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.interface
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.phys_intf = options.primary_phys_intf
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.client_username.name = vpn
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.client_username.password = options.password
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), backupOnly=True)

        # backup cluster, primary bridge remote QCOK
        drCluster.xmlbuilder = SolaceXMLBuilder("DR Cluster, Primary Bridge v:Remote %s on Primary Appliance" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.bridge.vpn_name = vpn
        drCluster.xmlbuilder.bridge.primary
        drCluster.xmlbuilder.bridge.remote.create.message_vpn.vpn_name = vpn
        drCluster.xmlbuilder.bridge.remote.create.message_vpn.router
        drCluster.xmlbuilder.bridge.remote.create.message_vpn.virtual_router_name = "v:%s" % options.primary_cluster_primary_node_name
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
        drCluster.rpc(str(drCluster.xmlbuilder), primaryOnly=True)

        # backup cluster, primary bridge, remote username
        drCluster.xmlbuilder = SolaceXMLBuilder("DR Cluster, Backup Bridge Remote %s on Backup Appliance Username" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.bridge.vpn_name = vpn
        drCluster.xmlbuilder.bridge.primary
        drCluster.xmlbuilder.bridge.remote.message_vpn.vpn_name = vpn
        drCluster.xmlbuilder.bridge.remote.message_vpn.router
        drCluster.xmlbuilder.bridge.remote.message_vpn.virtual_router_name = "v:%s" % options.primary_cluster_primary_node_name
        drCluster.xmlbuilder.bridge.remote.message_vpn.client_username.name = vpn
        drCluster.xmlbuilder.bridge.remote.message_vpn.client_username.password = options.password
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
        drCluster.rpc(str(drCluster.xmlbuilder), primaryOnly=True)

        # backup cluster, backup bridge remote
        drCluster.xmlbuilder = SolaceXMLBuilder("DR Cluster, Backup Bridge Remote %s on Backup Appliance" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.bridge.vpn_name = vpn
        drCluster.xmlbuilder.bridge.backup
        drCluster.xmlbuilder.bridge.remote.create.message_vpn.vpn_name = vpn
        drCluster.xmlbuilder.bridge.remote.create.message_vpn.router
        drCluster.xmlbuilder.bridge.remote.create.message_vpn.virtual_router_name = "v:%s" % options.primary_cluster_primary_node_name
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
        drCluster.rpc(str(drCluster.xmlbuilder), backupOnly=True)

        # backup cluster, backup bridge, remote username
        drCluster.xmlbuilder = SolaceXMLBuilder("DR Cluster, Backup Bridge Remote %s on Backup Appliance Username" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.bridge.vpn_name = vpn
        drCluster.xmlbuilder.bridge.backup
        drCluster.xmlbuilder.bridge.remote.message_vpn.vpn_name = vpn
        drCluster.xmlbuilder.bridge.remote.message_vpn.router
        drCluster.xmlbuilder.bridge.remote.message_vpn.virtual_router_name = "v:%s" % options.primary_cluster_primary_node_name
        drCluster.xmlbuilder.bridge.remote.message_vpn.client_username.name = vpn
        drCluster.xmlbuilder.bridge.remote.message_vpn.client_username.password = options.password
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
        drCluster.rpc(str(drCluster.xmlbuilder), backupOnly=True)


        ''' NO SHUTDOWN BRIDGE
        <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
          <bridge>
            <bridge-name>backup_dev_testvpn</bridge-name>
            <vpn-name>dev_testvpn</vpn-name>
            <backup/>
            <no>
              <shutdown/>
            </no>
          </bridge>
        </rpc>
        '''
        # primary cluster, enable primary bridges
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Enable Bridge %s on Primary Appliance" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.primary
        primaryCluster.xmlbuilder.bridge.no.shutdown
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), primaryOnly=True)

        # primary cluster, enable backup bridges
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Enable Bridge %s on Backup Appliance" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.backup
        primaryCluster.xmlbuilder.bridge.no.shutdown
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), backupOnly=True)

        # dr cluster, enable primary bridges
        drCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Enable Bridge %s on Primary Appliance" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.bridge.vpn_name = vpn
        drCluster.xmlbuilder.bridge.primary
        drCluster.xmlbuilder.bridge.no.shutdown
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
        drCluster.rpc(str(drCluster.xmlbuilder), primaryOnly=True)

        # dr cluster, enable backup bridges
        drCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Enable Bridge %s on Backup Appliance" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.bridge.vpn_name = vpn
        drCluster.xmlbuilder.bridge.backup
        drCluster.xmlbuilder.bridge.no.shutdown
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
        drCluster.rpc(str(drCluster.xmlbuilder), backupOnly=True)


        # primary cluster, primary appliance, primary bridge, enable remote
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Enable Bridge Remote %s on Primary Appliance" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.primary
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.connect_via
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.addr = options.backup_addr
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.interface
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.phys_intf = options.primary_phys_intf
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.no.shutdown
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), primaryOnly=True)

        # primary cluster, backup appliance, primary bridge, enable remote
        primaryCluster.xmlbuilder = SolaceXMLBuilder("Primary Cluster, Enable Bridge Remote %s on Primary Appliance" % primaryBridgeName, version=options.soltr_version)
        primaryCluster.xmlbuilder.bridge.bridge_name = primaryBridgeName
        primaryCluster.xmlbuilder.bridge.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.backup
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.vpn_name = vpn
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.connect_via
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.addr = options.backup_addr
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.interface
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.phys_intf = options.primary_phys_intf
        primaryCluster.xmlbuilder.bridge.remote.message_vpn.no.shutdown
        cq.enqueue(str(primaryCluster.xmlbuilder)) # validate the XML
        primaryCluster.rpc(str(primaryCluster.xmlbuilder), backupOnly=True)

        ''' NO SHUTDOWN THE REMOTE
                <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
                  <bridge>
                    <bridge-name>backup_dev_testvpn</bridge-name>
                    <vpn-name>dev_testvpn</vpn-name>
                    <backup/>
                    <remote>
                      <message-vpn>
                        <vpn-name>test_vpn</vpn-name>
                        <router/>
                        <virtual-router-name>v:solace1</virtual-router-name>
                        <no>
                          <shutdown/>
                        </no>
                      </message-vpn>
                    </remote>
                  </bridge>
                </rpc>
        '''
        # dr cluster, primary appliance, primary bridge, enable remote
        drCluster.xmlbuilder = SolaceXMLBuilder("DR Cluster, Backup Bridge Remote %s on Backup Appliance Username" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.bridge.vpn_name = vpn
        drCluster.xmlbuilder.bridge.primary
        drCluster.xmlbuilder.bridge.remote.message_vpn.vpn_name = vpn
        drCluster.xmlbuilder.bridge.remote.message_vpn.router
        drCluster.xmlbuilder.bridge.remote.message_vpn.virtual_router_name = "v:%s" % options.primary_cluster_primary_node_name
        drCluster.xmlbuilder.bridge.remote.message_vpn.no.shutdown
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
        drCluster.rpc(str(drCluster.xmlbuilder), primaryOnly=True)

        # dr cluster, backup appliance, backup bridge, enable remote
        drCluster.xmlbuilder = SolaceXMLBuilder("DR Cluster, Backup Bridge Remote %s on Backup Appliance Username" % backupBridgeName, version=options.soltr_version)
        drCluster.xmlbuilder.bridge.bridge_name = backupBridgeName
        drCluster.xmlbuilder.bridge.vpn_name = vpn
        drCluster.xmlbuilder.bridge.backup
        drCluster.xmlbuilder.bridge.remote.message_vpn.vpn_name = vpn
        drCluster.xmlbuilder.bridge.remote.message_vpn.router
        drCluster.xmlbuilder.bridge.remote.message_vpn.virtual_router_name = "v:%s" % options.primary_cluster_primary_node_name
        drCluster.xmlbuilder.bridge.remote.message_vpn.no.shutdown
        cq.enqueue(str(drCluster.xmlbuilder)) # validate the XML
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

    solace_bridge(options=options)
