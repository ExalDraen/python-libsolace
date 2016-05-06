"""libsolace is a python library to manage the configuration of Solace messaging appliances. This project has a modular
design which provides the basic features required to manage pairs of Solace Appliances.

Basics
=========

    Managed objects within Solace are managed through :class:`plugin.Plugin`. Plugins are used to create SEMP requests,
    which can then be posted to the appliance through a :class:`SolaceAPI.SolaceAPI` instance.

    During the creation of SEMP requests, Plugins will enqueue the request in a instance of :class:`SolaceCommandQueue.SolaceCommandQueue`
    which will also validate the request against the appropriate XSD for the version of SolOS-TR the appliance is running.

Example:

    >>> import libsolace.settingsloader as settings
    >>> from libsolace.SolaceAPI import SolaceAPI
    >>> client = SolaceAPI("dev")
    >>> list_requests = client.manage("NullPlugin", foo="bar", baz="jaz")
    >>> type(list_requests)
    <class 'libsolace.items.NullPlugin.NullPlugin'>

"""

import pkg_resources


try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    import subprocess
    __version__ = subprocess.Popen(['git', 'describe'], stdout=subprocess.PIPE).communicate()[0].rstrip()

__author__ = 'Kegan Holtzhausen <Kegan.Holtzhausen@unibet.com>'


# registering the plugin system
from libsolace.plugin import Plugin

# the plugin registry instance
plugin_registry = Plugin()
