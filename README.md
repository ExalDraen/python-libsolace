# libSolace

## Overview

This is a set of python helpers for managing and provisioning Solace Messaging Appliances. The design is to be flexible
and aimed at managing multiple clusters in multiple environments.

### XML Generator

The core of this provisioning system is the SolaceXMLBuilder class which can generate XML through recursive instantiation
of a dictionary like object. Example:

```python
>>> document = SolaceXMLBuilder(version="soltr/6_2")
>>> document.create.client_username.username = "myUserName"
>>> document.create.client_username.vpn_name = "dev_MyVPN"
>>> str(document)
'<rpc semp-version="soltr/6_2"><create><client-username><username>myUserName</username><vpn-name>dev_MyVPN</vpn-name></client-username></create></rpc>'
```


Plugins are written to create single SEMP commands or a list of SEMP commands in order to provision a specific object. Example:

```python
>>> connection = SolaceAPI("dev")
>>> # create the command for creating a new user via the "SolaceUser" plugin
>>> xml = connection.manage("SolaceUser").create_user(username="foo", vpn_name="bar")
<rpc semp-version="soltr/6_0"><create><client-username><username>foo</username><vpn-name>bar</vpn-name></client-username></create></rpc>
>>> # create the commands for a user and all related objects
>>> xmlList = connection.manage("SolaceUser",
		      username='dev_myUser',
			  password='myPassword',
			  vpn_name='dev_MyVPN',
			  acl_profile='dev_MyVPN',
			  client_profile='glassfish').commands.commands
[ list of XML documents to POST to `dev` appliances ]
```

The SolaceXMLBuilder is typically used through the SolaceAPI, which will take
care to detect the appliance OS version for you. e.g.

```python
>>> from libsolace.SolaceAPI import SolaceAPI
>>> conn = SolaceAPI("dev")
>>> conn.manage("SolaceUser").get(username="dev_testvpn", vpn_name="dev_testvpn")
{'reply': {u'show': {u'client-username': {u'client-usernames': {u'client-username': {u'profile': u'glassfish', u'acl-profile': u'dev_testvpn', u'guaranteed-endpoint-permission-override': u'false', u'client-username': u'dev_testvpn', u'enabled': u'true', u'message-vpn': u'dev_testvpn', u'password-configured': u'true', u'num-clients': u'0', u'num-endpoints': u'2', u'subscription-manager': u'false', u'max-connections': u'500', u'max-endpoints': u'16000'}}}}}}
```



### CMDB Configuration data and Naming Patterns

In my use case, each Solace Cluster could potentially host multiple 'environments', therefore ALL objects are created
with a environment specific name to allow multi-homing.

e.g.:
    * dev_MyVPN
    * qa1_MyUsername
    * prod1_MyProfile
    * dev_MyACL

This means that any cluster can host any number of environments combined without conflicting resources. The CMDBClient
must resolve the final item name by substituting the environment name into the string. e.g. '%s_myVpn' % env_name. This
can be achieved through the Naming plugin. see <a href="libsolace/plugins/NamingStandard.py">NamingStandard</a> and 
<a href="libsolace/plugins/ZoinksNamingStandard.py">ZoinksNamingStandard</a>

See <a href="libsolace/plugins/CMDBClient.py">CMDBClient</a> for a CMDB plugin example.


### Limitations

* XML can only be validated if it is enqueued in a SolaceCommandQueue instance.
* Appliance responses are difficult to validate since the "slave" appliance will almost always return errors when NOT 
"active", and already existing CI's will throw a error on create events and incorrect states. see 
<a href="libsolace/Decorators.py">Decorators</a> for targeting specific appliances and states.
* Since python dictionaries cannot contain `-` use `_`, the SolaceNode class will substitute a `-` for a `_` and 
vice-versa as needed on keyNames.

## Install

You might need libyaml-devel or equivilant for your OS.

```
python setup.py install
```

## Configuration

libsolace requires a `libsolace.yaml` file in order to know what environments exist and what appliances are part of 
those environments. A single appliance can be part of multiple environments.

The `libsolace.yaml` file is searched for in:

* 'libsolace.yaml'
* '/etc/libsolace/libsolace.yaml'
* '/opt/libsolace/libsolace.yaml'

The configuration loader is also responsible for loading all plugins as specified in the PLUGINS key.

See <a href="libsolace.yaml.template">libsolace.yaml.template</a> for more info.

## Plugins

libsolace is pluggable, and you can register your own classes to customize the appliance management. You need to 
implement your own CMDBClient which should integrate with whatever configuration system you desire to populate solace.

