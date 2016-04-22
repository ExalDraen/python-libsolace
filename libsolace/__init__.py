import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    import subprocess
    __version__ = subprocess.Popen(['git', 'describe'], stdout=subprocess.PIPE).communicate()[0].rstrip()

__author__ = 'Kegan Holtzhausen <Kegan.Holtzhausen@unibet.com>'

__doc__ = """
libsolace is a python library to manage the configuration of Solace messaging appliances. This project has a modular
design which provides the basic features required to manage your Solace infrastructure.

## Basic Principles

Managed items within Solace are managed through Plugins. These plugins in general do not actually alter state on the
appliances, they tend to return single or multiple SEMP commands which can then be posted to the appliance.

SEMP requests that are created through plugins are validated against the appropriate XSD for the version of appliance being
managed.

Example:
```
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
client = SolaceAPI("dev")
# generate batch of commands to provision a ACL Profile
list_tuple_request = client.manage("SolaceACLProfile", name="myprofile", vpn_name="testvpn")
for req in list_tuple_request:
    api.rpc(str(req[0], **req[1])
# create only a profile
tuple_request = client.manage("SolaceACLProfile").new_acl(name="myprofile", vpn_name="dev_testvpn")
api.rpc(tuple_request)
```

"""

# registering the plugin system
from libsolace.plugin import Plugin
plugin_registry = Plugin()
