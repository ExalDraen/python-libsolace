#!/usr/bin/env python
"""
solace-cli-user

This script takes some command line args and creates users for CLI + GUI purposes

"""
from optparse import OptionParser
import pprint
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
import libsolace.settingsloader as settings
settings.debugmode = False


def solace_provision_user(options=None):
    """ Creates a user within solace appliance cluster

    1. Connects to a both appliances in cluster
    2. Creates new user
    3. Assigns rights to user

    :param options: dictionary containig user details
        {'environment': 'ci1',
         'global_access_level': 'read-only',
         'password': 'readonly',
         'username': 'readonly'}

    :example of xml produced:
    <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
      <create>
        <username>
          <name>readonly</name>
          <password>readonly</password>
        </username>
      </create>
    </rpc>
    <rpc xmlns="http://www.solacesystems.com/semp/topic_routing/6_0">
      <username>
        <name>readonly</name>
        <global-access-level>
          <access-level>read-only</access-level>
        </global-access-level>
      </username>
    </rpc>

    """
    try:
        pprint.pprint(options.__dict__)
        # Create a client to the PT1 unit ( Update to connect to both devices and create USERS, ACL, CLIENT PROFILE )
        # only queues are replicated and JNDI
        print(options.__dict__)
        for environment in options.environment:
            solace = SolaceAPI(environment)

            # ACLS / Users
            cmd = SolaceXMLBuilder("Creating User %s" % options.username)
            cmd.create.username.name = options.username
            cmd.create.username.password = options.password
            solace.rpc(str(cmd))

            # Allow acl profile to publish
            cmd = SolaceXMLBuilder("Setting Permissions to %s" % options.global_access_level)
            cmd.username.name = options.username
            cmd.username.global_access_level.access_level = options.global_access_level
            solace.rpc(str(cmd))
    except:
        raise


if __name__ == "__main__":
    usage = '''Solace CLI User

    Creates / Sets passwords for CLI users of Solace-TR appliances.

    Examples:
    python solace-cli-user.py -e dev,ci1,si1,qa1,pt1 -u readonly -p readonly -l read-only
    python solace-cli-user.py -e pt1 -u readwrite -p rwpassword -l read-write
    python solace-cli-user.py -e pt1 -u superuser -p superpassword -l admin
    '''
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--environment", action="store", type="string", dest="environment",
                      help="environment to apply changes to eg:[ qa1 | ci1 | si1 | prod ] | qa1,si1,pt1")

    parser.add_option("-u", "--user", action="store", type="string", dest="username",
                      help="username to create or adjust")

    parser.add_option("-p", "--password", action="store", type="string", dest="password",
                      help="user's password")

    parser.add_option("-l", "--level", action="store", type="string", dest="global_access_level",
                      help="level, [read-only|read-write|admin]", default="read-only")

    # Parse Opts
    (options, args) = parser.parse_args()

    # Lowecase the environment because GO seems to use uppercase
    try:
        options.environment = options.environment.lower().split(',')
    except:
        parser.print_help()

    if not options.environment:   # if filename is not given
        parser.error('Environment Not Given')
    if not options.username:
        parser.error("Username Not Given")
    if not options.password:
        parser.error("Password Not Given")
    if not options.global_access_level:
        parser.error("Global Access Level Not Given")

    # call the provision function
    solace_provision_user(options=options)
