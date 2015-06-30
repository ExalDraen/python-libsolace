#!/usr/bin/env python
from libsolace import solace
from libsolace.solacehelper import SolaceXMLBuilder
import libsolace.settingsloader as settings
import pprint
import copy

pp = pprint.PrettyPrinter(indent=2)
settings.debugmode=False
# Create a list to stack commands onto
commands = []

'''
This example does a few simple tasks

1. Create VPN
2. Sets the SPOOL size of the VPN
3. Creates a new acl-profile for ENV_VPN
4. Assign rights for acl-profiles
5. Create a new user using acl-profile
6. Assign Rights to user
7. Create queues

'''

environment = 'dev'			# Which environment to create VPN in
vpnname = 'my_%s_vpn' % environment 			# VPN Name with environment reflected in it
shortname = 'my_%s_vpn' % environment 				# Shortname used by VPN for logging and so forth
usernames = [shortname] 									# The username(s) to create for this VPN
password = 'password' 										# Password to set all users to
client_profile = 'default'									# Client profile to use ( must exist )
queuespoolsize = '1024'										# Max per-queue spool size
spool_size = '5000' 										# Spool size in MB of the spool
large_message_threshold = '4096' 							# triggeres warning events if size is exceeded
maxbindcount = '10'											# queue max bind count

queues = [
        {"name": "AdminEvents"},
        {"name": "Events"},
        {"name": "MessagingEvents"}
]

# Create a client to the PT1 unit ( Update to connect to both devices and create VPN, SPOOL, USERS, ACL, CLIENT PROFILE )
solace = solace.SolaceAPI(environment)

# Create domain-event VPN, this can fail if VPN exists, but thats ok.
cmd = SolaceXMLBuilder('VPN Create new VPN %s' % vpnname)
cmd.create.message_vpn.vpn_name=vpnname
solace.rpc(str(cmd))

# Switch Radius Domain to nothing
cmd = SolaceXMLBuilder("VPN %s Clearing Radius" % vpnname)
cmd.message_vpn.vpn_name = vpnname
cmd.message_vpn.authentication.user_class.client
cmd.message_vpn.authentication.user_class.radius_domain.radius_domain
solace.rpc(str(cmd))

# Switch to Internal Auth
cmd = SolaceXMLBuilder("VPN %s Enable Internal Auth" % vpnname)
cmd.message_vpn.vpn_name = vpnname
cmd.message_vpn.authentication.user_class.client
cmd.message_vpn.authentication.user_class.auth_type.internal
solace.rpc(str(cmd))

# Set the Spool Size
cmd = SolaceXMLBuilder("VPN %s Set spool size to %s" % (vpnname, spool_size))
cmd.message_spool.vpn_name = vpnname
cmd.message_spool.max_spool_usage.size = spool_size
solace.rpc(str(cmd))

# Large Message Threshold
cmd = SolaceXMLBuilder("VPN %s Settings large message threshold event to %s" % (vpnname, large_message_threshold))
cmd.message_vpn.vpn_name = vpnname
cmd.message_vpn.event.large_message_threshold.size = large_message_threshold
solace.rpc(str(cmd))

# Logging Tag for this VPN
cmd = SolaceXMLBuilder("VPN %s Setting logging tag to %s" % (vpnname, shortname))
cmd.message_vpn.vpn_name = vpnname
cmd.message_vpn.event.log_tag.tag_string = shortname
solace.rpc(str(cmd))

# Enable the VPN
cmd = SolaceXMLBuilder("VPN %s Enabling the vpn" % vpnname)
cmd.message_vpn.vpn_name = vpnname
cmd.message_vpn.no.shutdown
solace.rpc(str(cmd))

# ACLS / Users
cmd = SolaceXMLBuilder("VPN %s Creating ACL Profile %s" % (vpnname, shortname))
cmd.create.acl_profile.name = shortname
cmd.create.acl_profile.vpn_name = vpnname
solace.rpc(str(cmd))

# Allow acl profile to publish
cmd = SolaceXMLBuilder("VPN %s Setting ACL Profile to allow publishing" % vpnname)
cmd.acl_profile.name = shortname
cmd.acl_profile.vpn_name=vpnname
cmd.acl_profile.publish_topic.default_action.allow
solace.rpc(str(cmd))

# ACL Profile allow subscribe
cmd = SolaceXMLBuilder("VPN %s Allowing ACL Profile to subscribe to VPN" % vpnname)
cmd.acl_profile.name = shortname
cmd.acl_profile.vpn_name = vpnname
cmd.acl_profile.subscribe_topic.default_action.allow
solace.rpc(str(cmd))

cmd = SolaceXMLBuilder("VPN %s Allowing ACL Profile to connect to VPN" % vpnname)
cmd.acl_profile.name = shortname
cmd.acl_profile.vpn_name = vpnname
cmd.acl_profile.client_connect.default_action.allow
solace.rpc(str(cmd))

