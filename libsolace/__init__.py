import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    import subprocess
    __version__ = subprocess.Popen(['git', 'describe'], stdout=subprocess.PIPE).communicate()[0].rstrip()

__author__ = 'Kegan Holtzhausen <Kegan.Holtzhausen@unibet.com'

__doc__ = """
libsolace is a python library to manage the configuration of Solace messaging appliances. This project has a modular
design which provides the basic features required to manage your Solace infrastructure.
"""

# registering the plugin system
from libsolace.plugin import Plugin
plugin_registry = Plugin()
