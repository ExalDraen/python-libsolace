"""
The settingsloader searches for a libsolace.yaml file in:

    - libsolace.yaml
    - /etc/libsolace/libsolace.yaml
    - /opt/libsolace/libsolace.yaml

The environment variable: :envvar:`LIBSOLACE_CONFIG` can also be used to specify another file. e.g

    LIBSOLACE_CONFIG="/tmp/my.yaml" ./bin/solace-provision.py ....

Examples:

    >>> from libsolace.settingsloader import settings
    >>> settings["CMDB_URL"]
    'http://mydomain.com/path'
"""

import logging
import os

import yaml

__author__ = 'johlyh'

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


primary_config = os.environ.get('LIBSOLACE_CONFIG', 'libsolace.yaml')

__yamlfiles__ = [
    "%s" % primary_config,
    '/etc/libsolace/libsolace.yaml',
    '/opt/libsolace/libsolace.yaml'
]

# defaults which are set / could not be present
defaults = {
    "UPDATE_MOCK_TESTS": False,
    "CMDB_URL": "http://someurl/site.xml",
    "CMDB_FILE": "provision-example.yaml",
    "CMDB_USER": "",
    "CMDB_PASS": "",
    "SOLACE_QUEUE_PLUGIN": "SolaceQueue"
}

# Choose the first file we find on disk; if we don't find anything we can't carry on so bail
existing = [f for f in __yamlfiles__ if os.path.exists(f)]
if len(existing) == 0:
    msg = "Failed to find libpipeline.yaml in any of these locations: %s" % ",".join(__yamlfiles__)
    raise Exception(msg)
yaml_file = existing[0]

# YAML file is assumed to contain a mapping (a dictionary)
logger.info("Using yaml file %s", yaml_file)
with open(yaml_file, 'r') as stream:
    settings = yaml.load(stream)

settings.update(defaults)
logger.debug("Yaml file loaded successfully")

logger.info("Loading plugins...")
for p in settings['PLUGINS']:
    try:
        __import__(p, globals())
    except Exception as e:
        logger.exception("Failed to import plugin %s", p)
        raise
