# libSolace

## Overview

This is a set of python helpers for managing and provisioning Solace Messaging Appliances and the VMR. The design is to be flexible
and aimed at managing multiple clusters in multiple environments.

### XML Generator

The core of this provisioning system is the SolaceXMLBuilder class which can generate XML through recursive instantiation of a dictionary like object. Example:

```python
    document = SolaceXMLBuilder(version="soltr/6_2")
    document.create.client_username.username = "myUserName"
    document.create.client_username.vpn_name = "dev_MyVPN"
    str(document)
'<rpc semp-version="soltr/6_2"><create><client-username><username>myUserName</username><vpn-name>dev_MyVPN</vpn-name></client-username></create></rpc>'
```


Plugins are written to create single SEMP commands or a list of SEMP commands in order to provision a specific object. Example:

```python
    connection = SolaceAPI("dev")
    # create the command for creating a new user via the "SolaceUser" plugin
    xml = connection.manage("SolaceUser").create_user(username="foo", vpn_name="bar")
<rpc semp-version="soltr/6_0"><create><client-username><username>foo</username><vpn-name>bar</vpn-name></client-username></create></rpc>
    # create the commands for a user and all related objects
    xmlList = connection.manage("SolaceUser",
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
    from libsolace.SolaceAPI import SolaceAPI
    conn = SolaceAPI("dev")
    conn.manage("SolaceUser").get(username="dev_testvpn", vpn_name="dev_testvpn")
{'reply': {u'show': {u'client-username': {u'client-usernames': {u'client-username': {u'profile': u'glassfish', u'acl-profile': u'dev_testvpn', u'guaranteed-endpoint-permission-override': u'false', u'client-username': u'dev_testvpn', u'enabled': u'true', u'message-vpn': u'dev_testvpn', u'password-configured': u'true', u'num-clients': u'0', u'num-endpoints': u'2', u'subscription-manager': u'false', u'max-connections': u'500', u'max-endpoints': u'16000'}}}}}}
```



### CMDB Configuration data and Naming Patterns

In my use case, each Solace Cluster could potentially host multiple 'environments', therefore ALL objects are created with a environment specific name to allow multi-homing.

e.g.:
    
    * dev_MyVPN
    * qa1_MyUsername
    * prod1_MyProfile
    * dev_MyACL

This means that any cluster can host any number of environments combined without conflicting resources. The CMDBClient contract states it must resolve the final item name by substituting the environment name into the string. 

e.g. '%s_myVpn' % env_name. 

This can be achieved through a Naming plugin. see <a href="libsolace/plugins/NamingStandard.py">NamingStandard</a> and
<a href="libsolace/plugins/ZoinksNamingStandard.py">ZoinksNamingStandard</a>

See <a href="libsolace/plugins/CMDBClient.py">CMDBClient</a> for a CMDB plugin example.


### Limitations

* XML can only be validated if it is enqueued in a SolaceCommandQueue instance.
* Appliance responses are difficult to validate since the "slave" appliance will almost always return errors when NOT "active", and already existing CI's will throw a error on create events and incorrect states. see
<a href="libsolace/Decorators.py">Decorators</a> for targeting specific appliances and states.
* Since python dictionaries cannot contain `-` use `_`, the SolaceNode class will substitute a `-` for a `_` and
vice-versa as needed on keyNames.

## Install

You might need libyaml-devel or equivilant for your OS.

For debian derivitaves this is:
libxslt1-dev 
libxml2-dev
python-dev

```sh
python setup.py install
```

## Configuration

libsolace requires a `libsolace.yaml` file in order to know what environments exist and what appliances are part of those environments. A single appliance can be part of multiple environments.

The `libsolace.yaml` file is searched for in:

* 'libsolace.yaml'
* '/etc/libsolace/libsolace.yaml'
* '/opt/libsolace/libsolace.yaml'

The configuration loader is also responsible for loading all plugins as specified in the PLUGINS key.

See <a href="libsolace.yaml.template">libsolace.yaml.template</a> for more info.

## Plugins

libsolace is pluggable, and you can register your own classes to customize the appliance management. You need to implement your own CMDBClient which should integrate with whatever configuration system you desire to populate solace.

See <a href="libsolace/plugins/CMDBClient.py">CMDBClient</a>
See <a href="libsolace/plugins/">All Plugins</a>
See <a href="libsolace/items/">Item Plugins</a>

## bin

See the `bin` directory for examples of various activities.

## Classes

Overview of some of the plugins and classes. Generally, you would initialize the solace API with:

```python
import libsolace.settingsloader as settings
import libsolace
from libsolace.SolaceAPI import SolaceAPI
client = SolaceAPI("dev")
xmls = client.manage(......)
for xml in xmls.commands.commands:
  c.rpc(str(xml))
```

### SolaceACLProfile

#### init
Calls new_acl, allow_publish, allow_subscribe and allow_connect, returns list of xml strings

```python
acl_profile_xml_list =  client.manage("SolaceACLProfile", name=self.vpn_name, vpn_name=self.vpn_name).commands.commands
```

#### new_acl
Returns single XML string required to create a new ACL

```python
str_xml=client.manage("SolaceACLProfile").new_acl(name="testprofile", vpn_name="myvpn")
```

#### allow_publish, allow_subscribe, allow_connect
Returns only the XML to allow a specific feature

```python
str_xml=client.manage("SolaceACLProfile").allow_publish(name="testprofile", vpn_name="myvpn")
```
### SolaceClientProfile

