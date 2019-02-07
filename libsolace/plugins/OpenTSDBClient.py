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

"""
Simple opentsdb plugin

.. code-block:: none

    PLUGINS:
        ...
        - libsolace.plugins.OpenTSDBClient
        ...

    TSDB_HOST: localhost
    TSDB_PORT: 4242
    TSDB_QSIZE: 1000
    TSDB_MPS: 100

"""

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@libsolace.plugin_registry.register
class OpenTSDBClient(Plugin):
    """
    Similar to the influxdb client, but for opentsdb.

    Example:

    .. doctest::
        :options: +SKIP

            >>> from libsolace.settingsloader import settings
            >>> import libsolace
            >>> metrics_class = libsolace.plugin_registry('OpenTSDBClient', settings=settings)
            >>> metrics = metrics_class(settings=settings)

    """
    plugin_name = "OpenTSDBClient"

    def __init__(self, settings=None, **kwargs):
        logger.debug("Configuring with settings: %s" % settings)
        self.settings = settings
        self.host = settings.get("TSDB_HOST", "defiant")
        self.port = settings.get("TSDB_PORT", 4242)
        self.qsize = settings.get("TSDB_QSIZE", 1000)
        self.mps = settings.get("TSDB_MPS", 100)
        self.host_tag = False
        self.check_host = True

        # connect
        self.client = potsdb.Client(self.host, port=self.port, qsize=self.qsize, host_tag=self.host_tag,
                                    mps=self.mps, check_host=self.check_host)

    def send(self, measurement, data, **tags):
        """
        Send the metrics to opentsdb

        Example:

        .. doctest::
            :options: +SKIP

            >>> from libsolace.settingsloader import settings
            >>> import libsolace
            >>> metrics_class = libsolace.plugin_registry('OpenTSDBClient', settings=settings)
            >>> metrics = metrics_class(settings=settings)
            >>> metrics.send('somekey', 100, extratag1='tagvalue', extratag2='tagvalue')

        :param measurement: the key name
        :param data: the value
        :param tags:
        :return:
        """
        try:
            self.client.log(measurement, data, **tags)
        except Exception, ex:
            logger.error(ex.message)
            logger.error("Unable to send metrics")
