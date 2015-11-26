import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    import subprocess
    __version__ = subprocess.Popen(['git', 'describe'], stdout=subprocess.PIPE).communicate()[0].rstrip()

__author__ = 'Kegan Holtzhausen <Kegan.Holtzhausen@unibet.com'

# registering the plugin system
from libsolace.plugin import Plugin
plugin_registry = Plugin()
