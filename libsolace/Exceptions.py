from exceptions import Exception

__doc__ = """
Various exception classes, nothing much to see here. move along...
"""


class LoginException(Exception):
    pass


class MissingException(Exception):
    pass


class MissingProperty(MissingException):
    pass


class MissingClientUser(MissingException):
    pass


class MissingClientProfile(MissingException):
    pass


class MissingACLProfileException(MissingException):
    pass
