
import logging
import libsolace.settingsloader as settings
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
    Used by SolaceProvision, Use directly only if you know what you're doing. See SolaceProvision rather.

    Example:

    api = SolaceAPI("dev")
    api.x = XMLBuilder("My Something something", version=api.version)
    api.cq.enqueueV2(str(api.x))

    Set version on primary cluster node only:

    api = SolaceAPI("dev", version="soltr/7_1_1")
    api.x = XMLBuilder("My Something something", version=api.version)
    api.cq.enqueueV2(str(api.x), primaryOnly=True)

    Backup cluster node only:
    api = SolaceAPI("dev")
    api.x = XMLBuilder("My Something something", version=api.version)
    api.cq.enqueueV2(str(api.x), backupOnly=True)

    """
    def __init__(self, environment, version=None, testmode=False, **kwargs):
        try:
            logging.debug("Solace Client initializing version: %s" % version)
            self.config = settings.SOLACE_CONF[environment]
            logging.debug("Loaded Config: %s" % self.config)
            self.testmode = testmode
            if 'VERIFY_SSL' not in self.config:
                self.config['VERIFY_SSL'] = True
            if testmode:
                self.config['USER'] = settings.READ_ONLY_USER
                self.config['PASS'] = settings.READ_ONLY_PASS
                logging.info('READONLY mode')
            logging.debug("Final Config: %s" % self.config)

            # get the spool statuses since its a fairly reliable way to determin
            # the primary vs backup routers
            self.status = self.get_message_spool()

            self.primaryRouter = None
            self.backupRouter = None

            for node in self.status:
                spoolStatus = node['rpc-reply']['rpc']['show']['message-spool']['message-spool-info']['operational-status']
                logging.info(spoolStatus)
                if spoolStatus == 'AD-Active' and self.primaryRouter == None:
                    self.primaryRouter = node['HOST']
                elif self.backupRouter == None and self.primaryRouter != None:
                    self.backupRouter = node['HOST']
                else:
                    logging.warn("More than one backup router?")
                    self.primaryRouter = node['HOST']
                    #raise BaseException("Appliance State(s) Error")

            if version == None:
                logging.info("Detecting Version")
                self.xmlbuilder = SolaceXMLBuilder("Getting Version")
                self.xmlbuilder.show.version
                result = self.rpc(str(self.xmlbuilder))
                self.version = result[0]['rpc-reply']['@semp-version']
            else:
                logging.info("Setting Version %s" % version)
                self.version = version
            logging.info("Detected version: %s" % self.version)

            # backwards compatibility
            self.xmlbuilder = SolaceXMLBuilder(version = self.version)

            # shortcut / new methods
            self.x = SolaceXMLBuilder(version = self.version)
            self.cq = SolaceCommandQueue(version = self.version)

        except Exception, e:
            logging.warn("Solace Error %s" %e)
            raise BaseException("Configuration Error")

    def __restcall(self, request, primaryOnly=False, backupOnly=False, **kwargs):
        logging.info("%s user requesting: %s" % (self.config['USER'], request))
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
        """ Return redundancy information """
        try:
            #request = '<rpc semp-version="soltr/6_0"><show><redundancy></redundancy></show></rpc>'
            request = SolaceXMLBuilder(version=self.version)
            request.show.redundancy
            return self.rpc(str(request))
        except:
            raise

    def get_memory(self):
        """ Returns the Memory Usage """
        try:
            #request ='<rpc semp-version="soltr/6_0"><show><memory></memory></show></rpc>'
            request = SolaceXMLBuilder(version=self.version)
            request.show.memory
            return self.rpc(str(request))
        except:
            raise

    def get_message_spool(self):
        """ Returns the Message Spool """
        try:
            request = SolaceXMLBuilder(version="soltr/6_0")
            request.show.message_spool
            return self.rpc(str(request))
        except:
            raise

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
        """
        try:
            request = SolaceXMLBuilder(version = self.version)
            request.show.client_username.name = clientusername
            request.show.client_username.vpn_name = vpn
            if detail:
                request.show.client_username.detail

            return self.rpc(str(request))
        except:
            raise

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

    def rpc(self, xml, allowfail=False, **kwargs):
        ''' Ships XML string direct to the Solace RPC '''
        responses = None
        mywargs = kwargs
        logging.info("Kwargs: %s" % mywargs)
        try:
            data = []
            responses, codes = self.__restcall(xml, **mywargs)
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
