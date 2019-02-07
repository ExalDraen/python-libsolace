"""
a plugin for manipulating how objects are named to allow multiple homing within a single
appliance cluster.
"""

import logging

import libsolace
from libsolace.plugin import Plugin

"""
The default naming plugin
"""

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@libsolace.plugin_registry.register
class NamingStandard(Plugin):
    plugin_name = "NamingStandard"

    def solve(self, *args, **kwargs):
        """
        Given two args, "name" and "prefix", this plugin returns "prefix_name"

        :type args: list[str]
        :rtype: str

        """
        try:
            return "%s_%s" % (args[1], args[0])
        except:
            logger.error("Unable to resolve object name for: %s" % args)
            raise