# Users
for username in usernames:
    # Create the USER
    cmd = SolaceXMLBuilder("New User %s" % username)
    cmd.create.client_username.username = username
    cmd.create.client_username.vpn_name = vpnname
    solace.rpc(str(cmd))

    # Disable / Shutdown User ( else we cant change profiles )
    cmd = SolaceXMLBuilder("Disabling User %s" % username)
    cmd.client_username.username = username
    cmd.client_username.vpn_name = vpnname
    cmd.client_username.shutdown
    solace.rpc(str(cmd))

    # Client Profile
    cmd = SolaceXMLBuilder("Setting User %s client profile to %s" % (username,client_profile))
    cmd.client_username.username = username
    cmd.client_username.vpn_name = vpnname
    cmd.client_username.client_profile.name = client_profile
    solace.rpc(str(cmd))

    # Set client user profile
    cmd = SolaceXMLBuilder("Set User %s ACL Profile to %s" % (username, shortname))
    cmd.client_username.username = username
    cmd.client_username.vpn_name = vpnname
    cmd.client_username.acl_profile.name = shortname
    solace.rpc(str(cmd))

    # No Guarenteed Endpoint
    cmd = SolaceXMLBuilder("Default User %s guaranteed endpoint override" % username)
    cmd.client_username.username = username
    cmd.client_username.vpn_name = vpnname
    cmd.client_username.no.guaranteed_endpoint_permission_override
    solace.rpc(str(cmd))

    # No Subscription Managemer
    cmd = SolaceXMLBuilder("Default User %s subscription manager" % username)
    cmd.client_username.username = username
    cmd.client_username.vpn_name=vpnname
    cmd.client_username.no.subscription_manager
    solace.rpc(str(cmd))

    # Set User Password
    cmd = SolaceXMLBuilder("Set User %s password")
    cmd.client_username.username = username
    cmd.client_username.vpn_name = vpnname
    cmd.client_username.password.password = password
    solace.rpc(str(cmd))

    # Enable User
    cmd = SolaceXMLBuilder("Enable User %s" % username)
    cmd.client_username.username = username
    cmd.client_username.vpn_name = vpnname
    cmd.client_username.no.shutdown
    solace.rpc(str(cmd))

# for loop to create queues
for queuename in queues:
    # Create some queues now
    cmd = SolaceXMLBuilder("Creating Queue %s" % queuename["name"])
    cmd.message_spool.vpn_name = vpnname
    cmd.message_spool.create.queue.name=queuename["name"]
    solace.rpc(str(cmd))

    # Shutdown the queue ( cause it might have existed and we cant change parameters if its up )
    cmd = SolaceXMLBuilder("Shutdown Queue %s" % queuename["name"])
    cmd.message_spool.vpn_name = vpnname
    cmd.message_spool.queue.name = queuename["name"]
    cmd.message_spool.queue.shutdown
    solace.rpc(str(cmd))

    # Non Exclusive queue
    cmd = SolaceXMLBuilder("Set Queue %s to Non Exclusive " % queuename["name"] )
    cmd.message_spool.vpn_name = vpnname
    cmd.message_spool.queue.name = queuename["name"]
    cmd.message_spool.queue.access_type.non_exclusive
    solace.rpc(str(cmd))

    # Queue Owner
    cmd = SolaceXMLBuilder("Set Queue %s owner to %s" % (queuename["name"], shortname))
    cmd.message_spool.vpn_name = vpnname
    cmd.message_spool.queue.name = queuename["name"]
    cmd.message_spool.queue.owner.owner = usernames[0]
    solace.rpc(str(cmd))

    cmd = SolaceXMLBuilder("Settings Queue %s max bind count to %s" % (queuename["name"], maxbindcount))
    cmd.message_spool.vpn_name = vpnname
    cmd.message_spool.queue.name = queuename["name"]
    cmd.message_spool.queue.max_bind_count.value = maxbindcount
    solace.rpc(str(cmd))

    # Configure Queue Spool Usage
    cmd = SolaceXMLBuilder("Set Queue %s spool size: %s" % (queuename["name"], queuespoolsize))
    cmd.message_spool.vpn_name = vpnname
    cmd.message_spool.queue.name = queuename["name"]
    cmd.message_spool.queue.max_spool_usage.size = queuespoolsize
    solace.rpc(str(cmd))

    # Enable the Queue
    cmd = SolaceXMLBuilder("Enabling Queue %s" % queuename["name"])
    cmd.message_spool.vpn_name = vpnname
    cmd.message_spool.queue.name = queuename["name"]
    cmd.message_spool.queue.no.shutdown.full
    solace.rpc(str(cmd))
