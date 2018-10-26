# libSolace
<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [libSolace](#libsolace)
    - [Overview](#overview)
    - [Installation](#installation)
    - [API Docs](#api-docs)
        - [XML Generator](#xml-generator)
        - [CMDB Configuration data and Naming Patterns](#cmdb-configuration-data-and-naming-patterns)
        - [Limitations](#limitations)
- [Provisioning](#provisioning)
    - [Configuration](#configuration)
- [Plugins](#plugins)
- [bin](#bin)
- [Classes](#classes)
- [Site Management / Provisioning](#site-management--provisioning)
    - [-](#-)
    - [Integration with a Custom CMDB](#integration-with-a-custom-cmdb)
    - [Running the provision tasks](#running-the-provision-tasks)
- [Testing](#testing)
    - [Single Plugin](#single-plugin)
    - [Single Test](#single-test)
    - [All with Coverage](#all-with-coverage)
- [Docs](#docs)
    - [Doctests](#doctests)
    - [Html](#html)

<!-- markdown-toc end -->

## Overview

This is a set of python helpers for managing and provisioning [Solace](https://solace.com/) Messaging Appliances and the VMR. The design is to be flexible
and aimed at managing multiple clusters in multiple environments.

## Installation

1. Install the libraries required for `lxml` and `pyyaml`
1. Install using `pip`:
   ```sh
   pip install libsolace
   ```

## API Docs

[API Docs](https://unixunion.github.io)


### XML Generator

The core of this provisioning system is the SolaceXMLBuilder class which can generate XML through recursive instantiation of a dictionary like object. Example:

```python
    >>> document = SolaceXMLBuilder(version="soltr/6_2")
    >>> document.create.client_username.username = "myUserName"
    >>> document.create.client_username.vpn_name = "dev_MyVPN"
    >>> str(document)
    '<rpc semp-version="soltr/6_2"><create><client-username><username>myUserName</username><vpn-name>dev_MyVPN</vpn-name></client-username></create></rpc>'
```


Plugins create SEMP request objects, which then need to be sent via SolaceAPI.rpc to the appliances.
Plugins are written to create single or batches of SEMP commands and return them once the XML is validated against the XSD.

```python
    >>> from libsolace.SolaceAPI import SolaceAPI
    >>> connection = SolaceAPI("dev")
    >>> # VMR: connection = SolaceAPI("dev", detect_status=False, version="soltr/7_1_1")
    >>> # create the command for creating a new user via the "SolaceUser" plugin
    >>> plugin_request = connection.manage("SolaceUser").create_user(client_username="foo", vpn_name="bar")
    >>> plugin_request.xml
    '<rpc semp-version="soltr/7_1_1"><create><client-username><username>foo</username><vpn-name>bar</vpn-name></client-username></create></rpc>'
    >>> plugin_request.kwargs
    {'vpn_name': 'bar', 'primaryOnly': True, 'backupOnly': True, 'client_username': 'foo'}
```

The SolaceXMLBuilder is typically used through the SolaceAPI, which will take care to detect the appliance OS version for you. e.g.

```python
    >>> from libsolace.SolaceAPI import SolaceAPI
    >>> conn = SolaceAPI("dev")
    >>> conn.manage("SolaceUser").get(client_username="dev_testvpn", vpn_name="dev_testvpn")
    [{'HOST': 'http://solace1/SEMP', u'rpc-reply': {u'rpc': {u'show': {u'client-username': {u'client-usernames': {u'num-total-client-usernames': u'763', u'max-num-total-client-usernames': u'9002', u'num-dynamic-client-usernames': u'0', u'num-configured-client-usernames': u'763', u'client-username': {u'profile': u'glassfish', u'dynamically-configured': u'false', u'acl-profile': u'dev_testvpn', u'max-endpoints': u'16000', u'client-username': u'dev_testvpn', u'max-connections-service-smf': u'9000', u'enabled': u'true', u'message-vpn': u'dev_testvpn', u'password-configured': u'true', u'num-clients': u'0', u'max-connections-service-web': u'9000', u'num-endpoints': u'3', u'subscription-manager': u'false', u'authorization-group': None, u'max-connections': u'500', u'num-clients-service-web': u'0', u'guaranteed-endpoint-permission-override': u'false', u'num-clients-service-smf': u'0'}}}}}, u'execute-result': {u'@code': u'ok'}, u'@semp-version': u'soltr/7_1_1'}}, {'HOST': 'http://solace2/SEMP', u'rpc-reply': {u'rpc': {u'show': {u'client-username': {u'client-usernames': {u'num-total-client-usernames': u'755', u'max-num-total-client-usernames': u'9002', u'num-dynamic-client-usernames': u'0', u'num-configured-client-usernames': u'755', u'client-username': {u'profile': u'glassfish', u'dynamically-configured': u'false', u'acl-profile': u'dev_testvpn', u'max-endpoints': u'16000', u'client-username': u'dev_testvpn', u'max-connections-service-smf': u'9000', u'enabled': u'true', u'message-vpn': u'dev_testvpn', u'password-configured': u'true', u'num-clients': u'0', u'max-connections-service-web': u'9000', u'num-endpoints': u'4', u'subscription-manager': u'false', u'authorization-group': None, u'max-connections': u'500', u'num-clients-service-web': u'0', u'guaranteed-endpoint-permission-override': u'false', u'num-clients-service-smf': u'0'}}}}}, u'execute-result': {u'@code': u'ok'}, u'@semp-version': u'soltr/7_1_1'}}]
```

The VMR requires initialization with the following:

```python
    >>> from libsolace.SolaceAPI import SolaceAPI
    >>> conn = SolaceAPI("dev", detect_status=False, version="soltr/7_1_1)
    >>> conn.manage("SolaceUser").get(client_username="dev_testvpn", vpn_name="dev_testvpn")
    [{'HOST': 'http://solace3:8080/SEMP', u'rpc-reply': {u'rpc': {u'show': {u'client-username': {u'client-usernames': {u'num-total-client-usernames': u'10', u'max-num-total-client-usernames': u'1002', u'num-dynamic-client-usernames': u'0', u'num-configured-client-usernames': u'10'}}}}, u'execute-result': {u'@code': u'ok'}, u'@semp-version': u'soltr/7_1_1'}}, None]
```


### CMDB Configuration data and Naming Patterns

In my use case, each Solace Cluster could potentially host multiple 'environments', therefore ALL objects are created with
a environment specific name to allow multi-homing.

e.g.:

    * dev_MyVPN
    * qa1_productA
    * dev_productA

This means that any cluster can host any number of environments combined without conflicting resources. The CMDBClient
contract states it must resolve the final item name by substituting the environment name into the string.

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

# Provisioning

libsolace can provision Solace appliances from YAML files, or whichever CMDB you use if you implement a client for that.

The script ./bin/solace-provision.py is the entrypoint for provisioniong tasks.

Examples
```shell
# single VMR "au_dev3"
./bin/solace-provision.py -e au_dev3 --no-detect-status -p MySolaceEcosystem --soltr_version="soltr/7_1_1"
# 2 appliance cluster "dev"
./bin/solace-provision.py -e dev -p MySolaceEcosystem

```

## Configuration

libsolace requires a `libsolace.yaml` file in order to know what environments exist and what appliances are part of those
environments. A single appliance can be part of multiple environments.

The `libsolace.yaml` file is searched for in:

* os.environ['LIBSOLACE_CONFIG']
* 'libsolace.yaml'
* '/etc/libsolace/libsolace.yaml'
* '/opt/libsolace/libsolace.yaml'

The configuration loader is also responsible for loading all plugins as specified in the PLUGINS key.

See <a href="libsolace.yaml.template">libsolace.yaml.template</a> for more info.



# Plugins

libsolace is pluggable, and you can register your own classes to customize the appliance management. You need to implement your own CMDBClient which should integrate with whatever configuration system you desire to populate solace.

* See <a href="libsolace/plugins/CMDBClient.py">CMDBClient</a>
* See <a href="libsolace/plugins/">All Plugins</a>
* See <a href="libsolace/items/">Item Plugins</a>

# bin

See the <a href="bin/">bin</a> for examples of various activities.

# Classes

run `make html` to generate all sphinx docs.
make doctest -d to test docstrings

# Site Management / Provisioning

You can manage a simple set of configuration items in multiple datacenters or environments utilizing the `solace-provision.py` bin,
which can provision entire VPN's, Queues, Profiles and Users.

```bash
 ./bin/solace-provision.py -e dev --no-detect-status -p MySolaceEcosystem --soltr_version="soltr/7_1_1"
```

### YAMLClient

The YAML Client is the simplest way to spec out a environment. It is enabled by adding 'libsolace.plugins.YAMLClient' to
the PLUGINS list in libsolace.yaml, and settings 'SOLACE_CMDB_PLUGIN: YAMLClient'

```yaml

---
VPNS:
  MySolaceEcosystem:
    -
      vpn_config:
        spool_size: 1024
      password: d0nt_u5e_th1s
      id: au_testvpn
      name: au_testvpn
    -
      vpn_config:
        spool_size: 1024
      password: d0nt_u5e_th1s
      id: au_testvpn2
      name: au_testvpn2

QUEUES:
  au_testvpn:
    -
      name: testqueue1
      queue_config:
        exclusive: "true"
        queue_size: 4096
        retries: 0
        max_bind_count: 1000
        owner: au_testproductA
        consume: all

USERS:
  au_testvpn:
    -
      username: au_testproductA
      password: somepassword

  au_testvpn2:
    -
      username: au_testproductA
      password: somepassword
```


### Integration with a Custom CMDB

You should implement your own integration with whatever CMDB you use. See CMDBClient plugin *class* and associated
libpipeline.yaml properties for plugin structure and how to configure libsolace to use it.

Any CMDB implementation must implement the methods as defined in the CMDBClient.py example.


## Running the provision tasks
see ./bin/solace-provision.py --help

# Testing

Define a "dev" environment in the config as in libsolace-tests.yaml. You can then run tests as follows:

## Single Plugin
nosetests -d tests.unittests.test_solace_user:TestSolaceUser  --logging-level=INFO --nologcapture -v

## Single Test
nosetests -d tests.unittests.test_solace_user:TestSolaceUser.test_create_user  --logging-level=INFO --nologcapture -v

## All with Coverage
LIBSOLACE_CONFIG=libsolace-tests.yaml nosetests --with-coverage --cover-package=libsolace

# Docs

## Doctests
make doctest

## Html
make html
