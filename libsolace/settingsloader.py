import yaml
import os
import logging
import sys

__author__ = 'johlyh'

primary_config = 'libsolace.yaml',

try:
    primary_config = os.environ['LIBSOLACE_CONFIG']
except Exception, e:
    pass

__yamlfiles__ = [
    "%s" % primary_config,
    '/etc/libsolace/libsolace.yaml',
    '/opt/libsolace/libsolace.yaml'
]
__doc__ = """
The settingsloader searches for a libsolace.yaml file in:

    - libsolace.yaml
    - /etc/libsolace/libsolace.yaml
    - /opt/libsolace/libsolace.yaml

The environment variable: :envvar:`LIBSOLACE_CONFIG` can also be used to specify another file. e.g

    LIBSOLACE_CONFIG="/tmp/my.yaml" ./bin/solace-provision.py ....

Examples:

    >>> import libsolace.settingsloader as settings
    >>> settings.CMDB_URL
    'http://mydomain.com/path'

"""

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

yaml_loaded = False

# defaults which are set / could not be present
defaults = {
    "UPDATE_MOCK_TESTS": False,
    "CMDB_URL": "http://someurl/site.xml",
    "CMDB_FILE": "provision-example.yaml",
    "CMDB_USER": "",
    "CMDB_PASS": "",
    "SOLACE_QUEUE_PLUGIN": "SolaceQueue"
}

for yaml_file in __yamlfiles__:
    if not os.path.exists(yaml_file):
        continue

    logger.info("Using yaml file %s" % yaml_file)
    stream = open(yaml_file, 'r')
    yaml_settings = yaml.load(stream)

    # set the defaults
    for default in defaults:
        logger.info("Setting default %s:%s" % (default, defaults[default]))
        globals()[default] = defaults[default]

    # TODO FIXME
    # get each plugins "default" variables and add to globals

    # get the real values if any
    for variable in yaml_settings.keys():
        logger.info("Setting config %s:%s" % (variable, yaml_settings[variable]))
        globals()[variable] = yaml_settings[variable]

    yaml_loaded = True
    logger.debug("Yaml loaded successful")

    logger.info("Loading plugins...")
    for p in globals()['PLUGINS']:
        try:
            __import__(p, globals())
        except Exception, e:
            logger.error("Failed to import plugin %s" % p)
            raise
    break

if yaml_loaded is False:
    msg = "Failed to find libpipeline.yaml in any of these locations: %s" % ",".join(__yamlfiles__)
    logger.error(msg)
    raise Exception(msg)

