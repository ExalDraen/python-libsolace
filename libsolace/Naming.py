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
