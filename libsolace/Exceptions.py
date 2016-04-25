from exceptions import Exception


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