See <a href="libsolace/plugins/CMDBClient.py">CMDBClient</a>
See <a href="libsolace/plugins/">All Plugins</a>
See <a href="libsolace/items/">Item Plugins</a>

## bin

See the `bin` directory for examples of various activities.

## Classes

### SolaceACLProfile

### SolaceClientProfile

### SolaceQueue

Plugin which can query and manages the creation of queues.

Plugin Manage Identifier: "SolaceQueue"

Get Queue Usage Example:


```python
from libsolace.SolaceAPI import SolaceAPI
connection = SolaceAPI('dev')
connection.manage("SolaceQueue").get(queue_name="testqueue1", vpn_name="dev_testvpn")
{'reply': {'show': {'queue': {'queues': {'queue': {'info': {'num-messages-spooled': '0', 'message-vpn': 'dev_testvpn', 'egress-config-status': 'Up', 'egress-selector-present': 'No', 'network-topic': '#P2P/QUE/v:solace1/testqueue1', 'owner': 'dev_testvpn', 'max-bind-count': '1000', 'endpt-id': '2134', 'access-type': 'exclusive', 'event': {'event-thresholds': [{'clear-value': '600', 'clear-percentage': '60', 'set-percentage': '80', 'name': 'bind-count', 'set-value': '800'}, {'clear-value': '2457', 'clear-percentage': '60', 'set-percentage': '80', 'name': 'spool-usage', 'set-value': '3276'}, {'clear-value': '0', 'clear-percentage': '60', 'set-percentage': '80', 'name': 'reject-low-priority-msg-limit', 'set-value': '0'}]}, 'total-delivered-unacked-msgs': '0', 'durable': 'true', 'max-redelivery': '0', 'created-by-mgmt': 'Yes', 'max-message-size': '10000000', 'topic-subscription-count': '0', 'type': 'Primary', 'ingress-config-status': 'Up', 'bind-time-forwarding-mode': 'Store-And-Forward', 'quota': '4096', 'reject-low-priority-msg-limit': '0', 'others-permission': 'Consume (1100)', 'current-spool-usage-in-mb': '0', 'reject-msg-to-sender-on-discard': 'Yes', 'max-delivered-unacked-msgs-per-flow': '250000', 'bind-count-threshold-high-percentage': '80', 'bind-count-threshold-high-clear-percentage': '60', 'low-priority-msg-congestion-state': 'Disabled', 'respect-ttl': 'No', 'high-water-mark-in-mb': '0', 'total-acked-msgs-in-progress': '0', 'bind-count': '0'}, 'name': 'testqueue1'}}}}}}
```

Create Queue Example:


```python
# list of queues we want to create
qlist = []
# a queue we will place in the list
queue1 = {}
queue1['queue_config'] = {}
queue1['queue_config']["exclusive"] = "true"
queue1['queue_config']["queue_size"] = "4096"
queue1['queue_config']["retries"] = 0
queue1['queue_config']['max_bind_count'] = 1000
queue1['queue_config']['owner'] = "dev_myUsername"
queue1['queue_config']["consume"] = "all"
queue1["name"] = "testqueue1"
# add the queue to the list
qlist.append(queue1)
# connect to the appliance
connection = SolaceAPI('dev')
qcreate = connection.manage("SolaceQueue", vpn_name="dev_testvpn", queues = qlist)
for cmd in qcreate.commands.commands:
	connection.rpc(str(cmd))

```


### SolaceUsers

User management plugin creates multiple users at once.

Plugin Manage Identifier: "SolaceUsers"



### SolaceVPN

Plugin which manages the creation of a VPN.

Plugin Manage Identifier: "SolaceVPN"

Usage Example:

```python
connection = SolaceAPI('dev')
vpn = conn.manage("SolaceVPN", vpn_name="foo", max_spool_usage=1024)
for cmd in vpn.commands.commands:
	connection.rpc(str(cmd))
```



### SolaceAPI

Connects to an appliance *cluster* on the *environment* key. Upon connection the
SolOS-TR version is detected and the appropriate language level is set.

```python
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
connection = SolaceAPI('dev')
```

#### manage

Returns a plugin instance

```python
conn = SolaceAPI('dev')
vpn = conn.manage("SolaceVPN", vpn_name="foo", owner_name="Someguy", max_spool_usage=1024)
for cmd in vpn.commands.commands:
	conn.rpc(str(cmd))
```

#### get_redundancy

Returns the redundancy status of each node in the cluster.

#### get_memory

Returns the memory usage of the appliance.

#### get_queue(queue, vpn, detail=False)

Shows a queue in a vpn, optionally added detail

#### list_queues(vpn, queue_filter="*")

