"""
a hook for manipulating how objects are named to allow multiple homing within a single
appliance cluster.
"""

import libsolace
from libsolace.plugin import Plugin


"""
The default naming plugin
"""
@libsolace.plugin_registry.register
class DefaultNaming(Plugin):
    plugin_name = "DefaultNaming"
    def solve(self, name, environment):
        try:
            return "%s_%s" % ( environment, name)
        except TypeError, e:
            return name
