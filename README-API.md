# libsolace

libsolace is a python library to manage the configuration of Solace messaging appliances. This project has a modular
design which provides the basic features required to manage your Solace infrastructure.

Table of Contents
=================


* [SolaceACLProfile](#solaceaclprofile)
   * [allow_connect](#solaceaclprofile.allow_connect)
   * [allow_publish](#solaceaclprofile.allow_publish)
   * [allow_subscribe](#solaceaclprofile.allow_subscribe)
   * [new_acl](#solaceaclprofile.new_acl)
   * [register](#solaceaclprofile.register)
   * [set_exists](#solaceaclprofile.set_exists)
* [SolaceUser](#solaceuser)
   * [check_acl_profile_exists](#solaceuser.check_acl_profile_exists)
   * [check_client_profile_exists](#solaceuser.check_client_profile_exists)
   * [create_user](#solaceuser.create_user)
   * [delete](#solaceuser.delete)
   * [get](#solaceuser.get)
   * [no_guarenteed_endpoint](#solaceuser.no_guarenteed_endpoint)
   * [no_shutdown](#solaceuser.no_shutdown)
   * [no_subscription_manager](#solaceuser.no_subscription_manager)
   * [register](#solaceuser.register)
   * [requirements](#solaceuser.requirements)
   * [set_acl_profile](#solaceuser.set_acl_profile)
   * [set_client_profile](#solaceuser.set_client_profile)
   * [set_exists](#solaceuser.set_exists)
   * [set_password](#solaceuser.set_password)
   * [shutdown](#solaceuser.shutdown)
* [SolaceUsers](#solaceusers)
   * [_tests](#solaceusers._tests)
   * [check_acl_profile_exists](#solaceusers.check_acl_profile_exists)
   * [check_client_profile_exists](#solaceusers.check_client_profile_exists)
   * [create_user](#solaceusers.create_user)
   * [disable_user](#solaceusers.disable_user)
   * [get](#solaceusers.get)
   * [no_guarenteed_endpoint](#solaceusers.no_guarenteed_endpoint)
   * [no_shutdown_user](#solaceusers.no_shutdown_user)
   * [no_subscription_manager](#solaceusers.no_subscription_manager)
   * [register](#solaceusers.register)
   * [set_acl_profile](#solaceusers.set_acl_profile)
   * [set_client_profile](#solaceusers.set_client_profile)
   * [set_exists](#solaceusers.set_exists)
   * [set_password](#solaceusers.set_password)
* [SolaceVPN](#solacevpn)
   * [clear_radius](#solacevpn.clear_radius)
   * [create_vpn](#solacevpn.create_vpn)
   * [enable_vpn](#solacevpn.enable_vpn)
   * [get](#solacevpn.get)
   * [list_vpns](#solacevpn.list_vpns)
   * [register](#solacevpn.register)
   * [set_exists](#solacevpn.set_exists)
   * [set_internal_auth](#solacevpn.set_internal_auth)
   * [set_large_message_threshold](#solacevpn.set_large_message_threshold)
   * [set_logging_tag](#solacevpn.set_logging_tag)
   * [set_spool_size](#solacevpn.set_spool_size)
* [SolaceQueue](#solacequeue)
   * [consume](#solacequeue.consume)
   * [create_queue](#solacequeue.create_queue)
   * [enable](#solacequeue.enable)
   * [exclusive](#solacequeue.exclusive)
   * [get](#solacequeue.get)
   * [get_queue_config](#solacequeue.get_queue_config)
   * [max_bind_count](#solacequeue.max_bind_count)
   * [owner](#solacequeue.owner)
   * [register](#solacequeue.register)
   * [reject_on_discard](#solacequeue.reject_on_discard)
   * [retries](#solacequeue.retries)
   * [set_exists](#solacequeue.set_exists)
   * [shutdown_egress](#solacequeue.shutdown_egress)
   * [shutdown_ingress](#solacequeue.shutdown_ingress)
   * [spool_size](#solacequeue.spool_size)
* [NamingStandard](#namingstandard)
   * [register](#namingstandard.register)
   * [set_exists](#namingstandard.set_exists)
   * [solve](#namingstandard.solve)
* [ZoinksNamingStandard](#zoinksnamingstandard)
   * [register](#zoinksnamingstandard.register)
   * [set_exists](#zoinksnamingstandard.set_exists)
   * [solve](#zoinksnamingstandard.solve)
* [SolaceClientProfile](#solaceclientprofile)
   * [allow_bridging](#solaceclientprofile.allow_bridging)
   * [allow_consume](#solaceclientprofile.allow_consume)
   * [allow_endpoint_create](#solaceclientprofile.allow_endpoint_create)
   * [allow_send](#solaceclientprofile.allow_send)
   * [allow_transacted_sessions](#solaceclientprofile.allow_transacted_sessions)
   * [delete](#solaceclientprofile.delete)
   * [get](#solaceclientprofile.get)
   * [new_client_profile](#solaceclientprofile.new_client_profile)
   * [register](#solaceclientprofile.register)
   * [set_exists](#solaceclientprofile.set_exists)
   * [set_max_clients](#solaceclientprofile.set_max_clients)
* [Utilities](#utilities)
   * [get_user_queues](#utilities.get_user_queues)
   * [is_client_user_enabled](#utilities.is_client_user_enabled)
   * [is_client_user_inuse](#utilities.is_client_user_inuse)
   * [register](#utilities.register)
   * [set_exists](#utilities.set_exists)
* [InfluxDBClient](#influxdbclient)
   * [register](#influxdbclient.register)
   * [send](#influxdbclient.send)
   * [set_exists](#influxdbclient.set_exists)
* [CMDBClient](#cmdbclient)
   * [get_queues_of_vpn](#cmdbclient.get_queues_of_vpn)
   * [get_users_of_vpn](#cmdbclient.get_users_of_vpn)
   * [get_vpns_by_owner](#cmdbclient.get_vpns_by_owner)
   * [register](#cmdbclient.register)
   * [set_exists](#cmdbclient.set_exists)
* [YAMLClient](#yamlclient)
   * [get_queues_of_vpn](#yamlclient.get_queues_of_vpn)
   * [get_users_of_vpn](#yamlclient.get_users_of_vpn)
   * [get_vpns_by_owner](#yamlclient.get_vpns_by_owner)
   * [register](#yamlclient.register)
   * [set_exists](#yamlclient.set_exists)
* [XMLAPI](#xmlapi)
   * [_XMLAPI__get_et_root_object](#xmlapi._xmlapi__get_et_root_object)
   * [_XMLAPI__read_file](#xmlapi._xmlapi__read_file)
   * [_XMLAPI__restcall](#xmlapi._xmlapi__restcall)
   * [_XMLAPI__route_call](#xmlapi._xmlapi__route_call)
   * [configure](#xmlapi.configure)
   * [get_queues_of_vpn](#xmlapi.get_queues_of_vpn)
   * [get_users_of_vpn](#xmlapi.get_users_of_vpn)
   * [get_vpn](#xmlapi.get_vpn)
   * [get_vpns_by_owner](#xmlapi.get_vpns_by_owner)
   * [populateDeployData](#xmlapi.populatedeploydata)
   * [register](#xmlapi.register)
   * [set_exists](#xmlapi.set_exists)
* [SolaceXMLBuilder](#solacexmlbuilder)
* [Decorators](#decorators)
   * [MissingClientUser](#decorators.missingclientuser)
   * [MissingException](#decorators.missingexception)
   * [backup](#decorators.backup)
   * [before](#decorators.before)
   * [get_calling_module](#decorators.get_calling_module)
   * [only_if_exists](#decorators.only_if_exists)
   * [only_if_not_exists](#decorators.only_if_not_exists)
   * [only_on_shutdown](#decorators.only_on_shutdown)
   * [primary](#decorators.primary)
   * [wraps](#decorators.wraps)
* [Plugin](#plugin)
   * [register](#plugin.register)
   * [set_exists](#plugin.set_exists)
* [Naming](#naming)
   * [name](#naming.name)
* [SolaceCommandQueue](#solacecommandqueue)
   * [enqueue](#solacecommandqueue.enqueue)
   * [enqueueV2](#solacecommandqueue.enqueuev2)
* [SolaceProvision](#solaceprovision)

## SolaceACLProfile
 Plugin to manage AclProfiles

    :param api: The instance of SolaceAPI if not called from SolaceAPI.manage
    :param name: name of ACL
    :param vpn_name: name of the VPN to scope the ACL to
    :type api: SolaceAPI
    :type name: str
    :type vpn_name: str
    :rtype: SolaceACLProfile

Example:
```python
>>> import libsolace.settingsloader as settings
>>> from libsolace.SolaceAPI import SolaceAPI
>>> client = SolaceAPI("dev")
>>> client.manage("SolaceACLProfile", name="myprofile", vpn_name="testvpn").commands.commands
```
    

### SolaceACLProfile.allow_connect

 Allow Connect

    :param name:
    :param vpn_name:
    :return:

Example:
```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceACLProfile").allow_connect(name="myprofile", vpn_name="dev_testvpn")
>>> api.rpc(tuple_request)
```
        

### SolaceACLProfile.allow_publish

Allow publish

    :param name: name of the profile
    :param vpn_name: vpn name
    :return: tuple SEMP request and kwargs

Example:
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceACLProfile").allow_publish(name="myprofile", vpn_name="dev_testvpn"))
```
        

### SolaceACLProfile.allow_subscribe

 Allow subscribe

    :param name: name of the profile
    :param vpn_name: vpn name
    :return: tuple SEMP request and kwargs

Example:
```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceACLProfile").allow_subscribe(name="myprofile", vpn_name="dev_testvpn")
>>> api.rpc(tuple_request)
```
        

### SolaceACLProfile.new_acl

Create a new ACL

    :param name: name of the profile
    :param vpn_name: vpn name
    :return: tuple SEMP request and kwargs

Example:
```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceACLProfile").new_acl(name="myprofile", vpn_name="dev_testvpn")
>>> api.rpc(tuple_request)
```
        

### SolaceACLProfile.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### SolaceACLProfile.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

## SolaceUser
 Manage client-user within Solace 

### SolaceUser.check_acl_profile_exists
Document me!

### SolaceUser.check_client_profile_exists


        Checks if a client_profile exists on the appliance for linking.

        Example:
            >>> foo = SolaceUser(client_username="joe", environment="dev", client_profile="glassfish")
            >>> foo.check_client_profile_exists()
            >>> from libsolace.SolaceAPI import SolaceAPI
            >>> apic = SolaceAPI("dev")
            >>> foo = SolaceUser(api=apic)
            >>> foo.check_client_profile_exists(client_profile="glassfish")

        

### SolaceUser.create_user


        Create user XML / enqueue command on connection instance

        Example
        >>> connection = SolaceAPI("dev")
        >>> xml = connection.manage("SolaceUser").create_user(client_username="foo", vpn_name="bar")
        <rpc semp-version="soltr/6_0"><create><client-username><username>foo</username><vpn-name>bar</vpn-name>
        </client-username></create></rpc>

        

### SolaceUser.delete


        Delete user XML / enqueue command on connection instance

        Example
        >>> connection = SolaceAPI("dev")
        >>> connection.manage("SolaceUser").delete(client_username="foo", vpn_name="bar")
        <rpc semp-version="soltr/6_0"><create><client-username><username>foo</username><vpn-name>bar</vpn-name>
        </client-username></create></rpc>

        

### SolaceUser.get


        Get a username from solace, return a dict

        Example
        >>> connection = SolaceAPI("dev")
        >>> connection.manage("SolaceUser").get(client_username="dev_testvpn", vpn_name="dev_testvpn")
        {'reply': {'show': {'client-username': {'client-usernames': {'client-username': {'profile': 'glassfish',
        'acl-profile': 'dev_testvpn', 'max-endpoints': '16000', 'client-username': 'dev_testvpn', 'enabled': 'true',
        'message-vpn': 'dev_testvpn', 'password-configured': 'true', 'num-clients': '0', 'num-endpoints': '5',
        'subscription-manager': 'false', 'max-connections': '500', 'guaranteed-endpoint-permission-override': 'false'}}}
        }}}

        

### SolaceUser.no_guarenteed_endpoint
Document me!

### SolaceUser.no_shutdown
Document me!

### SolaceUser.no_subscription_manager
Document me!

### SolaceUser.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### SolaceUser.requirements


        Call the tests before create is attempted, checks for profiles in this case
        

### SolaceUser.set_acl_profile
Document me!

### SolaceUser.set_client_profile


        Set the ClientProfile

        Example
        >>> connection = SolaceAPI("dev")
        >>> xml = []
        >>> xml.append(connection.manage("SolaceUser").shutdown(client_username="foo", vpn_name="bar", shutdown_on_apply=True))
        >>> xml.append(connection.manage("SolaceUser").set_client_profile(client_username="foo", vpn_name="bar", client_profile="jboss"))
        >>> xml.append(connection.manage("SolaceUser").no_shutdown(client_username="foo", vpn_name="bar", shutdown_on_apply=True))
        >>> for x in xml:
        >>>     connection.rpc(str(x))
        

### SolaceUser.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

### SolaceUser.set_password
Document me!

### SolaceUser.shutdown


        Disable the user, this method would be called by anything decorated with @shutdown
        the kwarg shutdown_on_apply needs to be either True or 'u' or 'b' for this to take effect.

        Example
        >>> connection.manage("SolaceUser").shutdown(client_username="foo", vpn_name="bar", shutdown_on_apply=True)
        <rpc semp-version="soltr/6_0"><client-username><username>foo</username><vpn-name>bar</vpn-name><shutdown/>
        </client-username></rpc>
        

## SolaceUsers
 Manage dict of client-users within Solace 

### SolaceUsers._tests


        Call the tests before create is attempted, checks for profiles in this case
        

### SolaceUsers.check_acl_profile_exists
Document me!

### SolaceUsers.check_client_profile_exists


        Checks if a client_profile exists on the appliance for linking.

        Example:
            >>> foo = SolaceUser(username="joe", environment="dev", client_profile="glassfish")
            >>> foo.check_client_profile_exists()
            >>> from libsolace.SolaceAPI import SolaceAPI
            >>> apic = SolaceAPI("dev")
            >>> foo = SolaceUser(api=apic)
            >>> foo.check_client_profile_exists(client_profile="glassfish")

        

### SolaceUsers.create_user
Document me!

### SolaceUsers.disable_user


        Disable the user ( suspending pub/sub )

        

### SolaceUsers.get

 Get a username from solace, return a dict 

### SolaceUsers.no_guarenteed_endpoint
Document me!

### SolaceUsers.no_shutdown_user
Document me!

### SolaceUsers.no_subscription_manager
Document me!

### SolaceUsers.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### SolaceUsers.set_acl_profile
Document me!

### SolaceUsers.set_client_profile
Document me!

### SolaceUsers.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

### SolaceUsers.set_password
Document me!

## SolaceVPN
Manage a Solace VPN

If `vpn_name` is passed as a kwarg, this plugin enters provision/batch mode, if it is omitted, the plugin will go into
single query mode.

In provision/batch mode, this plugin generates all the neccesary SEMP requests to create a VPN. You also need to pass a
`owner_name` and a existing `acl_profile` name. If these are omitted, the vpn_name property is used.

In single query mode, this plugin creates single SEMP requests, you need only pass a SolaceAPI into `api`, or invoke
via SolaceAPI("dev").manage("SolaceVPN")

    :param api: The instance of SolaceAPI if not called from SolaceAPI.manage
    :param vpn_name: name of the VPN to scope the ACL to
    :type api: SolaceAPI
    :type vpn_name: str
    :rtype: SolaceVPN

Query/Single Mode Example Direct Access:

```python
>>> import libsolace.settingsloader as settings
>>> import libsolace
>>> from libsolace.SolaceAPI import SolaceAPI
>>> clazz = libsolace.plugin_registry("SolaceVPN", settings=settings)
>>> api = SolaceAPI("dev")
>>> solaceVpnPlugin = clazz(settings=settings, api=api)
>>> solaceVpnPlugin.get(vpn_name="default")
```

Provision/Batch Mode Example via SolaceAPI

```python
>>> api = SolaceAPI("dev")
>>> vpn = api.manage("SolaceVPN", vpn_name="my_vpn", owner_name="someuser", acl_profile="default", max_spool_usage=1024)
>>> for req in vpn.commands.commands:
>>>    api.rpc(str(req[0]), **req[1])
```

    

### SolaceVPN.clear_radius

Clears radius authentication mechanism

    :param vpn_name: The name of the VPN
    :type vpn_name: str
    :return: tuple SEMP request and kwargs

Example:

```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceVPN").clear_radius(vpn_name="my_vpn")
>>> api.rpc(tuple_request)
```

Example 2:

```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceVPN").clear_radius(vpn_name="my_vpn"))
```

        

### SolaceVPN.create_vpn

New VPN SEMP Request generator.

    :param vpn_name: The name of the VPN
    :type vpn_name: str
    :return: tuple SEMP request and kwargs

Example:

```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceVPN").create_vpn(vpn_name="my_vpn")
>>> api.rpc(tuple_request)
```

Example2:

```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceVPN").create_vpn(vpn_name="my_vpn"))
```
        

### SolaceVPN.enable_vpn

Enable a VPN

    :param vpn_name: The name of the VPN
    :type vpn_name: str
    :return: tuple SEMP request and kwargs

Example:

```python
>>> api = SolaceAPI("dev")
>>> request_tuple = api.manage("SolaceVPN").enable_vpn(vpn_name="my_vpn")
>>> api.rpc(request_tuple)
```

        

### SolaceVPN.get

Returns a VPN from the appliance immediately. This method calls the api instance so it MUST be referenced through the SolaceAPI instance, or passed a `api` kwarg.

    :param vpn_name: The name of the VPN
    :param detail: return details
    :type vpn_name: str
    :type detail: bool
    :return: dict

Example:

```python
>>> api = SolaceAPI("dev")
>>> dict_vpn = api.manage("SolaceVPN").get(vpn_name="my_vpn", detail=True)
```
        

### SolaceVPN.list_vpns

Returns a list of vpns

    :param vpn_name: the vpn_name search pattern to apply.
    :return:

Example:

```python
>>> api = SolaceAPI("dev")
>>> list_dict = api.manage("SolaceVPN").list_vpns(vpn_name="*")
```

        

### SolaceVPN.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### SolaceVPN.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

### SolaceVPN.set_internal_auth

Set authentication method to internal

    :param vpn_name: The name of the VPN
    :type vpn_name: str
    :return: tuple SEMP request and kwargs

Example:

```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceVPN").set_internal_auth(vpn_name="my_vpn")
>>> api.rpc(tuple_request)
```

        

### SolaceVPN.set_large_message_threshold

Sets the large message threshold

    :param vpn_name: The name of the VPN
    :param large_message_threshold: size in bytes
    :type vpn_name: str
    :type large_message_threshold: int
    :return: tuple SEMP request and kwargs

Example:

```python
>>> api = SolaceAPI("dev")
>>> request_tuple = api.manage("SolaceVPN").set_large_message_threshold(vpn_name="my_vpn", large_message_threshold=4096)
>>> api.rpc(request_tuple)
```

        

### SolaceVPN.set_logging_tag

Sets the VPN logging tag, default = vpn_name

    :param vpn_name: The name of the VPN
    :param tag: string to use in logging tag
    :type vpn_name: str
    :type tag: str
    :return: tuple SEMP request and kwargs

Example:

```python
>>> api = SolaceAPI("dev")
>>> request_tuple = api.manage("SolaceVPN").set_logging_tag(vpn_name="my_vpn", tag="my_vpn_string")
>>> api.rpc(request_tuple)
```
        

### SolaceVPN.set_spool_size

Set the maximun spool size for the VPN

    :param vpn_name: The name of the VPN
    :param max_spool_usage: size in mb
    :type vpn_name: str
    :type max_spool_usage: int
    :return: tuple SEMP request and kwargs

Example:

```python
>>> api = SolaceAPI("dev")
>>> request_tuple = api.manage("SolaceVPN").set_spool_size(vpn_name="my_vpn", max_spool_usage=4096)
>>> api.rpc(request_tuple)
```

        

## SolaceQueue
Manage a Solace Queue

This plugin creates / manages properties of queues. As with other plugins, passing in only the "api" or no kwargs returns the plugin in "query" mode.

    :param api: The instance of SolaceAPI if not called from SolaceAPI.manage
    :param queue_name: the queue name
    :param vpn_name: name of the VPN to scope the ACL to
    :param defaults: dictionary of queue properties, see `defaults` in SolaceQueue class
    :type api: SolaceAPI
    :type queue_name: str
    :type vpn_name: str
    :type defaults: dict
    :rtype SolaceQueue

Example:

```python
>>> api = SolaceAPI("dev")
>>> sq = api.manage("SolaceQueue")
>>> dict_queue = sq.get(vpn_name="dev_testvpn", queue_name="testqueue1")
>>> api.rpc(sq.max_bind_count(vpn_name="dev_testvpn", queue_name="testqueue1", max_bind_count=10))
```
    

### SolaceQueue.consume

Sets consume permission. add `consume` kwarg to allow non-owner users to consume.

    :param vpn_name: the name of the vpn
    :param queue_name: the queue name
    :param consume: set to "all" to allow ALL appliance client-users to "consume"
    :type vpn_name: str
    :type queue_name: str
    :type consume: str
    :return: tuple SEMP request and kwargs

Example:
```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceQueue").consume(queue_name="testqueue1",\
>>>     vpn_name="dev_testvpn", shutdown_on_apply=True, consume="all")
>>> api.rpc(tuple_request)
```
        

### SolaceQueue.create_queue

Create a queue / endpoint only if it doesnt exist.

    :param queue_name: the queue name
    :param vpn_name: the vpn name
    :type queue_name: str
    :type vpn_name: str
    :return: tuple SEMP request and kwargs

Example 1: Create Request, then Execute
```python
>>> api = SolaceAPI("dev")
>>> tuple_xml = api.manage("SolaceQueue").create_queue(vpn_name="dev_testvpn", queue_name="my_test_queue")
>>> api.rpc(tuple_xml)
```

Example 2: One Shot
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceQueue").create_queue(vpn_name="dev_testvpn", queue_name="my_test_queue2"))
```

        

### SolaceQueue.enable

Enable a the queue

    :param vpn_name: the name of the vpn
    :param queue_name: the queue name
    :type vpn_name: str
    :type queue_name: str
    :return: tuple SEMP request and kwargs

Example:
```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceQueue").enable(queue_name="testqueue1", vpn_name="dev_testvpn")
>>> api.rpc(tuple_request)
```
        

### SolaceQueue.exclusive

Set queue exclusivity

    :param vpn_name: the name of the vpn
    :param queue_name: the queue name
    :param exclusive: state
    :type vpn_name: str
    :type queue_name: str
    :type exclusive: bool
    :return: tuple SEMP request and kwargs

Example: Shutdown, Set Exclusive, Start
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceQueue").shutdown_ingress(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True))
>>> api.rpc(api.manage("SolaceQueue").exclusive(queue_name="testqueue1", vpn_name="dev_testvpn", exclusive=False, shutdown_on_apply=True))
>>> api.rpc(api.manage("SolaceQueue").enable(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True))
```
        

### SolaceQueue.get

Fetch a queue from the appliance

    :type queue_name: str
    :type vpn_name: str
    :param queue_name: Queue name filter
    :param vpn_name: name of the VPN to scope the ACL to
    :rtype list

Examples:

```python
>>> api = SolaceAPI("dev")
>>> list_queues = api.manage("SolaceQueue").get(queue_name='*', vpn_name='dev_testvpn')
```
        

### SolaceQueue.get_queue_config

 Returns a queue config for the queue and overrides where neccesary

        :param queue: single queue dictionary e.g.
            {
                "name": "foo",
                "env": [
                    "qa1": {
                        "queue_config": {
                            "retries": 0,
                            "exclusive": "false",
                            "queue_size": 1024,
                            "consume": "all",
                            "max_bind_count": 1000,
                            "owner": "dev_testuser"
                        }
                    }
                ]
            }

        

### SolaceQueue.max_bind_count

Limit the max bind count

    :param vpn_name: the name of the vpn
    :param queue_name: the queue name
    :param max_bind_count: max bind count
    :type vpn_name: str
    :type queue_name: str
    :type max_bind_count: int
    :return: tuple SEMP request and kwargs

Example:
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceQueue").max_bind_count(vpn_name="dev_testvpn", queue_name="testqueue1", max_bind_count=50))
```

        

### SolaceQueue.owner

 Set the owner

    :param vpn_name: the name of the vpn
    :param queue_name: the queue name
    :param owner: the owner client-username
    :type vpn_name: str
    :type queue_name: str
    :type owner: str
    :return: tuple SEMP request and kwargs

Example:
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceQueue").shutdown_ingress(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True))
>>> api.rpc(api.manage("SolaceQueue").shutdown_egress(queue_name="testqueue1", vpn_name="dev_testvpn", shutdown_on_apply=True))
>>> api.rpc(api.manage("SolaceQueue").owner(vpn_name="dev_testvpn", queue_name="testqueue1", owner_username="dev_testproductA"))
>>> api.rpc(api.manage("SolaceQueue").enable(queue_name="testqueue1", vpn_name="dev_testvpn"))
```
        

### SolaceQueue.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### SolaceQueue.reject_on_discard

 Reject to sender on discard

    :param vpn_name: the name of the vpn
    :param queue_name: the queue name
    :type vpn_name: str
    :type queue_name: str
    :return: tuple SEMP request and kwargs

Example:
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceQueue").reject_on_discard(vpn_name="dev_testvpn", queue_name="testqueue1"))
```
        

### SolaceQueue.retries

Delivery retries before failing the message

    :param vpn_name: the name of the vpn
    :param queue_name: the queue name
    :param retries: number of retries
    :type vpn_name: str
    :type queue_name: str
    :type retries: int
    :return: tuple SEMP request and kwargs

Example:
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceQueue").retries(vpn_name="dev_testvpn", queue_name="testqueue1", retries=5))
```
        

### SolaceQueue.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

### SolaceQueue.shutdown_egress

Shutdown egress for a queue

    :param shutdown_on_apply: is shutdown permitted boolean or char
    :param vpn_name: name of the vpn
    :param queue_name: name of the queue
    :type shutdown_on_apply: char or bool
    :type queue_name: str
    :type vpn_name: str
    :return: tuple SEMP request and kwargs

Example 1: One Shot
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceQueue").shutdown_egress(shutdown_on_apply=True, vpn_name="dev_testvpn", queue_name="testqueue1"))
```

Example 2: Create Request, then Execute
```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceQueue").shutdown_egress(shutdown_on_apply=True, vpn_name="dev_testvpn", queue_name="testqueue1")
>>> api.rpc(tuple_request)
```
        

### SolaceQueue.shutdown_ingress

Shutdown the ingress of a queue

    :param shutdown_on_apply: is shutdown permitted boolean or char
    :param vpn_name: name of the vpn
    :param queue_name: name of the queue
    :type shutdown_on_apply: char or bool
    :type queue_name: str
    :type vpn_name: str
    :return: tuple SEMP request and kwargs

Example 1: Instant Execution:
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceQueue").shutdown_ingress(shutdown_on_apply=True, vpn_name="dev_testvpn", queue_name="testqueue1"))
```

Example 2: Create Request, then Execute
```python
>>> api = SolaceAPI("dev")
>>> tuple_request = api.manage("SolaceQueue").shutdown_ingress(shutdown_on_apply=True, vpn_name="dev_testvpn", queue_name="testqueue1")
>>> api.rpc(tuple_request)
```
        

### SolaceQueue.spool_size

Set the spool size

    :param vpn_name: the name of the vpn
    :param queue_name: the queue name
    :param queue_size: size of the spool in mb
    :type vpn_name: str
    :type queue_name: str
    :type queue_size: int
    :return: tuple SEMP request and kwargs

Example
```python
>>> api = SolaceAPI("dev")
>>> api.rpc(api.manage("SolaceQueue").spool_size(vpn_name="dev_testvpn", queue_name="testqueue1", queue_size=64))
```
        

## NamingStandard
None

### NamingStandard.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### NamingStandard.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

### NamingStandard.solve


        Given two args, "name" and "prefix", this plugin returns "prefix_name"

        :type args: list[str]
        :rtype: str

        

## ZoinksNamingStandard
None

### ZoinksNamingStandard.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### ZoinksNamingStandard.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

### ZoinksNamingStandard.solve
Document me!

## SolaceClientProfile
Create / Manage client profiles

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

    

### SolaceClientProfile.allow_bridging

Allow bridging

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
        

### SolaceClientProfile.allow_consume

Allow consume permission

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
        

### SolaceClientProfile.allow_endpoint_create

Allow endpoint creation permission

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
        

### SolaceClientProfile.allow_send

Allow send permission

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
        

### SolaceClientProfile.allow_transacted_sessions

Allow transaction sessions permission

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
        

### SolaceClientProfile.delete

Delete a client profile

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
        

### SolaceClientProfile.get

Returns a ClientProfile immediately

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
        

### SolaceClientProfile.new_client_profile

Create a new client profile

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
        

### SolaceClientProfile.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### SolaceClientProfile.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

### SolaceClientProfile.set_max_clients

Set max clients for profile

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
        

## Utilities
None

### Utilities.get_user_queues


        Get all queues and return filtered list of only queues who's owner matches the username

        Example:
            >>> connection = SolaceAPI("dev")
            >>> results = get_plugin("Utilities", connection).get_user_queues("dev_testproductA", "dev_testvpn")
            [u'testqueue1']

        :param username: username to filter on
        :param vpn_name: vpn to filter on
        :return:
        

### Utilities.is_client_user_enabled


        Returns boolean if client username has client connections
        

### Utilities.is_client_user_inuse


        Returns boolean if client username has client connections
        

### Utilities.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### Utilities.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

## InfluxDBClient


    import libsolace.settingsloader as settings
    import libsolace
    metrics_class = libsolace.plugin_registry('InfluxDBClient', settings=settings)
    metrics = metrics_class(settings=settings)

    

### InfluxDBClient.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### InfluxDBClient.send


        import libsolace.settingsloader as settings
        import libsolace
        metrics_class = libsolace.plugin_registry('InfluxDBClient', settings=settings)
        metrics = metrics_class(settings=settings)

        metrics.send('http-metrics', {"key": 10, "key2": 12}, environment='prod', host='foo')
        metrics.send("test", {"key": 2}, host="test")

        :param data: a json object of keys and values. will be flattened!
        :param measurement:
        

### InfluxDBClient.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

## CMDBClient
None

### CMDBClient.get_queues_of_vpn


        As with VPN, all configs should be finalized before returned.
        

### CMDBClient.get_users_of_vpn


        Just return a list of users for a VPN
        

### CMDBClient.get_vpns_by_owner


        return a LIST of vpns groups by some "owner", each VPN contains final config,
        so all environment overrides and that should be taken care of here!
        :param environment: the name of the environment
        

### CMDBClient.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### CMDBClient.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

## YAMLClient
None

### YAMLClient.get_queues_of_vpn


        As with VPN, all configs should be finalized before returned.
        

### YAMLClient.get_users_of_vpn


        Just return a list of users for a VPN
        

### YAMLClient.get_vpns_by_owner


        return a LIST of vpns groups by some "owner", each VPN contains final config,
        so all environment overrides and that should be taken care of here!
        :param environment: the name of the environment
        

### YAMLClient.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### YAMLClient.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

## XMLAPI
 LEGACY XML API handles reading the XML configuiration from URL or FILE.

        cmdbapi = libsolace.plugin_registry(settings.SOLACE_CMDB_PLUGIN)
        cmdbapi.configure(settings=settings)
        vpns = cmdbapi.get_vpns_by_owner(options.product, environment=options.env)
        users = cmdbapi.get_users_of_vpn(vpn['name'], environment=options.env)
        queues = cmdbapi.get_queues_of_vpn(vpn['name'], environment=options.env)

    

### XMLAPI._XMLAPI__get_et_root_object


        Returns elementtree root object representation of index.xml

        :return: Element object
        :rtype: xml.etree.ElementTree.Element
        

### XMLAPI._XMLAPI__read_file

 returns the file data from self.xml_file_data

        :param kwargs:
        :return: file contents
        :rtype: str
        

### XMLAPI._XMLAPI__restcall

 Uses urllib to read a data from a webservice, if self.xml_file_data = None, else returns the local file contents

        :type url: str
        :param url: url to call
        :param kwargs:
        :return: response data
        :rtype: str
        

### XMLAPI._XMLAPI__route_call

 Determines if the call should be routed via urllib or read from local file.

        :param url: url to call
        :param kwargs:
        :return: response from correct interface
        

### XMLAPI.configure
Document me!

### XMLAPI.get_queues_of_vpn
Document me!

### XMLAPI.get_users_of_vpn

 Returns all products users who use a specifig messaging VPN

        :type vpn: str
        :param vpn: name of vpn to search for users of

        

### XMLAPI.get_vpn

 Return a VPN by name

        :return: a solace vpn
        

### XMLAPI.get_vpns_by_owner


        Return a VPN by owner

        :type owner: str

        :return list of vpns
        :rtype libsolace.gfmisc.DataNode

        

### XMLAPI.populateDeployData

 Returns the entire deployment data ( entire xml ) as a python dict style object
        :return: all deployment data in a single dictionary object
        

### XMLAPI.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### XMLAPI.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

## SolaceXMLBuilder
Builds Solace's SEMP XML Configuration Commands

Any dot-name-space calling of a instance of SolaceXMLBuilder will create
nested dictionary named the same. These are converted to XML when the instance
is represented serialized or represented as a string.

```python
>>> a=SolaceXMLBuilder(version="soltr/6_2")
>>> a.foo.bar.baz=2
>>> str(a)
'<rpc semp-version="soltr/6_2">
<foo><bar><baz>2</baz></bar></foo></rpc>'
```
    

## Decorators

Some decorators which are used within the Plugins in order to control / limit execution.


### Decorators.backup

 Sets the backupOnly kwarg before calling the method. Use this to force a method onto a specific router.
Note, this does NOT unset primaryOnly kwarg, so you can actualy double target.

    :return: method
    

### Decorators.before

Call a named method before the decorated method. This is typically used to tell a object to shutdown so some
modification can be made.

    :param method_name: name of the method to call on object
    :return: method

Example:
```python
>>> def shutdown(self, **kwargs):
>>>    # shutdown some object
>>> @before("shutdown")
>>> def delete(self, **kwargs):
>>>    # delete object since its shutdown
```
    

### Decorators.only_if_exists

 Return method only if item exists.

    :param entity: the "getter" to call
    :param data_path: a dot name spaced string which will be used to decend into the response document to verify exist
    :param primaryOnly: run the "getter" only against primary
    :param backupOnly: run the "getter" only against backup
    :return: method

If object exists bit set, return the method
If object exists bit not set, query the object, return the method if succes
If object does not exist, dont return the method.

For Example see only_if_not_exists

    

### Decorators.only_if_not_exists

Return method if the item does NOT exist in the Solace appliance, setting the kwarg for which appliance needs
the method run.

    :param entity: the "getter" to call
    :param data_path: a dot name spaced string which will be used to descend into the response document to verify exist
    :param primaryOnly: run the "getter" only against primary
    :param backupOnly: run the "getter" only against backup
    :return: method

if the object's exists caching bit is False, return the method
If the object does not exist, return the method and set the exists bit to False
If the object exists in the appliance, set the exists bit to True

Example
```python
>>> @only_if_not_exists('get', 'rpc-reply.rpc.show.client-username.client-usernames.client-username')
>>> def create_user(**kwargs):
>>>    return True
>>> create_user()
```
    

### Decorators.only_on_shutdown

Only calls the method if the shutdown byte permits it. The entity is one of `queue` or `user` and both have
differnent trigger scenarios and commons ones too..

    :param entity: (str) "queue" or "user"
    :return: method

#### User:
If shutdown is True | b | u for a "user" entity, then allow the method to run.

#### Queue:
If shutdown is True | b | q for a "queue" entity, then allow the method to run.

methods decorated with this can optionally be decorated with the @shutdown decorator if you are needing to
shutdown the object at the same time. If the object is not shutdown, the appliance will throw a error.

Example:

```python
>>> @only_on_shutdown('user')
>>> def delete_user(**kwargs):
>>>    return True
>>> delete_user(shutdown_on_apply='u')
True
>>> delete_user(shutdown_on_apply='q')
None
```

    

### Decorators.primary

 Sets the primaryOnly kwarg before calling the method. Use this to force a method onto a specific router.
Note, this does NOT unset backupOnly kwarg, so you can actualy double target.

    :return: method
    

## Plugin
This is the plugin core object where all pluggables should extend from and register too.

Example:
```python
>>> import pprint
>>> import libsolace
>>> from libsolace.plugin import Plugin
>>> libsolace.plugin_registry = Plugin()
>>> @libsolace.plugin_registry.register
>>> class Bar(Plugin):
>>>     # must have a name for the plugin, helps calling it by name later.
>>>     plugin_name = "BarPlugin"
>>>     # Instance methods work!
>>>     def hello(self, name):
>>>         print("Hello %s from %s" % (name, self))
>>>     # Static methods work too!
>>>     @staticmethod
>>>     def gbye():
>>>         print("Cheers!")
>>> libsolace.plugin_registry('BarPlugin').hello("dude")
>>> libsolace.plugin_registry('BarPlugin').gbye()
>>> pprint.pprint(dir(libsolace.plugin_registry('BarPlugin')))
```

    

### Plugin.register

Registers a object with the plugin registry

    :param object_class: object to register, should be a class
    :return:
        

### Plugin.set_exists

set_exists is used to cut down on SEMP queries to validate existence of items. For example, if you create a
new VPN in Batch mode, After the "create-vpn" XML is generated, set_exists is set to True so subsequent provision
requests decorated with the `only_if_exists` decorator need to be have this set in order to fire.

    :param state: exists or not boolean
    :type state: bool
    :return:
        

## Naming
This method is responsible for handing off Naming work to the configured naming standard. The Plugin for the standard
is specified in the NAMEHOOK property of the libsolace.yaml file.

example while ZoinksNamingStandard set as NAMEHOOK in libsolace.yaml:
```python
>>> from libsolace.plugins.NamingStandard import name
>>> name("%s_something", "dev")
'dev_something'
```

example while DefaultNaming set as NAMEHOOK
```python
>>> name("something", "dev")
'dev_something'
```



### Naming.name


    Passes off work to the plugin as specified by NAMEHOOK in libsolace.yaml. The plugin MUST have a solve() method
    which accepts args and kwargs. see NamingStandard.py and ZoinksNamingStandard.py

    :rtype: str
    

## SolaceCommandQueue
 Solace Command Queue Class

A simple queue which validates SEMP XML against correct version of xsd,
and then puts returns the commands list object.

    

### SolaceCommandQueue.enqueue

 Validate and append a command onto the command list.

    :type command: SolaceXMLBuilder
    :param command: SEMP command to validate
    :return: None
        

### SolaceCommandQueue.enqueueV2

 Validate and append a command onto the command list.

    :type command: SolaceXMLBuilder
    :type kwargs: kwargs
    :param command: SEMP command to validate
    :param kwargs: primaryOnly = True, backupOnly = True
    :return: None
        

## SolaceProvision
 Provision the CLIENT_PROFILE, VPN, ACL_PROFILE, QUEUES and USERS

    :type vpn_dict: dictionary
        eg: {'owner': u'SolaceTest', 'spool_size': u'4096', 'password': u'd0nt_u5se_thIs', 'name': u'dev_testvpn'}
    :type queue_dict: list
        eg: [
              {"exclusive": u"true", "type": "", "name": u"testqueue1", "queue_size": u"4096"},
              {"exclusive": u"false", "type": "", "name": u"testqueue2", "queue_size": u"4096"}
            ]
    :type environment: str
    :type client_profile: str
    :type users: list
    :type testmode: bool
    :type create_queues: bool
    :type shutdown_on_apply: bool

    :param vpn_dict: vpn dictionary
    :param queue_dict: queue dictionary list
    :param environment: name of environment
    :param client_profile: name of client_profile, default='glassfish'
    :param users: list of user dictionaries to provision
        eg: [{'username': u'dev_marcom3', 'password': u'dev_marcompass'}]
    :param testmode: only test, dont apply changes
    :param create_queues: disable queue creation, default = True
    :param shutdown_on_apply: force shutdown Queue and User for config change, default = False

    
