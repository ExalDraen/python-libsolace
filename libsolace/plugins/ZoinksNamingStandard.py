"""
a hook for manipulating how objects are named to allow multiple homing within a single
appliance cluster.
"""

import logging
import libsolace
from libsolace.plugin import Plugin

"""
Example of a custom naming standard, load this up by specifying the module path to the
class FILENAME in PLUGINS key of libsolace.yaml

e.g.
PLUGINS:
    ...
    - mypackage.plugins.MyNamer
    ...

NAMEHOOK: MyNamer
"""


@libsolace.plugin_registry.register
class ZoinksNamingStandard(Plugin):
    plugin_name = "ZoinksNamingStandard"

    def solve(self, *args, **kwargs):
        logging.debug("Solving name for: %s" % str(args))
        try:
            return args[0] % args[1]
        except:
            logging.error("Unable to solve naming of object: %s" % args)
            raise
