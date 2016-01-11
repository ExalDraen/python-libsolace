"""
a hook for manipulating how objects are named to allow multiple homing within a single
appliance cluster.
"""

import libsolace
from libsolace.plugin import Plugin

"""
This method is responsible for returning strings in the namingstandard.

example:
>>> from libsolace.plugins.NamingStandard import name
>>> name("something", "dev")
'dev_something'

"""
def name(name, environment):
    import libsolace.settingsloader as settings
    try:
        return libsolace.plugin_registry(settings.NAMEHOOK).solve(name, environment)
    except Exception, e:
        raise


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