Plugin which can query and manages the creation of client profiles.

Plugin Manage Identifier: "SolaceClientProfile"


#### get
Returns a dictionary, or raises an exception if not found

```python
profile_dict = client.manage("SolaceClientProfile").get(name="profilename", vpn_name="vpnname")
```    

#### new_client_profile
Returns a single xml string

```python
new_client_profile_xml = client.manage("SolaceClientProfile")\
    .new_client_profile(\
        name="test",\
        vpn_name="qa1_myvpn"\
)
```
    
#### delete
Returns a single xml string

```python
delete_xml = client.manage("SolaceClientProfile")\
    .delete(\
        name="test",\ 
        vpn_name="qa1_myvpn"\
)
```

#### allow_consume
Returns a single xml string

```python
str_xml = client.manage("SolaceClientProfile").allow_consume(name="test", vpn_name="qa1_myvpn")
```

#### allow_send
Returns a single xml string


```python
str_xml = client.manage("SolaceClientProfile").allow_send(name="test", vpn_name="qa1_myvpn")
```

#### allow_endpoint_create
Returns a single xml string

```python
str_xml = client.manage("SolaceClientProfile").allow_consume(name="test", vpn_name="qa1_myvpn")
```

#### allow_transacted_sessions
Returns a single xml string

```python
str_xml = client.manage("SolaceClientProfile").allow_transacted_sessions(name="test", vpn_name="qa1_myvpn")
```

#### set_max_clients
Returns a single xml string

```python
str_xml = client.manage("SolaceClientProfile").set_max_clients(name="test", vpn_name="qa1_myvpn", max_clients=500)
```
#### allow_bridging
Returns a single xml string

```python
str_xml = client.manage("SolaceClientProfile").allow_bridging(name="test", vpn_name="qa1_myvpn")
```

### SolaceQueue

Plugin which can query and manages the creation of queues.

Plugin Manage Identifier: "SolaceQueue"

Get Queue Usage Example:


```python
queue_dict = client.manage("SolaceQueue").get(queue_name="testqueue1", vpn_name="dev_testvpn")
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
qcreate = connection.manage("SolaceQueue", vpn_name="dev_testvpn", queues=qlist)
for cmd in qcreate.commands.commands:
    # cmd is a tuple of the XML and "args"
	connection.rpc(str(cmd[0]), **cmd[1])
```

##### get
Returns queue(s) as a dict.

```python
q = client.manage("SolaceQueue").get(queue_name='*', vpn_name='dev_testvpn')
```


#### create_queue @only_if_not_exists
Returns a single xml string if queue does not exist!

```python
str_xml = client.manage("SolaceQueue").create_queue(queue_name="foo2", vpn_name="dev_testvpn")
```

#### shutdown_egress @only_if_exists @only_on_shutdown('q' OR 'b' OR True) @primary
Return XML to shutdown a queue egress.

```python
str_xml = client.manage("SolaceQueue").shutdown_egress(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True)
```

#### shutdown_ingress @only_if_exists @only_on_shutdown('q' OR 'b' OR True) @primary
Return XML to shutdown a queue ingress.

```python
str_xml = client.manage("SolaceQueue").shutdown_ingress(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True)
```

#### exclusive @only_if_exists @only_on_shutdown('q' OR 'b' OR True) @primary
Set exclusive to True / False for a queue. You need to STOP the queue before and START it after this.

```python
str_xml = client.manage("SolaceQueue").exclusive(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True, exclusive=True)
```

#### owner @only_if_exists @only_on_shutdown('q' OR 'b' OR True) @primary
Set the owner of a Queue. You need to STOP the queue before and START it after this.

```python
str_xml = client.manage("SolaceQueue")\
    .owner(vpn_name="dev_testvpn",\
           queue_name="testqueue1",\
           owner_username="dev_test_keghol",\
           shutdown_on_apply=True,\
           primaryOnly=True\
    )
```

#### max_bind_count @only_if_exists @primary
Limits the number of bindings on a queue. Recommended to limit misbehaving applications from consuming all sockets.

```python
str_xml = client.manage("SolaceQueue").max_bind_count(vpn_name="dev_testvpn", queue_name="testqueue1", max_bind_count=10)
```


#### consume @only_if_exists @only_on_shutdown('q' OR 'b' OR True) @primary
Set consume.

```python
str_xml = client.manage("SolaceQueue").consume(vpn_name="dev_testvpn", queue_name="testqueue1", consume="all", shutdown_on_apply=True)
```

#### spool_size @only_if_exists @primary
Set the spool size. Can be run hot!

```python
str_xml = client.manage("SolaceQueue").spool_size(vpn_name="dev_testvpn", queue_name="testqueue1", queue_size=1024)
```

#### retries @only_if_exists @primary
Set the number of delivery retries. Max 255

```python
str_xml = client.manage("SolaceQueue").retries(vpn_name="dev_testvpn", queue_name="testqueue1", retries=10)
```

#### enable @only_if_exists @primary
Enable a queue if its disabled.

```python
str_xml = client.manage("SolaceQueue").enable(vpn_name="dev_testvpn", queue_name="testqueue1")
```

#### reject_on_discard @only_if_exists @primary
Turn on notify producers of discard through rejection.

```python
str_xml = client.manage("SolaceQueue").reject_on_discard(vpn_name="dev_testvpn", queue_name="testqueue1")
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
    connection.list_vpns('*keghol*')
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
