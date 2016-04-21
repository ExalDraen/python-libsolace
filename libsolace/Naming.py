import libsolace
import logging

__doc__ = """This method is responsible for handing off Naming work to the configured naming standard. The Plugin for the standard
is specified in the NAMEHOOK property of the libsolace.yaml file.

example while ZoinksNamingStandard set as NAMEHOOK in libsolace.yaml:
```python
>>> from libsolace.plugins.NamingStandard import name
>>> name("%s_something", "dev")
'dev_something'
```

example while DefaultNaming set as NAMEHOOK
```python
>>> name("something", "dev")
'dev_something'
```

"""

# plugin_name = "Naming"


def name(*args, **kwargs):
    """
    Passes off work to the plugin as specified by NAMEHOOK in libsolace.yaml. The plugin MUST have a solve() method
    which accepts args and kwargs. see NamingStandard.py and ZoinksNamingStandard.py

    :rtype: str
    """
    import libsolace.settingsloader as settings
    try:
        return libsolace.plugin_registry(settings.NAMEHOOK)().solve(*args, **kwargs)
    except Exception, e:
        logging.error("Unable to solve name of object, reason: %s %s" % (e.__class__, e.message))
        raise
