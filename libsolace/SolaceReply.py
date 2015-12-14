import logging
import re

class SolaceReplyHandler:
    """
    Solace reply handler, pass a SolaceAPI replies into this for easier handling
    of the dict structures.

    TODO FIXME: add primary / backup only support somehow, now its just mapping
    the data in the first nodes response and ignoring the second, potentially
    ignoring the "primary" if its NOT the 1st host in the "MGMT" config

    Example:
        >>> srh = SolaceReplyHandler([{'HOST': 'http://solace2/SEMP', u'rpc-reply': {u'rpc': {u'show': {u'client-username': {u'client-usernames': {u'client-username': {u'profile': u'glassfish', u'acl-profile': u'dev_testvpn', u'max-endpoints': u'16000', u'client-username': u'dev_testvpn', u'enabled': u'true', u'message-vpn': u'dev_testvpn', u'password-configured': u'true', u'num-clients': u'0', u'num-endpoints': u'2', u'subscription-manager': u'false', u'max-connections': u'500', u'guaranteed-endpoint-permission-override': u'false'}}}}}, u'execute-result': {u'@code': u'ok'}, u'@semp-version': u'soltr/6_0'}}])
        >>> str(srh.reply.show.client_username.client_usernames.client_username.profile)
        'glassfish'
    """
    def __init__(self, document=None, version="soltr/6_0", **kwargs):
        # if version == "soltr/6_0" or version == "soltr/6_1" or version == "soltr/6_2" or version == "soltr/7_0" or version == "soltr/7_1_1":
        self.reply = SolaceReply(document.pop()['rpc-reply']['rpc'])

class SolaceReply:
    """ Create a "dot-name-space" navigable object from a dictionary """

    def __init__(self, document):
        for k in document:
            logging.info("%s: %s" % (k, document[k]))
            try:
                self.__dict__[k] = SolaceReply(document[k])
            except:
                logging.info("Final value %s" % document[k])
                self.__dict__[k] = document[k]

    # cant have `-` in the key names, rewrite em.
    def __getattr__(self, name):
        logging.info(self.__dict__)
        name = re.sub("_", "-", name)
        try:
            return self.__dict__[name]
        except:
            raise

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __call__(self, *args, **kwargs):
        return self.__dict__

    def __setattr__(self, name, value):
        # name = re.sub("_", "-", name)
        logging.info("Setting key %s" % name)
        self.__dict__[name] = value


if __name__ == "__main__":
    import doctest
    import logging
    import sys
    logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
    logging.getLogger().setLevel(logging.INFO)
    doctest.testmod()