
import libsolace.settingsloader as settings
import logging
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

import urllib2
import base64
URLLIB2 = True
URLLIB3 = False


class SolaceAPI:
    """ Used by SolaceHelper, Use directly only if you know what you're doing. See SolaceHelper rather. """
    def __init__(self, environment, testmode=False, **kwargs):
        try:
            logging.debug("Solace Client initializing")
            self.config = settings.SOLACE_CONF[environment]
            self.testmode = testmode
            if testmode:
                self.config['USER'] = settings.READ_ONLY_USER
                self.config['PASS'] = settings.READ_ONLY_PASS
                logging.warning('READONLY mode')
        except Exception, e:
            logging.warn("Solace Error %s" %e)
            raise BaseException("Configuration Error")

    def __restcall(self, request, **kwargs):
        logging.info("%s user requesting: %s" % (self.config['USER'], request))
        self.kwargs = kwargs
        try:
            data = OrderedDict()
            for host in self.config['MGMT']:
                url = 'http://%s/SEMP' % host
                headers = base64.encodestring('%s:%s' % (self.config['USER'],self.config['PASS']))[:-1]
                req = urllib2.Request(url=url,
                                      data=request,
                                      headers={'Content-Type': 'application/xml'})
                req.add_header("Authorization", "Basic %s" % headers)
                response = urllib2.urlopen(req)
                data[host]=response.read()
            logging.debug(data)
            for k in data:
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
            logging.debug("Returning Data from rest_call")
            return data
        except Exception, e:
            logging.warn("Solace Error %s" % e )
            raise

    def get_memory(self):
        """ Returns the Memory Usage """
        try:
            request ='<rpc semp-version="soltr/5_3"><show><memory></memory></show></rpc>'
            return self.rpc(request)
        except:
            raise

    def get_queue(self, queue, vpn, **kwargs):
        """ Return Queue details """
        try:
            extras = []
            if kwargs.has_key('detail'):
                if kwargs['detail']: extras.append('<detail/>')
            request = '<rpc semp-version="soltr/5_3"><show><queue><name>%s</name>' \
                      '<vpn-name>%s</vpn-name>%s</queue></show></rpc>' % (queue, vpn, "".join(extras))
            return self.rpc(request)
        except:
            raise

    def list_queues(self, vpn, queue_filter='*'):
        """ List all queues in a VPN """
        try:
            request = '<rpc semp-version="soltr/5_3"><show><queue><name>%s</name>' \
                      '<vpn-name>%s</vpn-name></queue></show></rpc>' % (queue_filter, vpn)
            response = self.rpc(request)
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

    def get_client_username(self, clientusername, vpn, **kwargs):
        """
        Get client username details
        """
        extras = []
        if kwargs.has_key('detail'):
            if kwargs['detail']: extras.append('<detail/>')
        if kwargs.has_key('count'):
            if kwargs['count']: extras.append('<count/>')
        request = '<rpc semp-version="soltr/5_3"><show><client-username>' \
                  '<name>%s</name><vpn-name>%s</vpn-name>%s</client-username></show></rpc>' % ( clientusername, vpn, "".join(extras))
        return self.rpc(request)

    def get_client(self, client, vpn, **kwargs):
        """ Get Client details """
        extras = []
        if kwargs.has_key('detail'):
            if kwargs['detail']: extras.append('<detail/>')
        try:
            request = '<rpc semp-version="soltr/5_3"><show><client>' \
                      '<name>%s</name><vpn-name>%s</vpn-name>%s</client></show></rpc>' % ( client, vpn, "".join(extras))
            return self.rpc(request)
        except:
            raise

    def get_vpn(self, vpn):
        """ Get VPN details """
        try:
            request = '<rpc semp-version="soltr/5_5"><show><message-vpn>' \
                      '<vpn-name>%s</vpn-name></message-vpn></show></rpc>' % vpn
            return self.rpc(request)
        except:
            raise

    def list_vpns(self, vpn):
        try:
            request = '<rpc semp-version="soltr/5_5"><show><message-vpn><vpn-name>%s</vpn-name>' \
                      '<replication/></message-vpn></show></rpc>' % vpn
            response = self.rpc(request)
            try:
                return [vpn['vpn-name'] for vpn in response[0]['rpc-reply']['rpc']['show']['message-vpn']['replication']['message-vpns']['message-vpn']]
            except:
                return [response[0]['rpc-reply']['rpc']['show']['message-vpn']['replication']['message-vpns']['message-vpn']['vpn-name']]
        except:
            raise

    def rpc(self, xml, allowfail=False,  **kwargs):
        ''' Ships XML string direct to the Solace RPC '''
        try:
            data = []
            responses = self.__restcall(xml)
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
            raise
