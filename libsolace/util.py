import re
import xml.sax.handler
import pkg_resources
import base64
import inspect
from xml.dom.minidom import Document
from distutils.version import StrictVersion

import libsolace
from libsolace.Exceptions import MissingProperty

from collections import OrderedDict

import logging

logger = logging.getLogger(__name__)


"""

.. testsetup::
    from libsolace.util import *

"""


try:
    import urllib3

    URLLIB3 = True
    URLLIB2 = False
except:
    import urllib
    import urllib2

    URLLIB2 = True
    URLLIB3 = False

try:
    version = pkg_resources.get_distribution('libsolace').version
except pkg_resources.DistributionNotFound:
    version = 'unknown'


def xml2obj(src):
    """A simple function to converts XML data into native Python object.

	Parameters:
	src -- XML source
	"""
    non_id_char = re.compile('[^_0-9a-zA-Z]')

    def _name_mangle(name):
        return non_id_char.sub('_', name)

    class DataNode(object):
        def __init__(self):
            self._attrs = {}  # XML attributes and child elements

        def __len__(self):
            # treat single element as a list of 1
            return 1

        def __setitem__(self, key, value):
            self._attrs[key] = value

        def __getitem__(self, key):
            if isinstance(key, basestring):
                return self._attrs.get(key, None)
            else:
                return [self][key]

        def __contains__(self, name):
            return self._attrs.has_key(name)

        def __nonzero__(self):
            return bool(self._attrs or self.data)

        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name, None)

        def _add_xml_attr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value

        def __str__(self):
            return self.data or ''

        def __repr__(self):
            items = sorted(self._attrs.items())
            if self.data:
                items.append(('data', self.data))
            return u'{%s}' % ', '.join([u'%s:%s' % (k, repr(v)) for k, v in items])

    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.current = self.root
            self.text_parts = []

        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = DataNode()
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
                self.current._add_xml_attr(_name_mangle(k), v)

        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = text
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._add_xml_attr(_name_mangle(name), obj)

        def characters(self, content):
            self.text_parts.append(content)

    builder = TreeBuilder()
    if isinstance(src, basestring):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root._attrs.values()[0]


class d2x:
    """ Converts Dictionary to XML """

    def __init__(self, structure):
        self.doc = Document()
        if len(structure) == 1:
            rootName = str(structure.keys()[0])
            self.root = self.doc.createElement(rootName)
            self.doc.appendChild(self.root)
            self.build(self.root, structure[rootName])

    def build(self, father, structure):
        if type(structure) == dict:
            for k in structure:
                tag = self.doc.createElement(k)
                father.appendChild(tag)
                self.build(tag, structure[k])
        elif type(structure) == OrderedDict:
            for k in structure:
                tag = self.doc.createElement(k)
                father.appendChild(tag)
                self.build(tag, structure[k])

        elif type(structure) == list:
            grandFather = father.parentNode
            tagName = father.tagName
            grandFather.removeChild(father)
            for l in structure:
                tag = self.doc.createElement(tagName)
                self.build(tag, l)
                grandFather.appendChild(tag)

        else:
            data = str(structure)
            tag = self.doc.createTextNode(data)
            father.appendChild(tag)

    def display(self, version="soltr/6_0"):
        # I render from the root instead of doc to get rid of the XML header
        # return self.root.toprettyxml(indent="  ")
        try:
            complete_xml = str('\n<rpc semp-version="%s">\n%s</rpc>' % (version, self.root.toprettyxml(indent="  ")))
            logging.debug(complete_xml)
            return self.root.toxml()
            # return self.root.toprettyxml(indent="  ")
        except AttributeError, e:
            logging.error("the root leaf node was not found, maybe you registered two roots!")
            raise


