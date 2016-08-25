import logging

import libsolace
from libsolace.Decorators import only_on_shutdown, only_if_not_exists, only_if_exists, primary, deprecation_warning
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.plugin import Plugin, PluginResponse
from libsolace.util import get_key_from_kwargs


@libsolace.plugin_registry.register
class SolaceQueue(Plugin):
    """Manage a Solace Queue

    Description
    ===========
        This plugin manages Queues within Solace. Typically you should invoke this plugin via L{SolaceAPI.SolaceAPI}.

        Please see L{plugin.Plugin} for how plugins are instantiated and used.
    """

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
        """
        :param api: The instance of SolaceAPI if not called from SolaceAPI.manage
        :param queue_name: the queue name in Query mode
        :param queues: list of queue dictionaries with keys: name, queue_config
        :param vpn_name: name of the VPN to scope the ACL to
        :param defaults: dictionary of queue properties, see `defaults` in SolaceQueue class
        :type api: SolaceAPI
        :type queue_name: str
        :type vpn_name: str
        :type defaults: dict
        :returns: instance with batch requests on SolaceACLProfile.commands.commands
        :rtype: SolaceClientProfile

        Example:

        >>> api = SolaceAPI("dev")
        >>> sq = api.manage("SolaceQueue")
        >>> dict_queue = sq.get(vpn_name="dev_testvpn", queue_name="testqueue1")
        >>> api.rpc(sq.max_bind_count(vpn_name="dev_testvpn", queue_name="testqueue1", max_bind_count=10))

        """
        self.api = get_key_from_kwargs("api", kwargs)
        self.commands = SolaceCommandQueue(version=self.api.version)
        kwargs.pop("api")

        if kwargs == {}:
            logging.info("Query Mode")
            return

        logging.info("Provision mode: %s" % kwargs)
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
        """Fetch a queue from the appliance

        :type queue_name: str
        :type vpn_name: str
        :param queue_name: Queue name or filter
        :param vpn_name: name of the VPN
        :rtype: plugin.PluginResponse
        :returns: the queue(s)

        Examples:

        >>> api = SolaceAPI("dev")
        >>> list_queues = api.manage("SolaceQueue").get(queue_name='*', vpn_name='dev_testvpn')

        """
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        detail = get_key_from_kwargs("detail", kwargs, default=False)

        # if this request is not specifically targeted at the backup, default to primary
        if get_key_from_kwargs("backupOnly", kwargs, default=False) is False:
            kwargs["primaryOnly"] = True

        self.api.x = SolaceXMLBuilder("Querying Queue %s" % queue_name, version=self.api.version)
        self.api.x.show.queue.name = queue_name
        self.api.x.show.queue.vpn_name = vpn_name
        if detail:
            self.api.x.show.queue.detail
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return self.api.rpc(PluginResponse(str(self.api.x), **kwargs))

    def get_queue_config(self, queue, **kwargs):
        """ Returns a queue config for the queue and overrides where neccessary

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
                    return self.__apply_default_config__(e['queue_config'], self.defaults)
        except:
            logging.warn("No environment overrides for queue %s" % queue_name)
            pass
        try:
            return self.__apply_default_config__(queue['queue_config'], self.defaults)
        except:
            logging.warning("No queue_config for queue: %s found, please check site-config" % queue_name)
            raise


    def __apply_default_config__(self, config, default):
        """ copys keys from default dict to config dict when not present """

        logging.info("Applying default config after config")

        final_config = {}

        for k, v in default.items():
            if k in config:
                logging.info("Using environment config key: %s to %s" % (k, config[k]))
                final_config[k] = config[k]
            else:
                logging.info("Using default config key: %s to %s" % (k, v))
                final_config[k] = v
        return final_config

    # perform the if_exists on the primary only
    @only_if_not_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    @primary()
    def create_queue(self, **kwargs):
        """Create a queue / endpoint only if it doesnt exist.

        :param queue_name: the queue name
        :param vpn_name: the vpn name
        :type queue_name: str
        :type vpn_name: str
        :type: plugin.PluginResponse
        :returns: single SEMP request

        Example 1: Create Request, then Execute

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").create_queue(vpn_name="dev_testvpn", queue_name="my_test_queue")
        >>> # response = api.rpc(request)

        """
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        # Create a queue
        self.api.x = SolaceXMLBuilder("Creating Queue %s in vpn: %s" % (queue_name, vpn_name), version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.create.queue.name = queue_name
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        self.exists = True
        return PluginResponse(str(self.api.x), **kwargs)

    # perform the if_exists on the primary only
    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    # @only_on_shutdown('queue')
    @primary()
    def shutdown_egress(self, **kwargs):
        """Shutdown egress for a queue

        :param shutdown_on_apply: is shutdown permitted boolean or char
        :param vpn_name: name of the vpn
        :param queue_name: name of the queue
        :type shutdown_on_apply: char or bool
        :type queue_name: str
        :type vpn_name: str
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example 1: One Shot

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").shutdown_egress(shutdown_on_apply=True, vpn_name="dev_testvpn", queue_name="testqueue1")
        >>> # response = api.rpc(request)

        Example 2: Create Request, then Execute

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").shutdown_egress(shutdown_on_apply=True, vpn_name="dev_testvpn", queue_name="testqueue1")
        >>> # response = api.rpc(request)

        """

        shutdown_on_apply = get_key_from_kwargs("shutdown_on_apply", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)

        if (shutdown_on_apply == 'b') or (shutdown_on_apply == 'q') or (shutdown_on_apply is True):
            # Lets only shutdown the egress of the queue
            self.api.x = SolaceXMLBuilder("Shutting down egress for queue:%s" % queue_name, version=self.api.version)
            self.api.x.message_spool.vpn_name = vpn_name
            self.api.x.message_spool.queue.name = queue_name
            self.api.x.message_spool.queue.shutdown.egress
            self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
            return PluginResponse(str(self.api.x), **kwargs)
        else:
            logging.warning("Not disabling Queue, commands could fail since shutdown_on_apply = %s" % shutdown_on_apply)

    # perform the if_exists on the primary only
    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    # @only_on_shutdown('queue')
    @primary()
    def shutdown_ingress(self, **kwargs):
        """Shutdown the ingress of a queue

        :param shutdown_on_apply: is shutdown permitted boolean or char
        :param vpn_name: name of the vpn
        :param queue_name: name of the queue
        :type shutdown_on_apply: char or bool
        :type queue_name: str
        :type vpn_name: str
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example 1: Instant Execution:

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").shutdown_ingress(shutdown_on_apply=True, vpn_name="dev_testvpn", queue_name="testqueue1")
        >>> # response = api.rpc(request)


        Example 2: Create Request, then Execute

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").shutdown_ingress(shutdown_on_apply=True, vpn_name="dev_testvpn", queue_name="testqueue1")
        >>> # api.rpc(request)

        """

        shutdown_on_apply = get_key_from_kwargs("shutdown_on_apply", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)

        if (shutdown_on_apply == 'b') or (shutdown_on_apply == 'q') or (shutdown_on_apply is True):
            # Lets only shutdown the egress of the queue
            self.api.x = SolaceXMLBuilder("Shutting down egress for queue:%s" % queue_name, version=self.api.version)
            self.api.x.message_spool.vpn_name = vpn_name
            self.api.x.message_spool.queue.name = queue_name
            self.api.x.message_spool.queue.shutdown.ingress
            self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
            return PluginResponse(str(self.api.x), **kwargs)
        else:
            logging.warning("Not disabling Queue, commands could fail since shutdown_on_apply = %s" % shutdown_on_apply)

    # perform the if_exists on the primary only
    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    # @only_on_shutdown('queue')
    @primary()
    def exclusive(self, **kwargs):
        """Set queue exclusivity

        :param vpn_name: the name of the vpn
        :param queue_name: the queue name
        :param exclusive: state
        :type vpn_name: str
        :type queue_name: str
        :type exclusive: bool
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example: Shutdown, Set Exclusive, Start

        >>> api = SolaceAPI("dev")
        >>> requests = []
        >>> requests.append(api.manage("SolaceQueue").shutdown_ingress(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True))
        >>> requests.append(api.manage("SolaceQueue").exclusive(queue_name="testqueue1", vpn_name="dev_testvpn", exclusive=False, shutdown_on_apply=True))
        >>> requests.append(api.manage("SolaceQueue").enable(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True))
        >>> # [api.rpc(x) for x in requests]

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
        else:
            # Non Exclusive queue
            self.api.x = SolaceXMLBuilder("Set Queue %s to Exclusive " % queue_name, version=self.api.version)
            self.api.x.message_spool.vpn_name = vpn_name
            self.api.x.message_spool.queue.name = queue_name
            self.api.x.message_spool.queue.access_type.exclusive
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    # @only_on_shutdown('queue')
    @primary()
    def owner(self, **kwargs):
        """ Set the owner

        :param vpn_name: the name of the vpn
        :param queue_name: the queue name
        :param owner: the owner client-username
        :type vpn_name: str
        :type queue_name: str
        :type owner: str
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example:

        >>> api = SolaceAPI("dev")
        >>> requests = []
        >>> requests.append(api.manage("SolaceQueue").shutdown_ingress(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True))
        >>> requests.append(api.manage("SolaceQueue").shutdown_egress(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True))
        >>> requests.append(api.manage("SolaceQueue").owner(vpn_name="dev_testvpn", queue_name="testqueue1", owner_username="dev_testproductA"))
        >>> requests.append(api.manage("SolaceQueue").enable(queue_name="testqueue1", vpn_name="dev_testvpn"))
        >>> # [api.rpc(x) for x in requests]

        """

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
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    @primary()
    def max_bind_count(self, **kwargs):
        """Limit the max bind count

        :param vpn_name: the name of the vpn
        :param queue_name: the queue name
        :param max_bind_count: max bind count
        :type vpn_name: str
        :type queue_name: str
        :type max_bind_count: int
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example:

        >>> api = SolaceAPI("dev")
        >>> requests = api.manage("SolaceQueue").max_bind_count(vpn_name="dev_testvpn", queue_name="testqueue1", max_bind_count=50)
        >>> # response = api.rpc(requests)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        max_bind_count = get_key_from_kwargs("max_bind_count", kwargs)

        self.api.x = SolaceXMLBuilder("Settings Queue %s max bind count to %s" % (queue_name, str(max_bind_count)),
                                      version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.max_bind_count.value = max_bind_count
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True, backupOnly=False)
    # @only_on_shutdown('queue')
    @primary()
    @deprecation_warning("Please implement the use of the 'permission' method instead of relying on this")
    def consume(self, **kwargs):
        """Sets consume permission. add `consume` kwarg to allow non-owner users to consume.

        :param vpn_name: the name of the vpn
        :param queue_name: the queue name
        :param consume: set to "all" to allow ALL appliance client-users to "consume"
        :type vpn_name: str
        :type queue_name: str
        :type consume: str
        :rtype: plugin.PluginResponse
        :returns: single SEMP request
        .. deprecated:: 2.0
             Use :func:`permission` instead.

        Example:

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").consume(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True, consume="all")
        >>> # response = api.rpc(request)
        ""

        """

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
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True, backupOnly=False)
    # @only_on_shutdown('queue')
    @primary()
    def permission(self, **kwargs):
        """Sets permission on a queue

        :param vpn_name: the name of the vpn
        :param queue_name: the queue name
        :param permission: which permission to grant non-owner users. e.g. "consume", "delete", "modify-topic", "read-only"
        :type vpn_name: str
        :type queue_name: str
        :type permission: str
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example:

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").permission(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True, permission="consume")
        >>> # api.rpc(request)


        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        permission = get_key_from_kwargs("permission", kwargs)

        # Open Access
        self.api.x = SolaceXMLBuilder("Settings Queue %s Permission to %s" % (queue_name, permission),
                                      version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.permission.all
        if permission == "consume":
            self.api.x.message_spool.queue.permission.consume
        elif permission == "delete":
            self.api.x.message_spool.queue.permission.delete
        elif permission == "modify-topic":
            self.api.x.message_spool.queue.permission.modify_topic
        elif permission == "read-only":
            self.api.x.message_spool.queue.permission.read_only
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    @primary()
    def spool_size(self, **kwargs):
        """Set the spool size

        :param vpn_name: the name of the vpn
        :param queue_name: the queue name
        :param queue_size: size of the spool in mb
        :type vpn_name: str
        :type queue_name: str
        :type queue_size: int
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example:

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").spool_size(vpn_name="dev_testvpn", queue_name="testqueue1", queue_size=64)
        >>> # response = api.rpc(request)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        queue_size = get_key_from_kwargs("queue_size", kwargs)

        # Configure Queue Spool Usage
        self.api.x = SolaceXMLBuilder("Set Queue %s spool size: %s" % (queue_name, queue_size),
                                      version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.max_spool_usage.size = queue_size
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    @primary()
    def retries(self, **kwargs):
        """Delivery retries before failing the message

        :param vpn_name: the name of the vpn
        :param queue_name: the queue name
        :param retries: number of retries
        :type vpn_name: str
        :type queue_name: str
        :type retries: int
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example:

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").retries(vpn_name="dev_testvpn", queue_name="testqueue1", retries=5)
        >>> # response = api.rpc(request)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)
        retries = get_key_from_kwargs("retries", kwargs, default=0)

        self.api.x = SolaceXMLBuilder("Tuning max-redelivery retries for %s to %s" % (queue_name, retries),
                                      version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.max_redelivery.value = retries
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    @primary()
    def enable(self, **kwargs):
        """Enable a the queue

        :param vpn_name: the name of the vpn
        :param queue_name: the queue name
        :type vpn_name: str
        :type queue_name: str
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example:

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").enable(queue_name="testqueue1", vpn_name="dev_testvpn")
        >>> # response = api.rpc(request)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)

        # Enable the Queue
        self.api.x = SolaceXMLBuilder("Enabling Queue %s" % queue_name, version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.no.shutdown.full
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)

    @only_if_exists('get', 'rpc-reply.rpc.show.queue.queues.queue.info', primaryOnly=True)
    @primary()
    def reject_on_discard(self, **kwargs):
        """ Reject to sender on discard

        :param vpn_name: the name of the vpn
        :param queue_name: the queue name
        :type vpn_name: str
        :type queue_name: str
        :rtype: plugin.PluginResponse
        :returns: single SEMP request

        Example:

        >>> api = SolaceAPI("dev")
        >>> request = api.manage("SolaceQueue").reject_on_discard(vpn_name="dev_testvpn", queue_name="testqueue1")
        >>> # response = api.rpc(request)

        """

        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        queue_name = get_key_from_kwargs("queue_name", kwargs)

        self.api.x = SolaceXMLBuilder("Setting Queue to Reject Drops", version=self.api.version)
        self.api.x.message_spool.vpn_name = vpn_name
        self.api.x.message_spool.queue.name = queue_name
        self.api.x.message_spool.queue.reject_msg_to_sender_on_discard
        self.commands.enqueue(PluginResponse(str(self.api.x), **kwargs))
        return PluginResponse(str(self.api.x), **kwargs)
