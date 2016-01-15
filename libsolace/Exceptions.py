from exceptions import Exception
# import logging

class MissingProperty(Exception):
    pass

    # missing_property = 'Undefined'
    #
    # def __init__(self, property, *args, **kwargs):
    #     logging.info("Init Exception")
    #     self.missing_property = property

    # def __get__(self, *args, **kwargs):
    #     raise Exception("Missing property %s" % args)
    #
    # def __call__(self, *args, **kwargs):
    #     raise Exception("Missing property %s" % args)
    #
    # def __repr__(self, *args, **kwargs):
    #     raise Exception("Missing property %s" % self.name)
    #
    # def __str__(self, *args, **kwargs):
    #     raise Exception("Missing property %s" % args)
    #
    # def __bytes__(self, *args, **kwargs):
    #     raise Exception("Missing property %s" % args)
    #
    # def __format__(self, *args, **kwargs):
    #     raise Exception("Missing property %s" % args)

    # def __getattr__(self, *args, **kwargs):
    #     raise Exception("Missing property %s" % self.missing_property)

    # def __new__(cls, *args, **kwargs):
    #     raise Exception("Missing property %s" % args)
