from exceptions import Exception


class MissingException(Exception):
    pass


class MissingProperty(MissingException):
    pass


class MissingClientUser(MissingException):
    pass
