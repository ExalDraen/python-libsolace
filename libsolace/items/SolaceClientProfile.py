import logging
import libsolace
from libsolace.SolaceReply import SolaceReplyHandler
from libsolace.plugin import Plugin
from libsolace.SolaceCommandQueue import SolaceCommandQueue
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from libsolace.util import version_equal_or_greater_than
from libsolace.util import get_key_from_kwargs


@libsolace.plugin_registry.register
class SolaceClientProfile(Plugin):
    """Create / Manage client profiles

If only the `api` kwarg is passed, initializes in Query mode. Else name, vpn_name should be provided to enter
provision mode.

    :param api: The instance of SolaceAPI if not called from SolaceAPI.manage
    :param name: the name of the profile
    :param vpn_name: name of the VPN to scope the ACL to
    :param defaults: dictionary of defaults
    :param max_clients: max clients sharing a username connection limit
    :type api: SolaceAPI
    :type name: str
    :type vpn_name: str
    :type defaults: dict
    :type max_clients: int

Example 1:

```python
>>> import libsolace.settingsloader as settings
>>> import libsolace
>>> from libsolace.SolaceAPI import SolaceAPI
>>> clazz = libsolace.plugin_registry("SolaceClientProfile", settings=settings)
>>> api = SolaceAPI("dev")
>>> scp = clazz(settings=settings, api=api)
>>> client_dict = scp.get(api=api, name="default", vpn_name="default")
```

Example 2, using SolaceAPI.manage:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> scp = api.manage("SolaceClientProfile")
>>> client_dict = scp.get(api=api, name="default", vpn_name="default")
>>> list_xml = api.manage("SolaceClientProfile", name="myprofile", vpn_name="dev_testvpn").commands.commands
>>> for xml in list_xml:
>>>    api.rpc(str(xml[0]), **xml[1])
```

    """

    plugin_name = "SolaceClientProfile"

    defaults = {
        "max_clients": 1000
    }

    def __init__(self, *args, **kwargs):

        self.api = get_key_from_kwargs("api", kwargs)
        self.commands = SolaceCommandQueue(version=self.api.version)
        kwargs.pop("api")

        if kwargs == {}:
            return

        if not "name" in kwargs:
            logging.info("No name kwarg, assuming query mode")
            return

        self.name = get_key_from_kwargs('name', kwargs)
        self.vpn_name = get_key_from_kwargs('vpn_name', kwargs)
        self.defaults = get_key_from_kwargs('defaults', kwargs, default=self.defaults)
        self.max_clients = get_key_from_kwargs('max_clients', kwargs, default=self.defaults.get("max_clients"))

        if kwargs.get('options', None) is None:
            logging.warning(
                "No options passed, assuming you meant 'add', please update usage of this class to pass a OptionParser instance")
            self.new_client_profile(**kwargs)
            self.allow_consume(**kwargs)
            self.allow_send(**kwargs)
            self.allow_endpoint_create(**kwargs)
            self.allow_transacted_sessions(**kwargs)

    def get(self, **kwargs):
        """Returns a ClientProfile immediately

    :param name: name of the profile
    :param vpn_name: the name of the vpn to scope the request to
    :param details: more details?
    :type name: str
    :type vpn_name: str
    :type details: bool
    :return: dictionary representation of client profile

Example:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> scp = api.manage("SolaceClientProfile").get(name="default", vpn_name="default")
```
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        details = get_key_from_kwargs("details", kwargs, default=False)

        self.api.x = SolaceXMLBuilder("Get Client Profile", version=self.api.version)
        self.api.x.show.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.show.client_profile.vpn_name = vpn_name
        if details:
            self.api.x.show.client_profile.details
        # enqueue to validate
        self.commands.enqueue(self.api.x)

        return SolaceReplyHandler(self.api.rpc(str(self.api.x)))

    # @only_if_not_exists('get', 'rpc-reply.rpc.show.message-vpn.vpn')
    def new_client_profile(self, **kwargs):
        """Create a new client profile

Enqueues the semp request in self.commands and returns the SolaceXMLBuilder
instance.

    :param name: name of the profile
    :param vpn_name: the name of the vpn to scope the request to
    :type name: str
    :type vpn_name: str
    :return: dictionary representation of client profile

