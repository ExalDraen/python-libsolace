#!/usr/bin/env python
import sys
import os
import logging
logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

import libsolace
from libsolace import solace
from libsolace.sitexml import XMLAPI
from libsolace.solacehelper import SolaceProvisionVPN, SolaceNodeFromJson

try:
    import simplejson as json
except:
    import json



vpn_json = '''
{
   "name":"%s_testvpn",
   "vpn_config":{
      "spool_size":"4096"
   },
   "queue":[
      {
         "env":[
            {
               "name":"pt1",
               "queue_config":{
                  "exclusive":"true",
                  "queue_size":"4096"
               }
            },
            {
               "name":"prod",
               "queue_config":{
                  "exclusive":"true",
                  "queue_size":"4096"
               }
            }
         ],
         "name":"testqueue1",
         "queue_config":{
            "exclusive":"true",
            "queue_size":"1024"
         }
      },
      {
         "env":[
            {
               "name":"pt1",
               "queue_config":{
                  "exclusive":"false",
                  "queue_size":"4096"
               }
            },
            {
               "name":"prod",
               "queue_config":{
                  "exclusive":"false",
                  "queue_size":"4096"
               }
            }
         ],
         "name":"testqueue2",
         "queue_config":{
            "exclusive":"false",
            "queue_size":"1024"
         }
      }
   ],
   "env":[
      {
         "name":"dev",
         "vpn_config":{
            "spool_size":"1024"
         }
      },
      {
         "name":"pt1",
         "vpn_config":{
            "spool_size":"16384"
         }
      },
      {
         "name":"prod",
         "vpn_config":{
            "spool_size":"16384"
         }
      }
   ],
   "owner":"SolaceTest",
   "password":"d0nt_u5se_thIs"
}
'''

users_json = None

logging.info(vpn_json)

foo = SolaceNodeFromJson(vpn_json)

logging.info(foo.__dict__)

# connect to the dev appliance cluster
result = SolaceProvisionVPN(
    vpn_datanode=SolaceNodeFromJson(vpn_json),
    environment='dev',
    client_profile="glassfish",
    users=users_json,
    testmode=False,
    shutdown_on_apply=False
)
