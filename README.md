# libsolace

## intro
this is a set of python helpers for managing solace appliances.

## limitations

* XML can only be validated if it passes through a SolaceCommandQueue instance.
* Appliance responses are difficult to validate since the "slave" appliance will almost always return errors when not "active", and already existing CI's will throw a error on create events and so forth.
* since python dictionaries cannot contain `-` use `_`, and the SolaceNode class will substitute a `-` as needed

## install

you might need libyaml-devel or equivilant!

```
python setup.py install
```

## configuration
libsolace requires a `libsolace.yaml` file in order to know what environments exist and what appliances are part of those environments. A single appliance can be part of multiple environments.

the `libsolace.yaml` file is searched for in:

* 'libsolace.yaml'
*  '/etc/libsolace/libsolace.yaml'
* '/opt/libsolace/libsolace.yaml'

see `libsolace.yaml` for specifics.

## bin
see the `bin` directory for examples of various activities.

## Classes
### SolaceAPI
connects to an appliance *set* on the *environment* key.

```
import libsolace.settingsloader as settings
from libsolace.solace import SolaceAPI
connection = SolaceAPI('ci1')
```

### SolaceXMLBuilder
the builder is a cheat to construct XML string requests.  e.g.

```python
from libsolace.solacehelper import SolaceXMLBuilder
a=SolaceXMLBuilder(version="soltr/6_2")
a.foo.bar.baz=2
str(a)
'<rpc semp-version="soltr/6_2">\n<foo><bar><baz>2</baz></bar></foo></rpc>'
```

### SolaceCommandQueue
the command queue is handy for creating a sequential list of SolaceXMLBuilder commands, each command is *validated* against the Solace's SEMP XSD on *enqueue*.  e.g.

```python
queue = SolaceCommandQueue(version="soltr/6_2")
cmd = SolaceXMLBuilder("Creating Queue Foo", version="soltr/6_2")
cmd.message_spool.vpn_name = 'ci1_testvpn'
cmd.message_spool.create.queue.name='Foo'
queue.enqueue(cmd)
```

### Executing on Appliances

simply iterate over SolaceCommandQueue `commands` and call `rpc` on appliance connection.

```python
import libsolace.settingsloader as settings
from libsolace.solace import SolaceAPI
self.connection = SolaceAPI('ci1')
for cmd in queue.commands:
  self.connection.rpc(str(cmd))
```

## Site Management

Through some classes in `solacehelper.py` you can manage a simple set of configuration items in multiple datacenters or environments.  the `SolaceProvisionVPN` class can provision entire VPN's, Queues and Users. e.g.

```
result = SolaceProvisionVPN(vpn_datanode=vpn, environment=options.env, client_profile="glassfish", users=users)
```

see the following classes and methods:

* SolaceClientProfile
* SolaceACLProfile
* SolaceUser
* SolaceVPN
* SolaceQueue

### site.xml

VPNs are declared with a `<vpn>` tag in the `<solace>` tag of `site.xml`, each VPN **must** have its `owner` attribute set, the `owner` attribute is used as a key to select which VPNs will be provisioned. e.g.

`solace-provision.py -p EcoSystemA -e ci1 -f /path/to/site.xml`

VPN's are named with a special environment placeholder e.g. `%s_testvpn`. the literal `%s` will be replaced with `environment` name at provision time. the above command would create a vpn named: `ci1_testvpn` which has a owner key of  `EcoSystemA`.

Certain items can be overridden on a environment level in the `site.xml`, current supported items:

* queue queue_size
* vpn spool_size

and the environment_name is used to prefix all VPN names to avoid collision

## running
see ./bin/solace-provision.py

## extending

adding new functionality is done through `solacehelper.py`. see the SolaceProvisionVPN.
