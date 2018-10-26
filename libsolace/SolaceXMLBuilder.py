import logging

from collections import OrderedDict

import re

from libsolace.SolaceNode import SolaceNode
from libsolace.util import d2x, get_calling_module


class SolaceXMLBuilder(object):
    """Builds Solace's SEMP XML Configuration Commands

    Creating a instance of this, and then calling any obj on the instance, will create
    nested XML tags if the element does not exist, or return the element if it does exist
    for recursive instantiation.

    THe only limitatoin here is that there can only be ONE root node, "foo" in the example below.

    Example

        >>> from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
        >>> a=SolaceXMLBuilder(version="soltr/6_2")
        >>> a.foo.bar.baz=2
        >>> a.foo.banana
        OrderedDict()
        >>> str(a)
        '<rpc semp-version="soltr/6_2"><foo><bar><baz>2</baz></bar><banana/></foo></rpc>'
        >>> a.bar.zoo = 2 # different ROOT will break repr
        >>> str(a)
        Traceback (most recent call last):
          ...
        AttributeError: d2x instance has no attribute 'root'



    """

    def __init__(self, description=None, version=None, **kwargs):

        if version is None:
            version = "soltr/6_0"

        self.__dict__ = OrderedDict()
        self.__setattr__ = None
        if description is not None:
            self.description = description
        self.version = version
        calling_module = get_calling_module()
        logging.info("Called by module: %s - %s description: %s " % (calling_module, self.version, description))

    def __getattr__(self, name):
        name = re.sub("_", "-", name)
        try:
            return self.__dict__[name]
        except:
            self.__dict__[name] = SolaceNode()
            return self.__dict__[name]

    def __repr__(self):
        myxml = d2x(eval(str(self.__dict__)))
        # I had to conjur up my own header cause solace doesnt like </rpc> to have attribs
        complete_xml = str('<rpc semp-version="%s">%s</rpc>' % (self.version, myxml.display(version=self.version)))
        logging.debug("Returning XML: %s" % complete_xml)
        return complete_xml

    def __call__(self, *args, **kwargs):
        return self.__dict__
