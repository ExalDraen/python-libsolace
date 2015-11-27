import logging
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder

class SolaceQueue:
    """ Construct Queues """
    def __init__(self, environment, vpn, queues, testmode=False, shutdown_on_apply=False, options=None, version="soltr/6_0"):
        """ Creates queue commands

        :type environment: str
        :type vpn: SolaceVPN
        :type queues: dict

        :param environment: environment name
        :param vpn: Datanode instance
        :param queues: queues to create:

        """
        self.queue = SolaceCommandQueue(version=version)
        self.environment = environment
        self.vpn = vpn
        self.testmode = testmode
        self.queues = queues # dictionary of queues to create
        self.shutdown_on_apply = shutdown_on_apply

        logging.info("Queues: %s" % self.queues)
        # backwards compatibility for None options passed to still execute "add" code
        if options == None:
            logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            self._create_queue()

    def _get_queue_confg(self, queue):
        """ Returns a queue config for the queue and overrides where neccesary

        :type queue: libsolace.gfmisc.DataNode
        :param queue: single queue datanode object

        """
        try:
            logging.debug("Checking env overrides for queue %s" % queue['env'])
            for e in queue['env']:
                if e['name'] == self.environment:
                    logging.info('setting queue_config to environment %s values' % e['name'] )
                    return e['queue_config']
        except:
            logging.warn("No environment overides for queue %s" % queue['name'])
            pass
        try:
            return queue['queue_config']
        except:
            logging.warning("No queue_config for queue: %s found, please check site-config" % queue['name'])
            raise

    def _create_queue(self):
        logging.debug("Building queues in %s" % self.queues)
        for queue in self.queues:
            logging.info("Preparing to build queue: %s" % queue)
            queue_config = self._get_queue_confg(queue)
            # Create some queues now
            cmd = SolaceXMLBuilder("Creating Queue %s" % queue['name'])
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.create.queue.name=queue['name']
            self.queue.enqueue(cmd)

            if ( self.shutdown_on_apply=='b' ) or ( self.shutdown_on_apply == 'q' ) or ( self.shutdown_on_apply == True):
                # Lets only shutdown the egress of the queue
                cmd = SolaceXMLBuilder("Shutting down egress for queue:%s" % queue['name'])
                cmd.message_spool.vpn_name = self.vpn.vpn_name
                cmd.message_spool.queue.name = queue['name']
                cmd.message_spool.queue.shutdown.egress
                self.queue.enqueue(cmd)
            else:
                logging.warning("Not disabling Queue, commands could fail since shutdown_on_apply = %s" % self.shutdown_on_apply)

            # Default to NON Exclusive queue
            cmd = SolaceXMLBuilder("Set Queue %s to Non Exclusive " % queue['name'] )
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue['name']
            cmd.message_spool.queue.access_type.non_exclusive
            self.queue.enqueue(cmd)

            if queue_config['exclusive'] == "true":
                # Non Exclusive queue
                cmd = SolaceXMLBuilder("Set Queue %s to Exclusive " % queue['name'] )
                cmd.message_spool.vpn_name = self.vpn.vpn_name
                cmd.message_spool.queue.name = queue['name']
                cmd.message_spool.queue.access_type.exclusive
                self.queue.enqueue(cmd)

            # Queue Owner
            cmd = SolaceXMLBuilder("Set Queue %s owner to %s" % (queue['name'], self.vpn.vpn_name))
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue['name']
            cmd.message_spool.queue.owner.owner = self.vpn.owner_username
            self.queue.enqueue(cmd)

            cmd = SolaceXMLBuilder("Settings Queue %s max bind count to %s" % (queue['name'], str(1000)))
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue['name']
            cmd.message_spool.queue.max_bind_count.value = 1000
            self.queue.enqueue(cmd)

            # Open Access
            cmd = SolaceXMLBuilder("Settings Queue %s Permission to Consume" % queue['name'])
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue['name']
            cmd.message_spool.queue.permission.all
            cmd.message_spool.queue.permission.consume
            self.queue.enqueue(cmd)

            # Configure Queue Spool Usage
            cmd = SolaceXMLBuilder("Set Queue %s spool size: %s" % (queue['name'], queue_config['queue_size']))
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue['name']
            cmd.message_spool.queue.max_spool_usage.size = queue_config['queue_size']
            self.queue.enqueue(cmd)

            if queue_config['retries']:
                cmd = SolaceXMLBuilder("Tuning max-redelivery retries for %s to %s" % (queue['name'], queue_config.retries))
                cmd.message_spool.vpn_name = self.vpn.vpn_name
                cmd.message_spool.queue.name = queue['name']
                cmd.message_spool.queue.max_redelivery.value = queue_config['retries']
                self.queue.enqueue(cmd)
            else:
                cmd = SolaceXMLBuilder("Tuning max-redelivery retries for %s to infinite" % queue['name'])
                cmd.message_spool.vpn_name = self.vpn.vpn_name
                cmd.message_spool.queue.name = queue['name']
                cmd.message_spool.queue.max_redelivery.value = 0
                self.queue.enqueue(cmd)

            # Enable the Queue
            cmd = SolaceXMLBuilder("Enabling Queue %s" % queue['name'])
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue['name']
            cmd.message_spool.queue.no.shutdown.full
            self.queue.enqueue(cmd)

            # Queue Reject on Drop
            """
            <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
              <message-spool>
                <vpn-name>prod_testvpn</vpn-name>
                <queue>
                  <name>testqueue1</name>
                  <reject-msg-to-sender-on-discard/>
                </queue>
              </message-spool>
            </rpc>
            """
            cmd = SolaceXMLBuilder("Setting Queue to Reject Drops")
            cmd.message_spool.vpn_name = self.vpn.vpn_name
            cmd.message_spool.queue.name = queue['name']
            cmd.message_spool.queue.reject_msg_to_sender_on_discard
            self.queue.enqueue(cmd)
