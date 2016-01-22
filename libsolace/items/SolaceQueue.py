import logging
import libsolace
from libsolace.plugin import Plugin
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceReply import SolaceReplyHandler
from libsolace.util import get_key_from_kwargs
from libsolace.Decorators import only_on_shutdown, only_if_not_exists, only_if_exists, primary


@libsolace.plugin_registry.register
class SolaceQueue(Plugin):
    plugin_name = "SolaceQueue"

    # defaults should be provided from the settingsloader key
    defaults = {
        "retries": 0,
        "exclusive": "true",
        "queue_size": 1024,
        "consume": "all",
        "max_bind_count": 1000,
        "owner": "default"
    }

    def __init__(self, *args, **kwargs):
        """ Manage Queues

        This plugin manages SolaceQueue's within the VPN scope. It needs to be
        instantiated from the SolaceAPI.manage method. See examples

        Query mode when initialized with only the "api" kwarg.
        Create mode if initialized with vpn_name and queues dictionary.

        :Parameters:
            - `api` (`SolaceAPI`) - instance with connection to appliances
            - `vpn_name` (`string`) - VPN Name
            - `queues` (`dict`) - queues to create as from CMDBClient
            - `testmode` (`boolean`) - testmode
            - `shutdown_on_apply` (`boolean` | `char`) - shutdown 'u' = users,
                'q' = queues, 'b' = both, True = force
            - `defaults` (`libsolace.settingsloader` key) - the key for
                optionally setting the defaults to something else.

        Example:
            >>> connection = SolaceAPI("dev")
            >>> q = connection.manager("SolaceQueue")


        """

        if kwargs == {}:
            logging.info("Getter Mode")
            return

        # decorator, for caching decorator create and set this property
        # self.exists = None


        self.api = get_key_from_kwargs("api", kwargs)
        self.commands = SolaceCommandQueue(version=self.api.version)
        self.vpn_name = get_key_from_kwargs("vpn_name", kwargs, default="default")
        self.testmode = get_key_from_kwargs("testmode", kwargs, default=False)
        self.queues = get_key_from_kwargs("queues", kwargs, default={})
        self.shutdown_on_apply = get_key_from_kwargs("shutdown_on_apply", kwargs, default=False)
        self.defaults = get_key_from_kwargs('defaults', kwargs, default=self.defaults)
        self.options = None
        logging.info("Queues: %s" % self.queues)

        # backwards compatibility for None options passed to still execute "add" code
        if self.options is None:
            logging.warning(
                    "No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")

            for queue in self.queues:

                queueName = queue['name']

                queue_config = self.get_queue_config(queue, **kwargs)
                self.create_queue(queue_name=queueName, **kwargs)
                self.shutdown_egress(queue_name=queueName, **kwargs)
                if queue_config['exclusive'].lower() == "true":
                    self.exclusive(queue_name=queueName, exclusive=True, **kwargs)
                else:
                    self.exclusive(queue_name=queueName, exclusive=False, **kwargs)
                self.owner(queue_name=queueName, owner_username=queue_config['owner'], **kwargs)
                self.max_bind_count(queue_name=queueName, max_bind_count=queue_config['max_bind_count'], **kwargs)
                self.consume(queue_name=queueName, consume=queue_config['consume'], **kwargs)
                self.spool_size(queue_name=queueName, queue_size=queue_config['queue_size'], **kwargs)
                self.retries(queue_name=queueName, retries=queue_config['retries'], **kwargs)
                self.reject_on_discard(queue_name=queueName, **kwargs)
                self.enable(queue_name=queueName, **kwargs)

    def get(self, **kwargs):
        """
        Return queue config from an appliance

        Parameters
        ----------
            vpn_name : string
                VPN Name
            queue_name : string
                Queue name

        Examples:
            >>> connection = SolaceAPI("dev")
            >>> q = connection.manager("SolaceQueue").get(queue_name='*', vpn_name='dev_testvpn')

        """
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        detail = get_key_from_kwargs("detail", kwargs, default=False)

        self.api.x = SolaceXMLBuilder("Querying Queue %s" % queue_name)
        self.api.x.show.queue.name = queue_name
        self.api.x.show.queue.vpn_name = vpn_name
        if detail:
            self.api.x.show.queue.detail
        return self.api.rpc(str(self.api.x), **kwargs)

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
                            "owner": "dev_testuser"
                        }
                    }
                ]
            }

        """

        # get the queue name from the queue dictionary as passed to this method
        queue_name = get_key_from_kwargs("name", queue)

        try:
            logging.debug("Checking env overrides for queue %s" % queue['env'])
            for e in queue['env']:
                if e['name'] == self.api.environment:
                    logging.info('setting queue_config to environment %s values' % e['name'])
                    return self.apply_default_config(e['queue_config'], self.defaults)
        except:
            logging.warn("No environment overides for queue %s" % queue_name)
            pass
        try:
            return self.apply_default_config(queue['queue_config'], self.defaults)
        except:
            logging.warning("No queue_config for queue: %s found, please check site-config" % queue_name)
            raise

    def apply_default_config(self, config, default):
        """ copys keys from default dict to config dict when not present """

        logging.info("Applying default config after config")

        final_config = {}

        for k, v in default.items():
            if k in config:
                logging.info("Config key: %s to %s" % (k, v))
                final_config[k] = config[k]
            else:
                logging.info("Default config key: %s to %s" % (k, v))
                final_config[k] = v
        return final_config

    @only_if_not_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    @primary()
    def create_queue(self, **kwargs):
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Create a queue
        self.api.x = SolaceXMLBuilder("Creating Queue %s in vpn: %s" % (queue_name, vpn_name), version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.create.queue.name = queue_name
        self.commands.enqueue(self.api.x, **kwargs)
        self.set_exists(True)
        return str(self.api.x)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info')
    @only_on_shutdown('queue')
    @primary()
    def shutdown_egress(self, **kwargs):

        shutdown_on_apply = get_key_from_kwargs("shutdown_on_apply", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)

        if (shutdown_on_apply == 'b') or (shutdown_on_apply == 'q') or (shutdown_on_apply is True):
            # Lets only shutdown the egress of the queue
            self.api.x = SolaceXMLBuilder("Shutting down egress for queue:%s" % queue_name, version=self.api.version)
            self.api.x.message_spool.vpn_name = vpn_name
            self.api.x.message_spool.queue.name = queue_name
            self.api.x.message_spool.queue.shutdown.egress
            self.commands.enqueue(self.api.x, **kwargs)
            return str(self.api.x)
        else:
            logging.warning("Not disabling Queue, commands could fail since shutdown_on_apply = %s" % shutdown_on_apply)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info')
    @only_on_shutdown('queue')
    @primary()
    def exclusive(self, **kwargs):
        """
        type: exclusive bool
        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        exclusive = get_key_from_kwargs("exclusive", kwargs)

        # Default to NON Exclusive queue
        if not exclusive:
            self.api.x = SolaceXMLBuilder("Set Queue %s to Non Exclusive " % queue_name, version=self.api.version)
            self.api.x.message_spool.vpn_name = vpn_name
            self.api.x.message_spool.queue.name = queue_name
            self.api.x.message_spool.queue.access_type.non_exclusive
            self.commands.enqueue(self.api.x, **kwargs)
            return str(self.api.x)
        else:
            # Non Exclusive queue
            self.api.x = SolaceXMLBuilder("Set Queue %s to Exclusive " % queue_name, version=self.api.version)
            self.api.x.message_spool.vpn_name = vpn_name
            self.api.x.message_spool.queue.name = queue_name
            self.api.x.message_spool.queue.access_type.exclusive
            self.commands.enqueue(self.api.x, **kwargs)
            return str(self.api.x)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info')
    @only_on_shutdown('queue')
    @primary()
    def owner(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        owner = get_key_from_kwargs("owner_username", kwargs)

        if owner == "%lsVPN":
            owner = vpn_name
            logging.info("Owner being set  to VPN itself: %s" % owner)

        # Queue Owner
        self.api.x = SolaceXMLBuilder("Set Queue %s owner to %s" % (queue_name, vpn_name), version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.owner.owner = owner
        self.commands.enqueue(self.api.x, **kwargs)
        return str(self.api.x)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info')
    @primary()
    def max_bind_count(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        max_bind_count = get_key_from_kwargs("max_bind_count", kwargs)

        self.api.x = SolaceXMLBuilder("Settings Queue %s max bind count to %s" % (queue_name, str(max_bind_count)),
                                      version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.max_bind_count.value = max_bind_count
        self.commands.enqueue(self.api.x, **kwargs)
        return str(self.api.x)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info')
    @only_on_shutdown('queue')
    @primary()
    def consume(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        consume = get_key_from_kwargs("consume", kwargs)

        # Open Access
        self.api.x = SolaceXMLBuilder("Settings Queue %s Permission to Consume" % queue_name, version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        if consume == "all":
            self.api.x.message_spool.queue.permission.all
        self.api.x.message_spool.queue.permission.consume
        self.commands.enqueue(self.api.x, **kwargs)
        return str(self.api.x)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info')
    @primary()
    def spool_size(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        queue_size = get_key_from_kwargs("queue_size", kwargs)

        # Configure Queue Spool Usage
        self.api.x = SolaceXMLBuilder("Set Queue %s spool size: %s" % (queue_name, queue_size),
                                      version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.max_spool_usage.size = queue_size
        self.commands.enqueue(self.api.x, **kwargs)
        return str(self.api.x)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info')
    @primary()
    def retries(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        retries = get_key_from_kwargs("retries", kwargs, default=0)

        self.api.x = SolaceXMLBuilder("Tuning max-redelivery retries for %s to %s" % (queue_name, retries),
                                      version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.max_redelivery.value = retries
        self.commands.enqueue(self.api.x, **kwargs)
        return str(self.api.x)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info')
    @primary()
    def enable(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)

        # Enable the Queue
        self.api.x = SolaceXMLBuilder("Enabling Queue %s" % queue_name, version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.no.shutdown.full
        self.commands.enqueue(self.api.x, **kwargs)
        return str(self.api.x)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info')
    @primary()
    def reject_on_discard(self, **kwargs):

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)

        self.api.x = SolaceXMLBuilder("Setting Queue to Reject Drops", version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.reject_msg_to_sender_on_discard
        self.commands.enqueue(self.api.x, **kwargs)
        return str(self.api.x)
