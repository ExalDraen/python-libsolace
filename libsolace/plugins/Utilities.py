import logging

import libsolace
from libsolace.plugin import Plugin
from libsolace.util import get_key_from_kwargs, get_key_from_settings
from libsolace.SolaceCommandQueue import SolaceCommandQueue

"""
General tools plugins
"""


@libsolace.plugin_registry.register
class Utilities(Plugin):
    plugin_name = "Utilities"
    settings = None

    def __init__(self, **kwargs):
        """
        General tools plugin, invoke as any other plugin. May have dependencies to other plugins.

        :param api: the SolaceAPI instance, settings object will be used from SolaceAPI.
        :param kwargs:
        :return:
        """
        self.api = get_key_from_kwargs('api', kwargs)
        self.commands = SolaceCommandQueue(version=self.api.version)
        self.settings = self.api.settings
        self.SOLACE_QUEUE_PLUGIN = get_key_from_settings("SOLACE_QUEUE_PLUGIN", self.settings.__dict__)
        self.SOLACE_USER_PLUGIN = get_key_from_settings("SOLACE_USER_PLUGIN", self.settings.__dict__)

    def get_user_queues(self, client_username, vpn_name):
        """
        Get all queues and return filtered list of only queues who's owner matches the username

        Example:

            >>> connection = SolaceAPI("dev")
            >>> results = connection.manage("Utilities").get_user_queues("dev_testproductA", "dev_testvpn")
            >>> results
            [u'testqueue1']

        :param username: username to filter on
        :param vpn_name: vpn to filter on
        :return:
        """

        result = []

        response = self.api.manage(self.SOLACE_QUEUE_PLUGIN).get(queue_name='*', vpn_name=vpn_name,
                                                                 detail=True)[0]['rpc-reply']['rpc']['show']['queue']['queues']['queue']

        try:
            for h in response:
                o = h['info']['owner']
                logging.debug("Owner: %s" % o)
                if o == client_username:
                    logging.info("Matched Queue: %s", h['name'])
                    result.append(h['name'])
        except KeyError, e:
            raise Exception(
                    "While getting list of queues from get_queue() the response did not contain the expected data. VPN:"
                    " %s. Exception message: %s" % (
                        vpn_name, str(e)))
        else:
            return result

    def is_client_user_inuse(self, client_username, vpn_name):
        """
        Returns boolean if client username has client

        Example:
            >>> connection = SolaceAPI("dev")
            >>> results = connection.manage("Utilities").is_client_user_inuse("dev_testproductA", "dev_testvpn")
            >>> results
            True

        """
        result = []

        try:
            data = self.api.manage(self.SOLACE_USER_PLUGIN).get(client_username=client_username, vpn_name=vpn_name,
                                                                detail=True)
            response = data[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']['num-clients']

        except KeyError, e:
            logging.debug("Key does not exist, this normally means there was no user matching the filter")
            logging.debug(data)
            return False

        except Exception, e:
            logging.warn("Error decoding response keys in %s" % data)
            logging.warn(e.message)
            raise

        if int(response) > 0:
            logging.info("User %s is in-use, %s sessions open" % (client_username, response))
            return True
        else:
            logging.info("User %s is NOT in-use, %s sessions open" % (client_username, response))
            return False

    def is_client_user_enabled(self, client_username, vpn_name):
        """
        Returns boolean if client username has client connections

        Example:
            >>> connection = SolaceAPI("dev")
            >>> t = connection.rpc(connection.manage("SolaceUser").no_shutdown(client_username="dev_testproductA", vpn_name="dev_testvpn", force=True))
            >>> results = connection.manage("Utilities").is_client_user_enabled("dev_testproductA", "dev_testvpn")
            >>> results
            True

        """
        result = []
        response = self.api.manage(self.SOLACE_USER_PLUGIN).get(client_username=client_username, vpn_name=vpn_name,
                                                                detail=True)[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames']['client-username']['num-clients']
        if int(response) > 0:
            logging.info("User %s is in-use, %s sessions open" % (client_username, response))
            return True
        else:
            logging.info("User %s is NOT in-use, %s sessions open" % (client_username, response))
            return False