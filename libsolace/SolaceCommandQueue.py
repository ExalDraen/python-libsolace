import os
from lxml import etree
import logging

class SolaceCommandQueue:
    """ Solace Command Queue Class

    A simple queue which validates SEMP XML against correct version of xsd,
    and then puts returns the commands list object.

    """

    schema_files = {
        None: os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_6_0.xsd'),
        "soltr/6_0": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_6_0.xsd'),
        "soltr/6_2": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_6_2.xsd'),
        "soltr/7_0": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_7_0.xsd'),
        "soltr/7_1": os.path.join(os.path.dirname(__file__), 'data/semp-rpc-soltr_7_1.xsd')
    }

    def __init__(self, version="soltr/6_0"):
        """
        Initializes the queue as a list
        """
        schema_file = open(self.schema_files[version])
        schema_root = etree.XML(schema_file.read())
        schema = etree.XMLSchema(schema_root)
        self.parser = etree.XMLParser(schema=schema)
        self.commands = []

    def enqueue(self, command, primaryOnly=False, backupOnly=False, **kwargs):
        """ Validate and append a command onto the command list.

        :type command: SolaceXMLBuilder
        :param command: SEMP command to validate
        :return: None
        """
        
        logging.debug("command %s" % str(command))

        try:
            root = etree.fromstring(str(command), self.parser)
            logging.debug('XML Validated')
            self.commands.append(command)
        except:
            logging.error('XML failed to validate, the XML was:')
            logging.error(command)
            raise
