import logging

import libsolace
from libsolace import Plugin
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceAPI import SolaceAPI
from libsolace.items.SolaceQueue import SolaceQueue


@libsolace.plugin_registry.register
class SolaceBridge(Plugin):
    """ Construct a bridge between two appliance clusters to link specific VPN's. This Plugin is still being developed,
    and is NOT ready for production. """

    def __init__(self, testmode=True, shutdown_on_apply=False, options=None, version=None, **kwargs):
        """ Init user object

        :type testmode: boolean
        :type shutdown_on_apply: boolean
        :type options: OptionParser
        :type version: string

        """
        logging.debug("options: %s" % options)
        self.cq = SolaceCommandQueue(version=version)

        self.primaryCluster = SolaceAPI(options.primary, testmode=testmode, version=version)
        self.drCluster = SolaceAPI(options.backup, testmode=testmode, version=version)
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

            # create remote username on primary cluster bridge
            self._bridge_username_addr(self.primaryCluster, primaryBridgeName, vpn,
                                       options.backup_addr, options.primary_phys_intf, options.username,
                                       options.password, version=version)

            # create remote username on backup cluster bridge
            self._bridge_username_vrouter(self.drCluster, backupBridgeName, vpn,
                                          options.primary_cluster_primary_node_name, options.username,
                                          options.password, version=version)

            # enable all bridges
            self._bridge_enable(self.primaryCluster, primaryBridgeName, vpn, version=version)
            self._bridge_enable(self.drCluster, backupBridgeName, vpn, version=version)

            # enable all remotes
            self._bridge_enable_remote_addr(self.primaryCluster, primaryBridgeName, vpn,
                                            options.backup_addr, options.primary_phys_intf, version=version)
            self._bridge_enable_remote_vrouter(self.drCluster, backupBridgeName, vpn,
                                               options.primary_cluster_primary_node_name, version=version)

            # create bridge internal queues
            self._bridge_create_queue(self.primaryCluster, options.queue, vpn, options.username, version=version)
            self._bridge_create_queue(self.drCluster, options.queue, vpn, options.username, version=version)

            # set remote internal queues
            self._bridge_set_remote_queue_addr(self.primaryCluster, primaryBridgeName, vpn,
                                               options.backup_addr, options.primary_phys_intf, options.queue,
                                               version=version)

            self._bridge_set_remote_queue_vrouter(self.drCluster, backupBridgeName, vpn,
                                                  options.primary_cluster_primary_node_name, options.queue,
                                                  version=version)

    def _create_bridge(self, api, bridgeName, vpn, **kwargs):
        api.x = SolaceXMLBuilder("%s create primary bridge: %s on primary appliance" % (api.primaryRouter, bridgeName),
                                 version=api.version)
        api.x.create.bridge.bridge_name = bridgeName
        api.x.create.bridge.vpn_name = vpn
        api.x.create.bridge.primary
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("%s create backup bridge: %s on backup appliance" % (api.backupRouter, bridgeName),
                                 version=api.version)
        api.x.create.bridge.bridge_name = bridgeName
        api.x.create.bridge.vpn_name = vpn
        api.x.create.bridge.backup
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _create_bridge_remote_vrouter(self, api, bridgeName, vpn, virtual_router, **kwargs):
        api.x = SolaceXMLBuilder("%s configure primary bridge: %s vrouter: %s on primary appliance" % (
        api.primaryRouter, bridgeName, virtual_router), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.create.message_vpn.vpn_name = vpn
        api.x.bridge.remote.create.message_vpn.router
        api.x.bridge.remote.create.message_vpn.virtual_router_name = "v:%s" % virtual_router
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("%s configure backup bridge: %s vrouter: %s on backup appliance" % (
        api.backupRouter, bridgeName, virtual_router), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.create.message_vpn.vpn_name = vpn
        api.x.bridge.remote.create.message_vpn.router
        api.x.bridge.remote.create.message_vpn.virtual_router_name = "v:%s" % virtual_router
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _create_bridge_remote_addr(self, api, bridgeName, vpn, backup_addr, phys_intf, **kwargs):
        api.x = SolaceXMLBuilder(
            "%s configure primary bridge: %s remote addr: %s phys_intf: %s on primary appliance" % (
            api.primaryRouter, bridgeName, backup_addr, phys_intf), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.create.message_vpn.vpn_name = vpn
        api.x.bridge.remote.create.message_vpn.connect_via
        api.x.bridge.remote.create.message_vpn.addr = backup_addr
        api.x.bridge.remote.create.message_vpn.interface
        api.x.bridge.remote.create.message_vpn.phys_intf = phys_intf
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("%s configure backup bridge: %s remote addr: %s phys_intf: %s on backup appliance" % (
        api.backupRouter, bridgeName, backup_addr, phys_intf), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.create.message_vpn.vpn_name = vpn
        api.x.bridge.remote.create.message_vpn.connect_via
        api.x.bridge.remote.create.message_vpn.addr = backup_addr
        api.x.bridge.remote.create.message_vpn.interface
        api.x.bridge.remote.create.message_vpn.phys_intf = phys_intf
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _bridge_username_addr(self, api, bridgeName, vpn, backup_addr, phys_intf, username, password, **kwargs):
        api.x = SolaceXMLBuilder("%s primary bridge: %s remote username: %s on primary appliance" % (
        api.primaryRouter, bridgeName, username), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.connect_via
        api.x.bridge.remote.message_vpn.addr = backup_addr
        api.x.bridge.remote.message_vpn.interface
        api.x.bridge.remote.message_vpn.phys_intf = phys_intf
        api.x.bridge.remote.message_vpn.client_username.name = username
        api.x.bridge.remote.message_vpn.client_username.password = password
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder(
            "%s backup bridge: %s remote username: %s on backup appliance" % (api.backupRouter, bridgeName, username),
            version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.connect_via
        api.x.bridge.remote.message_vpn.addr = backup_addr
        api.x.bridge.remote.message_vpn.interface
        api.x.bridge.remote.message_vpn.phys_intf = phys_intf
        api.x.bridge.remote.message_vpn.client_username.name = username
        api.x.bridge.remote.message_vpn.client_username.password = password
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _bridge_username_vrouter(self, api, bridgeName, vpn, vrouter, username, password, **kwargs):
        api.x = SolaceXMLBuilder("%s primary bridge: %s remote username: %s on primary appliance" % (
        api.primaryRouter, bridgeName, username), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.router
        api.x.bridge.remote.message_vpn.virtual_router_name = "v:%s" % vrouter
        api.x.bridge.remote.message_vpn.client_username.name = username
        api.x.bridge.remote.message_vpn.client_username.password = password
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder(
            "%s backup bridge: %s remote username: %s on backup appliance" % (api.backupRouter, bridgeName, username),
            version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.router
        api.x.bridge.remote.message_vpn.virtual_router_name = "v:%s" % vrouter
        api.x.bridge.remote.message_vpn.client_username.name = username
        api.x.bridge.remote.message_vpn.client_username.password = password
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _bridge_enable(self, api, bridgeName, vpn, **kwargs):
        api.x = SolaceXMLBuilder(
            "%s enable bridge: %s for vpn: %s on primary appliance" % (api.primaryRouter, bridgeName, vpn),
            version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.no.shutdown
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder(
            "%s enable bridge: %s for vpn: %s on backup appliance" % (api.backupRouter, bridgeName, vpn),
            version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.no.shutdown
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _bridge_enable_remote_addr(self, api, bridgeName, vpn, backup_addr, phys_intf, **kwargs):
        api.x = SolaceXMLBuilder("%s enable primary bridge: %s remote addr: %s phys_intf: %s on primary appliance" % (
        api.primaryRouter, bridgeName, backup_addr, phys_intf), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.connect_via
        api.x.bridge.remote.message_vpn.addr = backup_addr
        api.x.bridge.remote.message_vpn.interface
        api.x.bridge.remote.message_vpn.phys_intf = phys_intf
        api.x.bridge.remote.message_vpn.no.shutdown
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("%s enable backup bridge: %s remote addr: %s phys_intf: %s on backup appliance" % (
        api.backupRouter, bridgeName, backup_addr, phys_intf), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.connect_via
        api.x.bridge.remote.message_vpn.addr = backup_addr
        api.x.bridge.remote.message_vpn.interface
        api.x.bridge.remote.message_vpn.phys_intf = phys_intf
        api.x.bridge.remote.message_vpn.no.shutdown
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _bridge_enable_remote_vrouter(self, api, bridgeName, vpn, vrouter, **kwargs):
        api.x = SolaceXMLBuilder("%s enable primary bridge: %s vrouter: %s" % (api.primaryRouter, bridgeName, vrouter),
                                 version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.router
        api.x.bridge.remote.message_vpn.virtual_router_name = "v:%s" % vrouter
        api.x.bridge.remote.message_vpn.no.shutdown
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("%s enable backup bridge: %s vrouter: %s" % (api.backupRouter, bridgeName, vrouter),
                                 version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.router
        api.x.bridge.remote.message_vpn.virtual_router_name = "v:%s" % vrouter
        api.x.bridge.remote.message_vpn.no.shutdown
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _bridge_disable_remote_addr(self, api, bridgeName, vpn, backup_addr, phys_intf, **kwargs):
        api.x = SolaceXMLBuilder("%s disable primary bridge: %s remote addr: %s phys_intf: %s on primary appliance" % (
        api.primaryRouter, bridgeName, backup_addr, phys_intf), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.connect_via
        api.x.bridge.remote.message_vpn.addr = backup_addr
        api.x.bridge.remote.message_vpn.interface
        api.x.bridge.remote.message_vpn.phys_intf = phys_intf
        api.x.bridge.remote.message_vpn.shutdown
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("%s disable backup bridge: %s remote addr: %s phys_intf: %s on backup appliance" % (
        api.backupRouter, bridgeName, backup_addr, phys_intf), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.connect_via
        api.x.bridge.remote.message_vpn.addr = backup_addr
        api.x.bridge.remote.message_vpn.interface
        api.x.bridge.remote.message_vpn.phys_intf = phys_intf
        api.x.bridge.remote.message_vpn.shutdown
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _bridge_disable_remote_vrouter(self, api, bridgeName, vpn, vrouter, **kwargs):
        api.x = SolaceXMLBuilder("%s enable primary bridge: %s vrouter: %s" % (api.primaryRouter, bridgeName, vrouter),
                                 version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.router
        api.x.bridge.remote.message_vpn.virtual_router_name = "v:%s" % vrouter
        api.x.bridge.remote.message_vpn.shutdown
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder("%s enable backup bridge: %s vrouter: %s" % (api.backupRouter, bridgeName, vrouter),
                                 version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.router
        api.x.bridge.remote.message_vpn.virtual_router_name = "v:%s" % vrouter
        api.x.bridge.remote.message_vpn.shutdown
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _bridge_create_queue(self, api, queueName, vpnName, username, **kwargs):
        logging.info("%s:%s creating bridge queue: %s with owner username: %s" % (
        api.primaryRouter, api.backupRouter, queueName, username))
        queue1 = {}
        queue1['queue_config'] = {}
        queue1['queue_config']["exclusive"] = "true"
        queue1['queue_config']["queue_size"] = "4096"
        queue1['queue_config']["retries"] = 0
        queue1["name"] = queueName

        vpnd = {}
        vpnd['vpn_name'] = vpnName
        vpnd['owner_username'] = username

        q1 = SolaceQueue(api, vpnd, [queue1])

        for c in q1.queue.commands:
            api.cq.enqueue(str(api.x))

    def _bridge_set_remote_queue_addr(self, api, bridgeName, vpn, backup_addr, phys_intf, queueName, **kwargs):
        api.x = SolaceXMLBuilder("%s primary bridge: %s set remote queue: %s on primary appliance" % (
        api.primaryRouter, bridgeName, queueName), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.connect_via
        api.x.bridge.remote.message_vpn.addr = backup_addr
        api.x.bridge.remote.message_vpn.interface
        api.x.bridge.remote.message_vpn.phys_intf = phys_intf
        api.x.bridge.remote.message_vpn.message_spool.queue.name = queueName
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder(
            "%s backup bridge: %s set remote queue: %s on backup appliance" % (api.backupRouter, bridgeName, queueName),
            version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.connect_via
        api.x.bridge.remote.message_vpn.addr = backup_addr
        api.x.bridge.remote.message_vpn.interface
        api.x.bridge.remote.message_vpn.phys_intf = phys_intf
        api.x.bridge.remote.message_vpn.message_spool.queue.name = queueName
        api.cq.enqueueV2(str(api.x), backupOnly=True)

    def _bridge_set_remote_queue_vrouter(self, api, bridgeName, vpn, vrouter, queueName, **kwargs):
        api.x = SolaceXMLBuilder("%s primary bridge: %s set remote queue: %s on primary appliance" % (
        api.primaryRouter, bridgeName, queueName), version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.primary
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.router
        api.x.bridge.remote.message_vpn.virtual_router_name = "v:%s" % vrouter
        api.x.bridge.remote.message_vpn.message_spool.queue.name = queueName
        api.cq.enqueueV2(str(api.x), primaryOnly=True)

        api.x = SolaceXMLBuilder(
            "%s backup bridge: %s set remote queue: %s on backup appliance" % (api.backupRouter, bridgeName, queueName),
            version=api.version)
        api.x.bridge.bridge_name = bridgeName
        api.x.bridge.vpn_name = vpn
        api.x.bridge.backup
        api.x.bridge.remote.message_vpn.vpn_name = vpn
        api.x.bridge.remote.message_vpn.router
        api.x.bridge.remote.message_vpn.virtual_router_name = "v:%s" % vrouter
        api.x.bridge.remote.message_vpn.message_spool.queue.name = queueName
        api.cq.enqueueV2(str(api.x), backupOnly=True)
