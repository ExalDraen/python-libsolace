try:
    from collections import OrderedDict
except ImportError, e:
    from ordereddict import OrderedDict

import re

from libsolace.SolaceNode import SolaceNode
from libsolace.util import d2x

class SolaceXMLBuilder(object):
    """

    Builds Solace's SEMP XML Configuration Commands

    Any dot-name-space calling of a instance of SolaceXMLBuilder will create
    nested dictionary named the same. These are converted to XML when the instance
    is represented as str.

    >>> a=SolaceXMLBuilder(version="soltr/6_2")
    >>> a.foo.bar.baz=2
    >>> str(a)
    '<rpc semp-version="soltr/6_2">\n<foo><bar><baz>2</baz></bar></foo></rpc>'

    """

    def __init__(self, description=None, **kwargs):
        self.__dict__ = OrderedDict()
        self.__setattr__ = None
        if description is not None:
            self.description=description
        self.version = kwargs.get("version", "soltr/6_0")

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
        return complete_xml

    def __call__(self, *args, **kwargs):
        return self.__dict__
