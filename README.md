# libsolace

## intro

this is a set of python helpers for managing solace appliances.

## limitations

* XML can only be validated if it passes through a SolaceCommandQueue instance.
* appliance responses are difficult to validate since the "slave" appliance will almost always return errors when NOT "active", and already existing CI's will throw a error on create events and so forth.
* since python dictionaries cannot contain `-` use `_`, the SolaceNode class will substitute a `-` as needed

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
connection = SolaceAPI('dev')
```

#### get_redundancy

returns the redundancy status of each node in the cluster.

#### get_memory

returns the memory usage of the appliance.

#### get_queue(queue, vpn, detail=False)

shows a queue in a vpn, optionally added detail

#### list_queues(vpn, queue_filter="*")

shows a list of queues in a vpn matching a queue_filter

#### get_client_username_queues(username, vpn_name)

return a list of queues owned by a specific user

#### is_client_username_inuse(client_username, vpn)

returns boolean if username is in-use or not

#### does_client_username_exist(client_username, vpn)

returns boolean if a user exists

#### is_client_username_enabled(client_username, vpn)

returns boolean is a client username within a vpn is enabled

#### get_client_username(clientusername, vpn, detail=False)

get a client username with details and or counts

#### get_client(client, vpn, detail=False)

get a client "session" stats with optional details

#### get_vpn(vpn, stats=False)

get a vpn info with optional stats

#### list_vpns(vpns)

returns list of vpns matching a filter

```sh
>>> connection.list_vpns('*keghol*')
[u'test_dev_keghol']
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

### Integration with a custom CMDB

You can implement your own integration with whatever CMDB you use.
See CMDBClient plugin class and associated libpipeline.yaml properties for plugins and CMDB.

#### get_vpns_by_owner(owner_name, **kwargs)

Returns all VPNS owned by a specific "owner".

Example of the results your implementation should return.
```json
[
   {
      env:[
         {
            name:'dev',
            vpn_config:{
               spool_size:'1024'
            }
         },
         {
            name:'pt1',
            vpn_config:{
               spool_size:'16384'
            }
         },
         {
            name:'prod',
            vpn_config:{
               spool_size:'16384'
            }
         }
      ],
      name:'%s_testvpn',
      owner:'SolaceTest',
      password:'d0nt_u5se_thIs',
      queue:[
         {
            env:[
               {
                  name:'pt1',
                  queue_config:{
                     exclusive:'true',
                     queue_size:'4096'
                  }
               },
               {
                  name:'prod',
                  queue_config:{
                     exclusive:'true',
                     queue_size:'4096'
                  }
               }
            ],
            name:'testqueue1',
            queue_config:{
               exclusive:'true',
               queue_size:'1024'
            }
         },
         {
            env:[
               {
                  name:'pt1',
                  queue_config:{
                     exclusive:'false',
                     queue_size:'4096'
                  }
               },
               {
                  name:'prod',
                  queue_config:{
                     exclusive:'false',
                     queue_size:'4096'
                  }
               }
            ],
            name:'testqueue2',
            queue_config:{
               exclusive:'false',
               queue_size:'1024'
            }
         }
      ],
      vpn_config:{
         spool_size:'4096'
      }
   }
]
```

#### get_users_of_vpn(vpn_name, **kwargs)

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

#### get_queues_of_vpn(vpn_name, **kwargs)

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
