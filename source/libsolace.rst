libsolace package
=================

Main Package
-----------

.. automodule:: libsolace
    :members:
    :undoc-members:
    :show-inheritance:

Installing
-----------

You need libyaml-devel or equivilant for your OS.

For debian means install:

    - libxslt1-dev
    - libxml2-dev
    - python-dev

and then run:

.. code-block:: none

    python setup.py install


.. _quickstart:

Provisioning Quickstart
-----------

libsolace can be used as is for some basic provisioning which should be enough to get you started. In the main directory
`python-libsolace`, create the following two YAML files.

`libsolace.yaml`

.. code-block:: none

    ---
    # the url you might want to serve the site config from if not using local files
    CMDB_URL: "http://someurl/site.xml"
    CMDB_FILE: "provision-example.yaml"
    CMDB_USER: ""
    CMDB_PASS: ""


    # the readonly user to use for test mode
    READ_ONLY_USER: readonly
    READ_ONLY_PASS: readonly


    # the naming standard to use, default is <env>_<name> if CMDB Client supports it.
    NAMEHOOK: ZoinksNamingStandard


    # list of all plugins to load
    PLUGINS:
      - libsolace.items.SolaceACLProfile
      - libsolace.items.SolaceUser
      - libsolace.items.SolaceUsers
      - libsolace.items.SolaceVPN
      - libsolace.items.SolaceQueue
      - libsolace.plugins.NamingStandard
      - libsolace.plugins.ZoinksNamingStandard
      - libsolace.items.SolaceClientProfile
      - libsolace.plugins.Utilities
      - libsolace.plugins.InfluxDBClient
      - libsolace.plugins.YAMLClient


    # the plugin name as registered in the registry we want to use for solace config
    SOLACE_CMDB_PLUGIN: YAMLClient


    # The plugin to use for Solace Queue management
    SOLACE_QUEUE_PLUGIN: SolaceQueue
    SOLACE_USER_PLUGIN: SolaceUser


    # mapping of environment to solace appliances
    SOLACE_CONF:
      dev:
       MGMT:
          - http://appliance.fqdn:8080/SEMP
       PASS: admin
       USER: admin


provision-example.yaml

.. code-block:: none

    VPNS:
      SolaceTest:
        -
          vpn_config:
            spool_size: 1024
          password: d0nt_u5e_th1s
          id: au_testvpn
          name: au_testvpn
        -
          owner: SolaceTest
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


And then finally run wither of the following depending on if you have a cluster or standalone appliance.


Single appliance:
.. code-block:: none

    ./bin/solace-provision.py -e dev --no-detect-status -p SolaceTest --soltr_version="soltr/7_1_1"

Cluster
.. code-block:: none

    ./bin/solace-provision.py -e dev -p SolaceTest


Subpackages
-----------

.. toctree::
    :maxdepth: 3

    libsolace.data
    libsolace.items
    libsolace.plugins

Submodules
----------

.. toctree::

   libsolace.Decorators
   libsolace.Exceptions
   libsolace.Kwargs
   libsolace.Naming
   libsolace.SolaceAPI
   libsolace.SolaceCommandQueue
   libsolace.SolaceNode
   libsolace.SolaceProvision
   libsolace.SolaceReply
   libsolace.SolaceXMLBuilder
   libsolace.plugin
   libsolace.settingsloader
   libsolace.util
   libsolace.xml2dict

