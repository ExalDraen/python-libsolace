import logging
import libsolace
from libsolace.plugin import Plugin
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder

@libsolace.plugin_registry.register
class SolaceQueue(Plugin):

    plugin_name = "SolaceQueue"

    queue_defaults = {
        "retries": 0,
        "exclusive": "true",
        "queue_size": 1024,
        "consume": "all",
        "max_bind_count": 1000,
        "owner": "%lsVPN"
    }

    def init(self, **kwargs):
        """ Manage Queues

        This plugin manages SolaceQueue's within the VPN scope. It needs to be
        instantiated from a plugin manager.

        Query mode when initialized with only the "api" kwarg.
        Create mode if initialized with vpn_name and queues dictionary.

        :parameter api: SolaceAPI
        :parameter vpn_name: str
        :parameter queues: dict as from CMDBClient
        :parameter testmode: bool
        :parameter shutdown_on_apply: bool / char b / chart q

        Example:
            >>> connection = SolaceAPI("dev")
            >>> q = connection.manager("SolaceQueue")


        """

        self.api = kwargs.get("api")
        self.commands = SolaceCommandQueue(version = self.api.version)

        if not "vpn_name" in kwargs:
            logging.info("Query mode because vpn_name not in kwargs")
        else:
            self.vpn_name = kwargs.get("vpn_name")
            self.testmode = kwargs.get("testmode")
            self.queues = kwargs.get("queues")
            self.shutdown_on_apply = kwargs.get("shutdown_on_apply")
            self.options = None
            logging.info("Queues: %s" % self.queues)

            # backwards compatibility for None options passed to still execute "add" code
            if self.options == None:
                logging.warning("No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")

                for queue in self.queues:

                    queueName = queue['name']

                    queue_config = self.get_queue_config(queue, **kwargs)
                    self.create_queue(queue_name = queueName, **kwargs)
                    self.shutdown_egress(queue_name = queueName, **kwargs)
                    if queue_config['exclusive'].lower() == "true":
                        self.exclusive(queue_name = queueName, exclusive=True, **kwargs)
                    else:
                        self.exclusive(queue_name = queueName, exclusive=False, **kwargs)
                    self.owner(queue_name = queueName, owner_username = queue_config['owner'], **kwargs)
                    self.max_bind_count(queue_name = queueName, max_bind_count = queue_config['max_bind_count'], **kwargs)
                    self.consume(queue_name = queueName, consume = queue_config['consume'], **kwargs)
                    self.spool_size(queue_name = queueName, queue_size = queue_config['queue_size'], **kwargs)
                    self.retries(queue_name = queueName, retries = queue_config['retries'], **kwargs)
                    self.reject_on_discard(queue_name = queueName, **kwargs)
                    self.enable(queue_name = queueName, **kwargs)


    def get_queue_config(self, queue, **kwargs):
        """ Returns a queue config for the queue and overrides where neccesary

        :param queue: single queue dictionary e.g.
            {
                "name": "foo",
                "env": [
                    "qa1": {
                        "queue_config": {
                            "retries": 0,
                            "exclusive": "false",
                            "queue_size": 1024,
                            "consume": "all",
                            "max_bind_count": 1000,
                            "owner": "%slsVPN"
                        }
                    }
                ]
            }

        """

        queue_name = kwargs.get("queue_name")

        try:
            logging.debug("Checking env overrides for queue %s" % queue['env'])
            for e in queue['env']:
                if e['name'] == self.api.environment:
                    logging.info('setting queue_config to environment %s values' % e['name'] )
                    return self.apply_default_config(e['queue_config'], self.queue_defaults)
        except:
            logging.warn("No environment overides for queue %s" % queue_name)
            pass
        try:
            return self.apply_default_config(queue['queue_config'], self.queue_defaults)
        except:
            logging.warning("No queue_config for queue: %s found, please check site-config" % queue_name)
            raise

    def apply_default_config(self, config, default):
        """ copys keys from default dict to config dict when not present """

        logging.info("Applying default config after config")

        final_config = {}

        for k,v in default.items():
            if k in config:
                logging.info("Config key: %s to %s" % (k,v))
                final_config[k] = config[k]
            else:
                logging.info("Default config key: %s to %s" % (k,v))
                final_config[k] = v
        return final_config


    def create_queue(self, **kwargs):
        queue_name = kwargs.get("gueue_name")
        vpn_name = kwargs.get("vpn_name")

        # Create a queue
        self.api.x = SolaceXMLBuilder("Creating Queue %s in vpn: %s" % (queue_name, vpn_name), version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.create.queue.name = queue_name
        self.commands.enqueue(self.api.x)
        return self.api.x

    def shutdown_egress(self, **kwargs):

        shutdown_on_apply = kwargs.get("shutdown_on_apply")
        vpn_name = kwargs.get("vpn_name")
        queue_name = kwargs.get("queue_name")

        if ( shutdown_on_apply=='b' ) or ( shutdown_on_apply == 'q' ) or ( shutdown_on_apply == True):
            # Lets only shutdown the egress of the queue
            self.api.x = SolaceXMLBuilder("Shutting down egress for queue:%s" % queue_name, version = self.api.version)
            self.api.x.message_spool.vpn_name = vpn_name
            self.api.x.message_spool.queue.name = queue_name
            self.api.x.message_spool.queue.shutdown.egress
            self.commands.enqueue(self.api.x)
        else:
            logging.warning("Not disabling Queue, commands could fail since shutdown_on_apply = %s" % self.shutdown_on_apply)

    def exclusive(self, **kwargs):
        """
        type: exclusive bool
        """

        vpn_name = kwargs.get("vpn_name")
        queue_name = kwargs.get("queue_name")
        exclusive = kwargs.get("exclusive")

        # Default to NON Exclusive queue
        if not exclusive:
            self.api.x = SolaceXMLBuilder("Set Queue %s to Non Exclusive " % queue_name , version=self.api.version)
            self.api.x.message_spool.vpn_name = vpn_name
            self.api.x.message_spool.queue.name = queue_name
            self.api.x.message_spool.queue.access_type.non_exclusive
            self.commands.enqueue(self.api.x)
        else:
            # Non Exclusive queue
            self.api.x = SolaceXMLBuilder("Set Queue %s to Exclusive " % queue_name , version=self.api.version)
            self.api.x.message_spool.vpn_name = vpn_name
            self.api.x.message_spool.queue.name = queue_name
            self.api.x.message_spool.queue.access_type.exclusive
            self.commands.enqueue(self.api.x)

    def owner(self, **kwargs):

        vpn_name = kwargs.get("vpn_name")
        queue_name = kwargs.get("queue_name")
        owner = kwargs.get("owner_username")

        if owner == "%lsVPN":
            logging.info("Owner being set to VPN")
            owner = vpn_name

        # Queue Owner
        self.api.x = SolaceXMLBuilder("Set Queue %s owner to %s" % (queue_name, vpn_name), version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.owner.owner = owner
        self.commands.enqueue(self.api.x)

    def max_bind_count(self, **kwargs):

        vpn_name = kwargs.get("vpn_name")
        queue_name = kwargs.get("queue_name")
        max_bind_count = kwargs.get("max_bind_count")

        self.api.x = SolaceXMLBuilder("Settings Queue %s max bind count to %s" % (queue_name, str(max_bind_count)), version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.max_bind_count.value = max_bind_count
        self.commands.enqueue(self.api.x)

    def consume(self, **kwargs):

        vpn_name = kwargs.get("vpn_name")
        queue_name = kwargs.get("queue_name")
        consume = kwargs.get("consume")

        # Open Access
        self.api.x = SolaceXMLBuilder("Settings Queue %s Permission to Consume" % queue_name, version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        if consume == "all":
            self.api.x.message_spool.queue.permission.all
        self.api.x.message_spool.queue.permission.consume
        self.commands.enqueue(self.api.x)

    def spool_size(self, **kwargs):

        vpn_name = kwargs.get("vpn_name")
        queue_name = kwargs.get("queue_name")
        queue_size = kwargs.get("queue_size")

        # Configure Queue Spool Usage
        self.api.x = SolaceXMLBuilder("Set Queue %s spool size: %s" % (queue_name, queue_size), version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.max_spool_usage.size = queue_size
        self.commands.enqueue(self.api.x)

    def retries(self, **kwargs):

        vpn_name = kwargs.get("vpn_name")
        queue_name = kwargs.get("queue_name")
        retries = kwargs.get("retries", 0)

        self.api.x = SolaceXMLBuilder("Tuning max-redelivery retries for %s to %s" % (queue_name, retries), version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.max_redelivery.value = retries
        self.commands.enqueue(self.api.x)

    def enable(self, **kwargs):

        vpn_name = kwargs.get("vpn_name")
        queue_name = kwargs.get("queue_name")

        # Enable the Queue
        self.api.x = SolaceXMLBuilder("Enabling Queue %s" % queue_name, version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.no.shutdown.full
        self.commands.enqueue(self.api.x)

    def reject_on_discard(self, **kwargs):

        vpn_name = kwargs.get("vpn_name")
        queue_name = kwargs.get("queue_name")

        self.api.x = SolaceXMLBuilder("Setting Queue to Reject Drops", version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.reject_msg_to_sender_on_discard
        self.commands.enqueue(self.api.x)
