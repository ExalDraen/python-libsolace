"""
a plugin for sending metrics to OpenTSDB
"""

import logging
import sys

try:
    import potsdb as potsdb
except ImportError, e:
    print("You need to install potsdb")
    sys.exit(1)

import libsolace
from libsolace.plugin import Plugin
from libsolace.util import get_key_from_settings

"""

e.g.
PLUGINS:
    ...
    - libsolace.plugins.OpenTSDBClient
    ...

TSDB_HOST: localhost
TSDB_PORT: 4242
TSDB_QSIZE: 1000
TSDB_MPS: 100
"""


@libsolace.plugin_registry.register
class OpenTSDBClient(Plugin):
    """

    metrics_class = libsolace.plugin_registry('OpenTSDBClient', settings=settings)
    metrics = metrics_class(settings=settings)

    """
    plugin_name = "OpenTSDBClient"

    def __init__(self, settings=None, **kwargs):
        logging.debug("Configuring with settings: %s" % settings)
        self.settings = settings.__dict__  # type: dict
        self.host = get_key_from_settings("TSDB_HOST", self.settings, default="defiant")
        self.port = get_key_from_settings("TSDB_PORT", self.settings, default=4242)
        self.qsize = get_key_from_settings("TSDB_QSIZE", self.settings, default=1000)
        self.mps = get_key_from_settings("TSDB_MPS", self.settings, default=100)
        self.host_tag = False
        self.check_host = True

        # connect
        self.client = potsdb.Client(self.host, port=self.port, qsize=self.qsize, host_tag=self.host_tag,
                                    mps=self.mps, check_host=self.check_host)

    def send(self, key, value, **tags):
        """
        send('test.metric5', 100, extratag1='tagvalue', extratag2='tagvalue')

        :param key:
        :param value:
        :param tags:
        :return:
        """
        try:
            self.client.log(key, value, **tags)
        except Exception, e:
            logging.error(e.message)
            logging.error("Unable to send metrics")