def httpRequest(url, fields=None, headers=None, method='GET', timeout=3, protocol="http", verifySsl=False, **kwargs):
    """
    Performs HTTP request

    :param url: URL accessed
    :type url: str
    :param kwargs:
    :type kwargs: dict

    :return: Tuple containing data, headers and responsecode
    :rtype: tuple

    >>> l = httpRequest('http://www.google.se', method='GET')
    >>> type(l)
    <type 'tuple'>

    """
    if URLLIB3:
        logger.debug('Using urllib3')
        http = urllib3.PoolManager()
        if method == 'GET':
            request = http.request_encode_url(method, url, fields=fields, headers=headers, timeout=timeout)
        elif method == 'POST':
            logging.debug("method: %s, url: %s, headers: %s, fields: %s" % (method, url, headers, fields))
            request = http.urlopen(method, url, headers=headers, body=fields)
        code = request.status
        logging.debug("response code: %s" % code)
        headers = request.getheaders()
        logging.debug("response headers: %s" % headers)
        data = request.data
        logging.debug("response data: %s" % data)
    elif URLLIB2:
        logger.debug('Using urllib2')
        if not method in ['GET', 'POST']:
            raise Exception('Unsupported HTTP method %s while using urllib2' % method)

        req = urllib2.Request(url=url,
                              data=fields,
                              headers=headers)

        ctx = None
        if protocol == 'https' and not verify:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        response = urllib2.urlopen(req, ctx)

        code = response.getcode()
        headers = response.headers.dict
        data = response.read()
    logger.debug('Got response. Data: %s, Headers: %s, Status code: %s' % (str(data), str(headers), str(code)))
    return (data, headers, code)


def generateBasicAuthHeader(username, password):
    """
    Generates a basic auth header

    :param username: Username of user
    :type username: str
    :param password: Password of user
    :type password: str
    :return: Dict containing basic auth header
    :rtype: dict

    >>> generateBasicAuthHeader('test','test')
    {'Authorization': 'Basic dGVzdDp0ZXN0'}

    """
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    return {'Authorization': 'Basic %s' % base64string}


def generateRequestHeaders(**kwargs):
    """
    Generates a dict of headers

    :param kwargs: Dict of headers
    :type kwargs: dict
    :return: Dict containing headers
    :rtype: dict

    >>> generateRequestHeaders(someheaders={'header1':'value1'})
    {'header1': 'value1', 'User-agent': 'libsolace/doctest'}

    """
    request_headers = {'User-agent': 'libsolace/%s' % str(version)}
    for key in kwargs.keys():
        if type(kwargs[key]) is dict: request_headers.update(kwargs[key])
    logger.debug("Headers generated: %s" % request_headers)
    return request_headers


def version_equal_or_greater_than(left, right):
    """
    Checks if right is equals or greater than left

    :param left: soltr_version string
    :type left: str
    :param right: soltr_version string
    :type right: str
    :return: result of comparison
    :rtype: bool

    >>> version_equal_or_greater_than('soltr/6_0', 'soltr/6_2')
    True

    """

    def _extract_version(soltr_version):
        try:
            return re.sub(u'_', '.', soltr_version.split("/")[1])
        except:
            msg = "Failed to parse version %s" % soltr_version
            logger.error(msg)
            raise Exception(msg)

    left = _extract_version(left)
    right = _extract_version(right)
    return StrictVersion(right) >= StrictVersion(left)


def get_key_from_kwargs(key, kwargs, default=None):
    """
    Returns a key from kwargs or raises exception is no key is present

    Example:

    >>> get_key_from_kwargs("vpn_name", kwargs)
    'dev_testvpn'

    >>> get_key_from_kwargs("missing_key", other_dict, default=True)
    True

    >>> get_key_from_kwargs("missin_key", kwargs)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/keghol/Development/libsolace/libsolace/util.py", line 303, in get_key_from_kwargs
        raise(MissingProperty(key))
    libsolace.Exceptions.MissingProperty: missing_key

    """
    if key in kwargs:
        return kwargs.get(key)
    elif default != None:
        return default
    else:
        raise (MissingProperty("%s is missing from kwargs" % key))


def get_key_from_settings(key, kwargs, default=None):
    """
    Same as above, but different error message
    """
    if key in kwargs:
        return kwargs.get(key)
    elif default != None:
        return default
    else:
        raise (MissingProperty("%s is missing from yaml config"))


def get_plugin(plugin_name, solace_api, *args, **kwargs):
    """
    Returns a new plugin configured for the environment

    :param plugin_name: name of the plugun
    :param solace_api: a instance of SolaceAPI
    :param kwargs:
    :return:
    """
    plugin = libsolace.plugin_registry(plugin_name, **kwargs)
    logging.info(args)
    return plugin(api=solace_api, *args, **kwargs)


def get_calling_module(point=2):
    """
    Return a module at a different point in the stack.

    :param point: the number of calls backwards in the stack.
    :return:
    """
    frm = inspect.stack()[point]
    function = str(frm[3])
    line = str(frm[2])
    modulepath = str(frm[1]).split('/')
    module = str(modulepath.pop())
    return "%s:%s" % (module, line)
