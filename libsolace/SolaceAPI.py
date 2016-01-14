
import logging
import libsolace.settingsloader as settings
import libsolace
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace import xml2dict
import pprint

try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

try:
    import simplejson
except:
    from json import simplejson

from libsolace.util import httpRequest, generateRequestHeaders, generateBasicAuthHeader


class SolaceAPI:
    """
    Connects to a Solace cluster's *primary* and *backup* appliance(s)

    a SolaceAPI instance contains a SolaceXMLBuilder and a SolaceCommandQueue
    in order to facilitate the generation of SEMP XML requests, enqueuing the XML
    requests, and sending them to the appliance(s) through the rpc(str) method.

    SolaceAPI connects to **both** appliances in a redundant pair setup and gets
    the the *primary* and *backup* node states. Typically you issue the same SEMP
    command to both appliances. Commands can also be issued to either the primary
    or the backup appliance utilizing the `primaryOnly` and `backupOnly` kwargs.
    see: :func:`~libsolace.SolaceAPI.SolaceAPI.rpc`

    The version of the SolOS-TR OS is detected on instantiation, and this behaviour
    can be overridden with the `version` kwarg.

    Args:
        environment (str): The environment name to connect to as defined in
            libsolace.yaml.
        version (Optional(str)): set the version to disable version detection
            example of version: "soltr/6_0"
        detect_status (Optional(bool)): detect the primary/backup appliance through
            querying the message-spool state, default: True
        version (Optional(str)): set the solOS-TR version, if None the version will
            be retrieved from the appliances.
        testmode (Optional(bool)): Uses readonly user from config
            Communication with the appliance(s) will use the READ_ONLY_USER
            and READ_ONLY_PASS as defined in libsolace.yaml

    Returns:
        SolaceAPI: instance of SolaceAPI

    Examples:

        >>> api = SolaceAPI("dev")
        >>> api.x = SolaceXMLBuilder("My Something something", version=api.version)
        >>> api.x.show.message_spool.detail
        OrderedDict()
        >>> api.cq.enqueueV2(str(api.x))

        Set version on primary cluster node only:

        >>> api = SolaceAPI("dev", version="soltr/7_1_1")
        >>> api.x = SolaceXMLBuilder("My Something something", version=api.version)
        >>> api.x.show.message_spool
        OrderedDict()
        >>> api.cq.enqueueV2(str(api.x), primaryOnly=True)
        >>> api.rpc(str(api.cq.commands[0]))

        Backup cluster node only:

        >>> api = SolaceAPI("dev")
        >>> api.x = SolaceXMLBuilder("My Something something", version=api.version)
        >>> api.x.show.version
        OrderedDict()
        >>> api.cq.enqueueV2(str(api.x), backupOnly=True)

        Get a instance of SolaceQueue from the plugin manager

        >>> api = SolaceAPI("dev")
        >>> api.manager("SolaceQueue")

        Solace User plugin, check if a profile exists

        >>> api = SolaceAPI("dev")
        >>> api.manage("SolaceUser").check_client_profile_exists(client_profile="glassfish")
        True

        Create a Solace User via plugin

        >>> api.manage("SolaceUser", client_profile="glassfish", acl_profile="test", username="foo", password="bar", vpn_name="%s_testvpn").commands.commands # doctest:+ELLIPSIS
        [<rpc semp-version=...</client-username></rpc>]
        >>> api.manage("SolaceUser").get(username="%s_testvpn", vpn_name="%s_testvpn") # doctest:+ELLIPSIS
        {'reply': {u'show': {u'client-username'...}}}}}}

    """

    def __init__(self, environment, version=None, **kwargs):
        try:
            logging.debug("Solace Client version: %s" % version)

            logging.info("Connecting to appliances in %s" % environment)
            self.environment = environment

            self.config = settings.SOLACE_CONF[environment]
            logging.debug("Loaded Config: %s" % self.config)

            # testmode sets the user to the RO user
            self.testmode = kwargs.get("testmode", False)
            if self.testmode:
                self.config['USER'] = settings.READ_ONLY_USER
                self.config['PASS'] = settings.READ_ONLY_PASS
                logging.info('READONLY mode')

            # for SSL / TLS
            if 'VERIFY_SSL' not in self.config:
                self.config['VERIFY_SSL'] = True

            # detect primary / backup node instance states or assume
            # 1st node is primary and second is backup
            self.detect_status = kwargs.get("detect_status", True)
            if self.detect_status:
                logging.debug("Detecting primary and backup node states")
                self.status = self.get_message_spool(**kwargs)
                self.primaryRouter = None
                self.backupRouter = None

                for node in self.status:
                    spoolStatus = node['rpc-reply']['rpc']['show']['message-spool']['message-spool-info']['operational-status']
                    logging.debug(spoolStatus)
                    if spoolStatus == 'AD-Active' and self.primaryRouter == None:
                        self.primaryRouter = node['HOST']
                    elif self.backupRouter == None and self.primaryRouter != None:
                        self.backupRouter = node['HOST']
                    else:
                        logging.warn("More than one backup router?")
                        self.primaryRouter = node['HOST']
                    logging.info("Primary Router: %s" % self.primaryRouter)
                    logging.info("Backup Router: %s" % self.backupRouter)

            else:
                logging.debug("Not detecting statuses, using config")
                self.primaryRouter = self.config['MGMT'][0]
                self.backupRouter = self.config['MGMT'][1]

            # if the version is NOT specified, query appliance versions
            # assumes that backup and primary are SAME firmware version.s
            if version == None:
                logging.info("Detecting Version")
                self.xmlbuilder = SolaceXMLBuilder("Getting Version")
                self.xmlbuilder.show.version
                result = self.rpc(str(self.xmlbuilder), **kwargs)
                self.version = result[0]['rpc-reply']['@semp-version']
            else:
                logging.info("Setting Version %s" % version)
                self.version = version
            logging.info("Detected solOS-TR version: %s" % self.version)

            # backwards compatibility
            self.xmlbuilder = SolaceXMLBuilder(version = self.version)

            # shortcut / new methods
            self.x = SolaceXMLBuilder(version = self.version)
            self.cq = SolaceCommandQueue(version = self.version)

        except Exception, e:
            logging.warn("Solace Error %s" %e)
            raise

    def __restcall(self, request, primaryOnly=False, backupOnly=False, **kwargs):
        logging.info("%s user requesting: %s kwargs:%s primaryOnly:%s backupOnly:%s"
            % (self.config['USER'], request, kwargs, primaryOnly, backupOnly))
        self.kwargs = kwargs

        # appliances in the query
        appliances = self.config['MGMT']

        # change appliances based on boolean conditions
        if primaryOnly:
            logging.info("Primary appliance ONLY")
            appliances=[self.primaryRouter]
        if backupOnly:
            logging.info("Backup appliance ONLY")
            appliances=[self.backupRouter]

        try:
            data = OrderedDict()
            codes = OrderedDict()
            for host in appliances:
                url = host
                request_headers = generateRequestHeaders(
                    default_headers = {
                      'Content-type': 'text/xml',
                      'Accept': 'text/xml'
                    },
                    auth_headers = generateBasicAuthHeader(self.config['USER'], self.config['PASS'])
                )
                (response, response_headers, code) = httpRequest(url, method='POST', headers=request_headers, fields=request, timeout=5000, verifySsl = self.config['VERIFY_SSL'])
                data[host] = response
                codes[host] = code
            logging.debug(data)

            for k in data:
                thisreply = None
                try:
                    thisreply = xml2dict.parse(data[k])
                    if thisreply['rpc-reply'].has_key('execute-result'):
                        if thisreply['rpc-reply']['execute-result']['@code'] != 'ok':
                            logging.warn("Device: %s: %s %s" % (k, thisreply['rpc-reply']['execute-result']['@code'],
                                                                     "Request that failed: %s" % request))
                            logging.warn("Device: %s: %s: %s" % (k, thisreply['rpc-reply']['execute-result']['@code'],
                                                                        "Reply from appliance: %s" % thisreply['rpc-reply']['execute-result']['@reason']))
                        else:
                            logging.info("Device: %s: %s" % (k, thisreply['rpc-reply']['execute-result']['@code']))
                        logging.debug("Device: %s: %s" % (k, thisreply))
                    else:
                        logging.debug("no execute-result in response. Device: %s" % k)
                except Exception, e:
                    logging.error("Error decoding response from appliance")
                    logging.error("Response Codes: %s" % codes)
                    raise(Exception("Appliance Communication Failure"))
            logging.debug("Returning Data from rest_call")
            return data, codes

        except Exception, e:
            logging.warn("Solace Error %s" % e )
            raise



    def get_redundancy(self):
        """ Return redundancy status """
        try:
            request = SolaceXMLBuilder(version=self.version)
            request.show.redundancy
            return self.rpc(str(request))
        except:
            raise

    def get_memory(self):
        """ Returns the Memory Usage

        Example of request XML
        <rpc semp-version="soltr/6_0">
            <show>
                <memory></memory>
            </show>
        </rpc>
        """
        request = SolaceXMLBuilder(version=self.version)
        request.show.memory
        return self.rpc(str(request))

    def get_message_spool(self, **kwargs):
        """ show message spool """
        request = SolaceXMLBuilder(version="soltr/6_0")
        request.show.message_spool
        return self.rpc(str(request), **kwargs)

    def get_queue(self, queue, vpn, detail=False, **kwargs):
        """ Return Queue details """
        try:
            request = SolaceXMLBuilder(version=self.version)
            request.show.queue.name = queue
            request.show.queue.vpn_name = vpn
            if detail:
                request.show.queue.detail
            return self.rpc(str(request))
        except:
            raise

    def list_queues(self, vpn, queue_filter='*'):
        """ List all queues in a VPN """
        try:
            request = SolaceXMLBuilder(version=self.version)
            request.show.queue.name=queue_filter
            request.show.queue.vpn_name = vpn
            response = self.rpc(str(request))
            logging.debug(response)
            queues = []
            for k in response:
                logging.debug("Response: %s" % k)
                try:
                    myq = [ queue['name'] for queue in k['rpc-reply']['rpc']['show']['queue']['queues']['queue'] ]
                    for q in myq:
                        queues.append(q)
                except TypeError, e:
                    logging.warn("Atttibute Error %s" % e)
                    try:
                        queues.append(k['rpc-reply']['rpc']['show']['queue']['queues']['queue']['name'])
                    except:
                        logging.warn("Error %s" % e)
                        pass
                logging.debug(queues)
            return queues
        except Exception, e:
            logging.warn("Solace Exception, %s" % e)
            raise

    def get_client_username_queues(self, client_username, vpn):
        """
        Returns a list of queues owned by user
        """
        result = []
        response = self.get_queue('*', vpn, detail=True)
        #queue_list = lambda x,y: [ yy['name'] for yy in y if yy['info']['owner'] == x ]
        queue_list = {
            list: lambda x: [ y['name'] for y in x if y['info']['owner'] == client_username ],
            dict: lambda x: [ y['name'] for y in [x] if y['info']['owner'] == client_username ]
            }
        try:
            for h in response:
                if h['rpc-reply']['rpc']['show']['queue'] != None and h['rpc-reply']['rpc']['show']['queue']['queues'] != None:
                    queues = h['rpc-reply']['rpc']['show']['queue']['queues']['queue']
                    result.extend(queue_list[type(queues)](queues))
        except KeyError, e:
            raise Exception("While getting list of queues from get_queue() the response did not contain the expected data. VPN: %s. Exception message: %s" % (vpn,str(e)))
        else:
            return result

    def is_client_username_inuse(self, client_username, vpn):
        """
        Returns boolean if client username has client connections
        """
        result = []
        response = self.get_client('*', vpn, detail=True)
        in_use = lambda x,y: [ True for yy in y if yy['client-username'] == x ]
        try:
            for h in response:
                if h['rpc-reply']['rpc']['show']['client'].has_key('primary-virtual-router'):
                    result = in_use(client_username,h['rpc-reply']['rpc']['show']['client']['primary-virtual-router']['client'])
        except KeyError, e:
            raise Exception("While getting list of connection from get_client() the response did not contain the expected data. VPN: %s. Exception message: %s" % (vpn,str(e)))
        else:
            return result.count(True) > 0

    def does_client_username_exist(self, client_username, vpn):
        """
        Returns boolean if client username exists inside vpn
        """
        response = self.get_client_username(client_username, vpn)
        try:
            result = [ x for x in response if x['rpc-reply']['rpc']['show']['client-username']['client-usernames'] != None and x['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']['client-username'] == client_username ]
        except TypeError, e:
            raise Exception("Client username not consistent across all nodes. Message: %s" % str(e))
        else:
            if len(result) > 0 and len(result) < len(response):
                msg = "Client username not consistent across all nodes, SEMP: %s" % str(result)
                logging.error(msg)
                raise Exception(msg)
            elif len(result) == len(response):
                return True
            else:
                return False

    def is_client_username_enabled(self, client_username, vpn):
        """
        Returns boolean if client username inside vpn is enabled
        """
        response = self.get_client_username(client_username, vpn)
        evaluate = lambda x: x['client-username'] == client_username and x['enabled'] == 'true'
        result = [ evaluate(x['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']) for x in response
                      if x['rpc-reply']['rpc']['show']['client-username']['client-usernames'] != None ]
        if len(result) == 0:
            raise Exception("Client username %s not found" % client_username)
        elif len(result) < len(response):
            raise Exception("Client username %s not consistent. Does not exist on all nodes" % client_username)
        if (not result[0]) in result:
            raise Exception("Client username %s not consistent. Enabled and disabled on some nodes" % client_username)
        else:
            return result[0]

    def get_client_username(self, clientusername, vpn, detail=False, **kwargs):
        """
        Get client username details

        Example:
            >>> c = SolaceAPI("dev")
            >>> c.get_client_username("%s_testvpn", "%s_testvpn")
            {'reply': {u'show': {u'client-username': {u'client-usernames': {u'client-username': {u'profile': u'glassfish', u'acl-profile': u'dev_testvpn', u'guaranteed-endpoint-permission-override': u'false', u'client-username': u'dev_testvpn', u'enabled': u'true', u'message-vpn': u'dev_testvpn', u'password-configured': u'true', u'num-clients': u'0', u'num-endpoints': u'2', u'subscription-manager': u'false', u'max-connections': u'500', u'max-endpoints': u'16000'}}}}}}

        """

        return self.manage("SolaceUser").get(username = clientusername, vpn_name = vpn)


    def get_client(self, client, vpn, detail=False, **kwargs):
        """ Get Client details """
        try:
            request = SolaceXMLBuilder(version = self.version)
            request.show.client.name = client
            request.show.client.vpn_name = vpn
            if detail:
                request.show.client.detail
            return self.rpc(str(request))
        except:
            raise

    def get_vpn(self, vpn, stats=False):
        """ Get VPN details """
        try:
            request = SolaceXMLBuilder(version = self.version)
            request.show.message_vpn.vpn_name = vpn
            if stats:
                request.show.message_vpn.stats
            return self.rpc(str(request))
        except:
            raise

    def list_vpns(self, vpn):
        try:
            request = SolaceXMLBuilder(version = self.version)
            request.show.message_vpn.vpn_name = vpn
            response = self.rpc(str(request))
            #try:
            return [vpn['name'] for vpn in response[0]['rpc-reply']['rpc']['show']['message-vpn']['vpn']] #['replication']['message-vpns']['message-vpn']]
            #except:
            #    return [response[0]['rpc-reply']['rpc']['show']['message-vpn']['vpn']]
        except:
            raise

    def rpc(self, xml, allowfail=False, primaryOnly=False, backupOnly=False, **kwargs):
        """
        Execute a SEMP command on the appliance(s), call with a string representation
        of a SolaceXMLBuilder instance.

        Args:
            xml(str): string representation of a SolaceXMLBuilder instance.
            allowFail(Optional(bool)): tollerate some types of errors from the
                appliance.
            primaryOnly(Optional(bool)): only execute on primary appliance.
            backupOnly(Optional(bool)): only execute on backup appliance.

        Returns:
            data response list as from appliances. Json-like data

        Example:
            >>> conn = SolaceAPI("dev")
            >>> xb = SolaceXMLBuilder(version = conn.version)
            >>> xb.show.version
            OrderedDict()
            >>> type(conn.rpc(str(xb)))
            <type 'list'>

        """
        responses = None
        mywargs = kwargs
        logging.debug("Kwargs: %s" % mywargs)
        try:
            data = []
            responses, codes = self.__restcall(xml, primaryOnly=primaryOnly, backupOnly=backupOnly, **mywargs)
            for k in responses:
                response = xml2dict.parse(responses[k])
                logging.debug(response)
                response['HOST'] = k
                if not allowfail:
                    if response['rpc-reply'].has_key('parse-error'):
                        raise Exception(str(response))
                    elif response['rpc-reply'].has_key('permission-error'):
                        if self.testmode:
                            logging.debug('tollerable permission error in test mode')
                        else:
                            logging.critical("Sholly Hit! Request was: %s" % xml)
                            raise Exception(str(response))
                    else:
                        data.append(response)
                else:
                    data.append(response)
            return data
        except:
            logging.error("responses: %s" % responses)
            raise

    def manage(self, plugin_name, **kwargs):
        """
        Gets a plugin, configures it, then allows direct communication with it.

        Plugins are passed the kwargs directly if any are specified.

        Example:
            >>> api = SolaceAPI("dev")
            >>> api.manage("SolaceUser").check_client_profile_exists(client_profile="glassfish")
            True
            >>> api.manage("SolaceUser", client_profile="glassfish", acl_profile="test", username="foo", password="bar", vpn_name="%s_testvpn").commands.commands
            [<rpc semp-version="soltr/6_0"><create><client-username><username>foo</username><vpn-name>%s_testvpn</vpn-name></client-username></create></rpc>, <rpc semp-version="soltr/6_0"><client-username><username>foo</username><vpn-name>%s_testvpn</vpn-name><client-profile><name>glassfish</name></client-profile></client-username></rpc>, <rpc semp-version="soltr/6_0"><client-username><username>foo</username><vpn-name>%s_testvpn</vpn-name><acl-profile><name>test</name></acl-profile></client-username></rpc>, <rpc semp-version="soltr/6_0"><client-username><username>foo</username><vpn-name>%s_testvpn</vpn-name><no><guaranteed-endpoint-permission-override/></no></client-username></rpc>, <rpc semp-version="soltr/6_0"><client-username><username>foo</username><vpn-name>%s_testvpn</vpn-name><no><subscription-manager/></no></client-username></rpc>, <rpc semp-version="soltr/6_0"><client-username><username>foo</username><vpn-name>%s_testvpn</vpn-name><password><password>bar</password></password></client-username></rpc>, <rpc semp-version="soltr/6_0"><client-username><username>foo</username><vpn-name>%s_testvpn</vpn-name><no><shutdown/></no></client-username></rpc>]
            >>> api.manage("SolaceUser").get(username="%s_testvpn", vpn_name="%s_testvpn")
            {'reply': {u'show': {u'client-username': {u'client-usernames': {u'client-username': {u'profile': u'glassfish', u'acl-profile': u'dev_testvpn', u'guaranteed-endpoint-permission-override': u'false', u'client-username': u'dev_testvpn', u'enabled': u'true', u'message-vpn': u'dev_testvpn', u'password-configured': u'true', u'num-clients': u'0', u'num-endpoints': u'2', u'subscription-manager': u'false', u'max-connections': u'500', u'max-endpoints': u'16000'}}}}}}

        """

        plugin = libsolace.plugin_registry(plugin_name, **kwargs)
        logging.info("Setting up the plugin instance with api and kwargs")
        return plugin(api=self, **kwargs)


if __name__ == "__main__":
    import doctest
    import logging
    import sys
    logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
    logging.getLogger().setLevel(logging.INFO)
    doctest.testmod()
