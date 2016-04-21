try:
    from collections import OrderedDict
except ImportError, e:
    from ordereddict import OrderedDict

import re


class SolaceNode:
    """
    A data node / leaf. recursive implemented creating keys on demand.
    """

    def __init__(self):
        self.__dict__ = OrderedDict()

    # cant have `-` in the key names, rewrite em.
    def __getattr__(self, name):
        name = re.sub("_", "-", name)
        try:
            return self.__dict__[name]
        except:
            self.__dict__[name] = SolaceNode()
            return self.__dict__[name]

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __call__(self, *args, **kwargs):
        return self.__dict__

    def __setattr__(self, name, value):
        name = re.sub("_", "-", name)
        self.__dict__[name] = value