Example:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> str_xml = api.manage("SolaceClientProfile").new_client_profile(name="default", vpn_name="default")
```
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Create Client Profile", version=self.api.version)
        self.api.x.create.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.create.client_profile.vpn_name = vpn_name
        self.commands.enqueue(self.api.x)
        return self.api.x

    def delete(self, **kwargs):
        """Delete a client profile

    :param name: name of the profile
    :param vpn_name: the name of the vpn to scope the request to
    :type name: str
    :type vpn_name: str
    :return: SEMP request

Example:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> str_xml = api.manage("SolaceClientProfile").delete(name="default", vpn_name="default")
```
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        self.api.x = SolaceXMLBuilder("Delete Client Profile", version=self.api.version)
        self.api.x.no.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.no.client_profile.vpn_name = vpn_name
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_consume(self, **kwargs):
        """Allow consume permission

    :param name: name of the profile
    :param vpn_name: the name of the vpn to scope the request to
    :type name: str
    :type vpn_name: str
    :return: SEMP request

Example:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> str_xml = api.manage("SolaceClientProfile").allow_consume(name="default", vpn_name="default")
```
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow profile consume", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_guaranteed_message_receive
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_send(self, **kwargs):
        """Allow send permission

    :param name: name of the profile
    :param vpn_name: the name of the vpn to scope the request to
    :type name: str
    :type vpn_name: str
    :return: SEMP request

Example:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> str_xml = api.manage("SolaceClientProfile").allow_send(name="default", vpn_name="default")
```
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow profile send", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_guaranteed_message_send
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_endpoint_create(self, **kwargs):
        """Allow endpoint creation permission

    :param name: name of the profile
    :param vpn_name: the name of the vpn to scope the request to
    :type name: str
    :type vpn_name: str
    :return: SEMP request

Example:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> str_xml = api.manage("SolaceClientProfile").allow_endpoint_create(name="default", vpn_name="default")
```
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow profile endpoint create", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_guaranteed_endpoint_create
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_transacted_sessions(self, **kwargs):
        """Allow transaction sessions permission

    :param name: name of the profile
    :param vpn_name: the name of the vpn to scope the request to
    :type name: str
    :type vpn_name: str
    :return: SEMP request

Example:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> str_xml = api.manage("SolaceClientProfile").allow_transacted_sessions(name="default", vpn_name="default")
```
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Allow profile transacted sessions", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.message_spool.allow_transacted_sessions
        self.commands.enqueue(self.api.x)
        return self.api.x

    def set_max_clients(self, **kwargs):
        """Set max clients for profile

    :param name: name of the profile
    :param vpn_name: the name of the vpn to scope the request to
    :param max_clients: max number of clients
    :type name: str
    :type vpn_name: str
    :type max_clients: int
    :return: SEMP request

Example:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> str_xml = api.manage("SolaceClientProfile").set_max_clients(name="default", vpn_name="default", max_clients=500)
```
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)
        max_clients = get_key_from_kwargs("max_clients", kwargs)

        self.api.x = SolaceXMLBuilder("Setting Max Clients", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.max_connections_per_client_username.value = max_clients
        self.commands.enqueue(self.api.x)
        return self.api.x

    def allow_bridging(self, **kwargs):
        """Allow bridging

    :param name: name of the profile
    :param vpn_name: the name of the vpn to scope the request to
    :type name: str
    :type vpn_name: str
    :return: SEMP request

Example:

```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> api = SolaceAPI("dev")
>>> str_xml = api.manage("SolaceClientProfile").allow_bridging(name="default", vpn_name="default")
```
        """
        name = get_key_from_kwargs("name", kwargs)
        vpn_name = get_key_from_kwargs("vpn_name", kwargs)

        self.api.x = SolaceXMLBuilder("Setting Bridging", version=self.api.version)
        self.api.x.client_profile.name = name
        if version_equal_or_greater_than('soltr/6_2', self.api.version):
            self.api.x.client_profile.vpn_name = vpn_name
        self.api.x.client_profile.allow_bridge_connections
        self.commands.enqueue(self.api.x)
        return self.api.x
