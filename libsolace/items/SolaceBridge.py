import logging
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceAPI import SolaceAPI

class SolaceBridge:
    """ Construct a bridge between two appliance clusters to link specific VPN's """

    def __init__(self, testmode=True, shutdown_on_apply=False, options=None, version="soltr/6_0", **kwargs):
        """ Init user object

        :type testmode: boolean
        :type shutdown_on_apply: boolean
        :type options: OptionParser
        :type version: string

        """

        self.cq = SolaceCommandQueue(version=version)

        self.primaryCluster = SolaceAPI(options.primary, testmode=testmode)
        self.drCluster = SolaceAPI(options.backup, testmode=testmode)
        self.vpns = []

        for vpn in options.vpns:
            try:
                self.vpns.append(vpn % options.environment)
            except Exception, e:
                self.vpns.append(vpn)

        for vpn in self.vpns:
            try:
                bridgeName = vpn % options.environment
            except Exception, e:
                bridgeName = vpn

            logging.info("Creating Bridge: %s" % bridgeName)

            primaryBridgeName = "%s_%s" % ("primary", bridgeName)
            backupBridgeName = "%s_%s" % ("backup", bridgeName)

            logging.info("Primary Bridge Name: %s" % primaryBridgeName)
            logging.info("Backup Bridge Name: %s" % backupBridgeName)

            # create bridge on primary cluster
            self._create_bridge(self.primaryCluster, primaryBridgeName, vpn,
                version=version)

            # create bridge on the DR cluster
            self._create_bridge(self.drCluster, backupBridgeName, vpn,
                version=version)

            # create remote on primary cluster bridge
            self._create_bridge_remote_addr(self.primaryCluster, primaryBridgeName, vpn,
                options.backup_addr, options.primary_phys_intf, version=version)

            # create reverse remote on dr cluster bridge
            self._create_bridge_remote_vrouter(self.drCluster, backupBridgeName, vpn,
                options.primary_cluster_primary_node_name, version=version)


    def _create_bridge(self, api, name, vpn, **kwargs):
        api.x = SolaceXMLBuilder("Primary Cluster, Primary Bridge: %s on Primary Appliance" % name, version=kwargs.get('version'))
        api.x.create.bridge.bridge_name = name
        api.x.create.bridge.vpn_name = vpn
        api.x.create.bridge.primary
        self.cq.enqueue(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("Primary Cluster, Backup Bridge: %s on Backup Appliance" % name, version=kwargs.get('version'))
        api.x.create.bridge.bridge_name = name
        api.x.create.bridge.vpn_name = vpn
        api.x.create.bridge.backup
        self.cq.enqueue(str(api.x), backupOnly=True)

    def _create_bridge_remote_vrouter(self, api, name, vpn, virtual_router, **kwargs):
        api.x = SolaceXMLBuilder("DR Cluster, Primary Bridge v:Remote %s on Primary Appliance" % name, version=kwargs.get('version'))
        api.x.bridge.bridge_name = name
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.create.message_vpn.vpn_name = vpn
        api.x.bridge.remote.create.message_vpn.router
        api.x.bridge.remote.create.message_vpn.virtual_router_name = "v:%s" % virtual_router
        self.cq.enqueue(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("DR Cluster, Backup Bridge Remote %s on Backup Appliance" % name, version=kwargs.get('version'))
        api.x.bridge.bridge_name = name
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.create.message_vpn.vpn_name = vpn
        api.x.bridge.remote.create.message_vpn.router
        api.x.bridge.remote.create.message_vpn.virtual_router_name = "v:%s" % virtual_router
        self.cq.enqueue(str(api.x), backupOnly=True)


    def _create_bridge_remote_addr(self, api, name, vpn, backup_addr, phys_intf, **kwargs):
        api.x = SolaceXMLBuilder("Primary Cluster, Primary Bridge: %s on Remote addr: %s phys_intf: %s" % (name, backup_addr, phys_intf), version=kwargs.get('version'))
        api.x.bridge.bridge_name = name
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.create.message_vpn.vpn_name = vpn
        api.x.bridge.remote.create.message_vpn.connect_via
        api.x.bridge.remote.create.message_vpn.addr = backup_addr
        api.x.bridge.remote.create.message_vpn.interface
        api.x.bridge.remote.create.message_vpn.phys_intf = phys_intf
        self.cq.enqueue(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("Primary Cluster, Backup Bridge: %s on Remote addr: %s phys_intf: %s" % (name, backup_addr, phys_intf), version=kwargs.get('version'))
        api.x.bridge.bridge_name = name
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.create.message_vpn.vpn_name = vpn
        api.x.bridge.remote.create.message_vpn.connect_via
        api.x.bridge.remote.create.message_vpn.addr = backup_addr
        api.x.bridge.remote.create.message_vpn.interface
        api.x.bridge.remote.create.message_vpn.phys_intf = phys_intf
        self.cq.enqueue(str(api.x), backupOnly=True)