Shows a list of queues in a vpn matching a queue_filter

#### get_client_username_queues(username, vpn_name)

Return a list of queues owned by a specific user

#### is_client_username_inuse(client_username, vpn)

Returns boolean if username is in-use or not

#### does_client_username_exist(client_username, vpn)

Returns boolean if a user exists

#### is_client_username_enabled(client_username, vpn)

Returns boolean is a client username within a vpn is enabled

#### get_client_username(clientusername, vpn, detail=False)

Get a client username with details and or counts

#### get_client(client, vpn, detail=False)

Get client "session" stats with optional details

#### get_vpn(vpn, stats=False)

Get a VPN info with optional stats

#### list_vpns(vpns)

Returns list of vpns matching a filter

```sh
>>> connection.list_vpns('*keghol*')
[u'test_dev_keghol']
```

### SolaceXMLBuilder
The builder is a cheat to construct XML string requests.  e.g.

```python
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
xml=SolaceXMLBuilder(version="soltr/6_2")
xml.foo.bar.baz=2
str(xml)
'<rpc semp-version="soltr/6_2">\n<foo><bar><baz>2</baz></bar></foo></rpc>'
```

### SolaceCommandQueue

The command queue is handy for creating a sequential list of SolaceXMLBuilder commands, each command is *validated* against the Solace's SEMP XSD when *enqueue* is called.

```python
queue = SolaceCommandQueue(version="soltr/6_2")
cmd = SolaceXMLBuilder("Creating Queue Foo", version="soltr/6_2")
cmd.message_spool.vpn_name = 'ci1_testvpn'
cmd.message_spool.create.queue.name='Foo'
queue.enqueue(cmd)
```

### Executing on Appliances

In order to run actual provisioning commands, iterate over SolaceCommandQueue  instance's `commands` and call `rpc` on the SolaceAPI connection instance.

```python
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
connection = SolaceAPI('ci1')
for cmd in queue.commands:
  connection.rpc(str(cmd))
```

## Site Management

You can manage a simple set of configuration items in multiple datacenters or environments utilizing the `SolaceProvisionVPN` class, which  can provision entire VPN's, Queues, Profiles and Users. e.g.

```
SolaceProvision(vpn_dict=vpn, queue_dict=queues, environment="dev", client_profile="glassfish", users=users)
```

See the following classes and methods:

* SolaceClientProfile
* SolaceACLProfile
* SolaceUser
* SolaceVPN
* SolaceQueue

### site.xml ( legacy )

**The XML provisioning schema is legacy, it will be replaced with a JSON-only version going forward.**

VPNs can be declared with a `<vpn>` tag in the `<solace>` tag of `site.xml`, each VPN **must** have its `owner` attribute set, the `owner` attribute is used as a key to select which VPNs will be provisioned. e.g.

`solace-provision.py -p EcoSystemA -e ci1 -f /path/to/site.xml`

VPN's are named with a special environment placeholder e.g. `%s_testvpn`. the literal `%s` will be replaced with `environment` name at provision time. the above command would create a vpn named: `ci1_testvpn` which has a owner key of  `EcoSystemA`.

Certain items can be overridden on a environment level in the `site.xml`, current supported items:

* queue's queue_size
* vpn's spool_size

The environment_name is used to prefix **all** VPN names, User names, Profile names and ACL names in order to avoid collisions. This facilitates multi-environment setups to share appliances, and still maintain a certain degree of isolation.

### Integration with a custom CMDB

You should implement your own integration with whatever CMDB you use.
See CMDBClient plugin *class* and associated libpipeline.yaml properties for plugin structure and how to configure libsolace to use it.

Any CMDB implementation must implement the following methods as part of the contract.

#### configure(settings=None, **kwargs)

#### get_vpns_by_owner(owner_name, environment='dev', **kwargs)

Returns all VPNS owned by a specific "owner".

See CMDBClient for example.

#### get_users_of_vpn(vpn_name, environment='dev', **kwargs)

```json
[  
   {  
      'username':'%s_testproductA',
      'password':'passwordX'
   },
   {  
      'username':'%s_testproductB',
      'password':'passwordX'
   }
]
```

#### get_queues_of_vpn(vpn_name, environment='dev', **kwargs)

```json
[
           {
              "exclusive":"true",
              "type":"",
              "name":"testqueue1",
              "queue_size":"4096"
           },
           {
              "exclusive":"false",
              "type":"",
              "name":"testqueue2",
              "queue_size":"4096"
           }
        ]
```


## running
see ./bin/solace-provision.py

## extending

adding new functionality is done through `solacehelper.py`. see the SolaceProvisionVPN.
