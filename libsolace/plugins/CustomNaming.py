"""
a hook for manipulating how objects are named to allow multiple homing within a single
appliance cluster.
"""

import libsolace
from libsolace.plugin import Plugin

@libsolace.plugin_registry.register
class ZoinksNamingStandard(Plugin):
    plugin_name = "ZoinksNamingStandard"
    def solve(self, name, environment):
        try:
            return "zoinks_%s_%s" % ( environment, name)
        except TypeError, e:
            return name
