from libsolace.util import httpRequest, generateRequestHeaders, generateBasicAuthHeader, xml2obj

import logging
from lxml import etree as ET

# Let the code that implements this API deal with logging
try:
    logging.getLogger().addHandler(logging.NullHandler())
except AttributeError:
    from libsolace.util import NullHandler
    logging.getLogger().addHandler(NullHandler())


class XMLAPI:
    """ XML API handles reading the XML configuiration from URL or FILE.

        xmlapi = XMLAPI(url="http://foo.com/config.xml" username="someuser", password="somepassword")
        vpns = xmlapi.getSolaceByOwner(owner, environment=env)
        users = xmlapi.getUsersOfVpn(vpn.name, environment=options.env)

    """
    def __init__(self, url=None, username=None, password=None, timeout=10, xml_file=None, use_etree=False,
                 use_xml2obj=True, etree_case_insensitive=False, **kwargs):
        """ Fetches data from site-config XML over URL or localfs and returns subsets of the data as requested.

        :type url: string
        :type username: string
        :type password: string
        :type timeout: int
        :type xml_file: file.io
        :type use_etree: bool
        :type use_xml2obj: bool
        :type etree_case_insensitive: bool

        :param url: url to source index.xml from
        :param username: username to auth as
        :param password: users password
        :param timeout: rest call timeout, default 10 seconds
        :param xml_file: file to open if available
        :param use_etree: enables etree parsing of index.xml for methods that use it
        :param use_xml2obj: enables the default libsolace.gfmisc.xml2obj implementation
        :param etree_case_insensitive: downcases index.xml and all method param values which uses it

        """
        self.deploydata = None
        self.components = None
        self.etree_case_insensitive = etree_case_insensitive

        if xml_file:
            logging.debug('Local file will be read, REST Calls disabled')
            self.xml_file_data = xml_file.read()
        else:
            self.xml_file_data = None
            self.username = username
            self.password = password
            self.timeout = timeout
            self.url = url
        if use_etree:
            self.root = self.__get_et_root_object()
            self.namespace = ET.QName(self.root.tag).namespace
        if use_xml2obj:
            self.populateDeployData()

    def __route_call(self, url, **kwargs):
        """ Determines if the call should be routed via urllib or read from local file.

        :param url: url to call
        :param kwargs:
        :return: response from correct interface
        """
        if self.xml_file_data:
            return self.__read_file()
        else:
            logging.debug("route call: %s" % url)
            return self.__restcall(url, **kwargs)

    def __read_file(self, **kwargs):
        """ returns the file data from self.xml_file_data

        :param kwargs:
        :return: file contents
        :rtype: str
        """
        return self.xml_file_data

    def __restcall(self, url, method='GET', fields=None, **kwargs):
        """ Uses urllib to read a data from a webservice, if self.xml_file_data = None, else returns the local file contents

        :type url: str
        :param url: url to call
        :param kwargs:
        :return: response data
        :rtype: str
        """
        request_headers = generateRequestHeaders(
            default_headers = {
              'Content-type': 'application/json',
              'Accept': 'application/json'
            })
        (data, response_headers, code) = httpRequest(url, method=method, headers=request_headers, fields=fields, timeout=self.timeout)
        return data

    def __get_et_root_object(self):
        """
        Returns elementtree root object representation of index.xml

        :return: Element object
        :rtype: xml.etree.ElementTree.Element
        """
        if self.xml_file_data:
            if self.etree_case_insensitive:
                et_xml = self.xml_file_data.lower()
            else:
                et_xml = self.xml_file_data
        else:
            if self.etree_case_insensitive:
                et_xml = self.__route_call(self.url).lower()
            else:
                et_xml = self.__route_call(self.url)
        return ET.fromstring(et_xml)

    def populateDeployData(self):
        """ Returns the entire deployment data ( entire xml ) as a python dict style object
        :return: all deployment data in a single dictionary object
        """
        if self.xml_file_data:
            self.deploydata = xml2obj(self.xml_file_data)
        else:
            myXML = self.__route_call(self.url)
            self.deploydata = xml2obj(myXML)

    def getSolace(self, vpn):
        """ Return a VPN by name

        :return: a solace vpn
        """
        self.populateDeployData()
        for v in self.deploydata.solace.vpn:
            logging.debug("VPN: %s in solace" % v.name)
            if v.name == vpn:
                return v
        raise BaseException('Unable to find solace configuration for vpn: %s' % vpn)

    def getSolaceByOwner(self, owner, **kwargs):
        """
        Return a VPN by owner

        :type owner: str

        :return list of vpns
        :rtype libsolace.gfmisc.DataNode

        """
        self.populateDeployData()
        vpns = []
        for v in self.deploydata.solace.vpn:
            logging.debug("VPN: %s in solace" % v.name)
            if v.owner == owner:
                vpns.append(v)
        return vpns

    def getUsersOfVpn(self, vpn, environment=None):
        """ Returns all products users who use a specifig messaging VPN

        :type vpn: str
        :param vpn: name of vpn to search for users of

        """
        self.populateDeployData()
        users = []
        logging.warn('Scaning for Products using vpn: %s' % vpn)
        for p in self.deploydata.product:
            logging.debug('Scanning Product: %s for messaging declarations' % p.name)
            if p.messaging:
                for m in p.messaging:
                    #  <messaging name="my_%s_sitemq" user="%s_um" password="somepassword"></messaging>
                    if m.name == vpn:
                        password = m.password
                        try:
                            #logging.debug("Dumping messaging environments: %s" % pprint.pprint(m.__dict__))
                            for e in m.env:
                                #logging.info("Env Searching %s" % e.name)
                                if e.name == environment:
                                    #logging.info("Env Matched %s" % e.name)
                                    for myp in e.messaging_conf:
                                        logging.info('Setting password %s' % myp.password)
                                        password = myp.password
                        except Exception, e:
                            logging.warn("No Environment Password Overrides %s" % e)
                            pass

                        logging.info('Product: %s using VPN: %s, adding user %s to users list' % (p.name, vpn, m.username))
                        users.append({'username': m.username, 'password': password})
        return users
