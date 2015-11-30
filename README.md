# libSolace

## Changelog

* Customizable CMDB API supporting XML / JSON / Custom backends
* Plugable CMDB API loading
* Separated classes for each Configurable Item 
	* SolaceClientProfile
	* SolaceACLProfile
	* SolaceQueue
	* SolaceUser
	* SolaceVPN

## Intro

This is a set of python helpers for managing Solace Messaging Appliances. The design is to be flexible and aimed at managing multiple clusters in multiple environments. 

### Design Patterns

In my requirements, each Solace cluster could potentially host multiple 'environments', so ALL objects are created with environment specific names. 

e.g.:
* development_MyVPN
* development_MyUsername
* development_MyProfile
* development_MyACL

This means that any cluster can host any number of environments combined without conflicting resources. Therefore, whenever you see '%s' in the name of a VPN, User or Profile, it will be substituted with the environment name at provision time. 

### XML Generator

The core of this provisioning system is the SolaceXMLBuilder class which can conjur up any XML code through recursive instantation of a speclial object. So if you want to create a new user within solace, you can do it with:

```python
>>> document=SolaceXMLBuilder(version="soltr/6_2")
>>> document.create.client_username.username = "myUserName"
>>> document.create.client_username.vpn_name = "dev_MyVPN"
>>> str(document)
'<rpc semp-version="soltr/6_2"><create><client-username><username>myUserName</username><vpn-name>dev_MyVPN</vpn-name></client-username></create></rpc>'
```

If you want to create a new user and set the password, acl profile and client profile, you can use the SolaceUser class:

```python
>>> from libsolace.items.SolaceUser import SolaceUser
>>> documents = SolaceUser('dev', '%s_myUser', 'myPassword', '%s_MyVPN', acl_profile='%s_MyVPN', client_profile='%s_glassfish')
>>> documents.commands.commands
[ list of XML documents to POST to `dev` appliances ]
```


## TODO FIXME

* optional environment name substitusion
* Item's are plugins ( version aware )


## Limitations

* XML can only be validated if it passes through a SolaceCommandQueue instance.
* appliance responses are difficult to validate since the "slave" appliance will almost always return errors when NOT "active", and already existing CI's will throw a error on create events and so forth.
* since python dictionaries cannot contain `-` use `_`, the SolaceNode class will substitute a `-` as needed

## Install

You might need libyaml-devel or equivilant!

```
python setup.py install
```

## Configuration

libSolace requires a `libsolace.yaml` file in order to know what environments exist and what appliances are part of those environments. A single appliance can be part of multiple environments.

the `libsolace.yaml` file is searched for in:

* 'libsolace.yaml'
*  '/etc/libsolace/libsolace.yaml'
* '/opt/libsolace/libsolace.yaml'

see `libsolace.yaml` for specifics.

## bin

see the `bin` directory for examples of various activities.

## Classes

### SolaceAPI

Connects to an appliance *cluster* on the *environment* key.

```
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
connection = SolaceAPI('dev')
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
