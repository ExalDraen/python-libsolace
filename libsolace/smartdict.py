try:
    from collections import OrderedDict
except ImportError, e:
    from ordereddict import OrderedDict


class SmartDict:
    def __init__(self, *args, **kwargs):
        self.__dict__ = OrderedDict()

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except:
            self.__dict__[name] = SmartDict()
            return self.__dict__[name]

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __call__(self, *args, **kwargs):
        return self.__dict__

    def __setattr__(self, name, value):
        self.__dict__[name] = value
