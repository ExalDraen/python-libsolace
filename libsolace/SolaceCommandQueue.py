import logging
import os

from lxml import etree

from libsolace.plugin import PluginResponse

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SolaceCommandQueue:
    """ Solace Command Queue Class

    A simple queue which validates SEMP XML against correct version of xsd,
    and then puts returns the commands list object.

    """

    schema_files = {
        None: os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_6_0.xsd'),
        "soltr/6_0": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_6_0.xsd'),
        "soltr/6_1": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_6_2.xsd'),
        "soltr/6_2": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_6_2.xsd'),
        "soltr/7_0": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_7_0.xsd'),
        "soltr/7_1_1": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_7_1.xsd')
    }

    def __init__(self, version="soltr/6_0"):
        """
        Initializes the queue as a list
        """
        logger.debug("Init with soltr version: %s" % version)
        try:
            schema_file = open(self.schema_files[version])
        except KeyError:
            logger.info("SolOS version '%s' unknown, falling back to latest known schema", version)
            schema_file = open(self.schema_files["soltr/7_1_1"])
        schema_root = etree.XML(schema_file.read())
        schema = etree.XMLSchema(schema_root)
        self.parser = etree.XMLParser(schema=schema)
        self.commands = []
        self.commandsv2 = []  # list or tuples ( command, kwargs )

    def enqueue(self, command, **kwargs):
        """ Validate and append a command onto the command list.

        :type command: SolaceXMLBuilder
        :param command: SEMP command to validate
        :return: None
        """

        # support being passed a PluginResponse
        if isinstance(command, PluginResponse):
            kwargs = command.kwargs
            command = command.xml

        logger.info("command %s" % str(command))
        logger.debug("kwargs: %s" % kwargs)

        try:
            root = etree.fromstring(str(command), self.parser)
            logger.debug('XML Validated')
            self.commands.append((command, kwargs))
        except:
            logger.error('XML failed to validate, the XML was: %s' % str(command))
            logger.error(command)
            raise

    def enqueueV2(self, command, **kwargs):
        """ Validate and append a command onto the command list.

        :type command: SolaceXMLBuilder
        :type kwargs: kwargs
        :param command: SEMP command to validate
        :param kwargs: primaryOnly = True, backupOnly = True
        :return: None
        """

        logger.debug("command %s" % str(command))
        logger.debug("kwargs: %s" % kwargs)

        try:
            root = etree.fromstring(str(command), self.parser)
            logger.debug('XML Validated')
            self.commands.append((command, kwargs))
        except:
            logger.error('XML failed to validate, the XML was:')
            logger.error(command)
            raise
