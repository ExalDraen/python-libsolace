#!/usr/bin/env python
"""
.. module:: bin
.. currentmodule:: solace-provision

Reads a config XML file for VPN's owned by `owner`, Then get a list of all products which use those VPNs.

Provision the VPN, QUEUES and the USERS of that VPN to the environment specified

Examples:

Running with a local XML file
./bin/solace-provision.py -e dev -p SolaceTest --xmlfile config.xml

Running with a local XML file with shutdown both queues and users before modification, re-enable post
./bin/solace-provision.py -e dev -p SolaceTest --xmlfile config.xml -s b

Running with a local XML file with shutdown only queues before modification, re-enable post
./bin/solace-provision.py -e dev -p SolaceTest --xmlfile config.xml -s q


The example above reads through the config XML for VPN's owned by SolaceTest, and then scan for
products using those VPN's and builds up the commands to be exectuted in order to provision the VPN and USERS. This
script will then use libpipeline.api.solace to connect to the correct 'dev' appliances and post the data to the SEMP
API on those devices.

"""

import os
import sys
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s %(levelname)s %(message)s', stream=sys.stdout)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger().setLevel(logging.INFO)
from optparse import OptionParser

try:
    import simplejson as json
except:
    import json

import libsolace.settingsloader as settings

try:
    import libsolace
    from libsolace import SolaceAPI
    from libsolace.SolaceProvision import SolaceProvision
except:
    print("Unable to import required libraries, is libsolace installed? try 'pip install "
          "git+https://git.somedomain.com/git/libsolace.git'")
    raise
else:
    logging.info("Using libsolace version: %s" % libsolace.__version__)


# load a class that implements the AbstractSolaceCMDB methods
# CMDBClass = getattr(libsolace, settings.SOLACE_CMDB)

if __name__ == '__main__':
    """ parse opts, read site.xml, start provisioning vpns. """

    usage = '''Examples:

    Running with a specified XML config file
    ./bin/solace-provision.py -e dev -p SolaceTest  -x https://svn.mydomain.com/v1.0.2.4/site.xml

    Running Testmode ( no-changes, just XML validation )
    ./bin/solace-provision.py -e dev -p SolaceTest  -x https://svn.mydomain.com/v1.0.2.4/site.xml --testmode

    Running with the default release site-config XML
    ./bin/solace-provision.py -e dev -p SolaceTest

    Running with a local XML file
    ./bin/solace-provision.py -e dev -p SolaceTest  --xmlfile tests/index.xml
    '''

    jobdata = {}

    try:
        # Get version of config were shipping, this should be used with RAT or JIRA.
        jobdata['defaultversion'] = os.environ.get('GO_PIPELINE_LABEL') # Get the version were releasing from environment variable

        # because GO sets vars to '' instead of None
        for k in jobdata:
            if jobdata[k] == '':
                jobdata[k] = None
    except Exception, e:
        logging.warn("Please export GO_PIPELINE_LABEL if not using this from GO. error: %s" % e)
        raise

    # Args Builder
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--env", "--environment", action="store", type="string", dest="env",
        help="environment to run job in eg:[ dev | ci1 | si1 | qa1 | pt1 | prod ]")
    parser.add_option("-p", "--product", action="store", type="string", dest="product",
        help="owner name as in sitexml eg: SolaceTest")
    parser.add_option("-v", "--version", action="store", type="string", dest="version",
        default=jobdata['defaultversion'], help="version to release eg: '1.2.3.4'")
    parser.add_option("--soltr_version", action="store", type="string", dest="soltr_version",
        default=None, help="semp language version")
    parser.add_option("-s", "--shutdown", action="store", type="string", dest="shutdown_on_apply",
        default='n', help="--shutdown=n for none OR --shutdown=b for both OR --shutdown=q for queues OR --shutdown=u for user during config update, only required if changing existing queue/user")
    parser.add_option("-x", "--xmlurl", action="store", type="string", dest="xmlurl",
        default=settings.CMDB_URL, help="sitexml URL to use as config base, can be authenticating SVN url too!'")
    parser.add_option("-f", "--xmlfile", action="store", type="string", dest="xmlfile",
        default=None, help="path to sitexml file if on local storage")
    parser.add_option("-t", "--testmode", action="store_true", dest="testmode",
        default=False, help="only test configuration and exit")
    parser.add_option("--aclprofile", action="store", type="string", dest="acl_profile",
        default="default", help="client acl profile to associate")
    parser.add_option("-c", "--clientprofile", action="store", type="string", dest="clientprofile",
        default="glassfish", help="client profile to associate, must exist")
    parser.add_option("--no-create-queues", action="store_false", dest="create_queues",
        default=True, help="prevent queue creation")
    parser.add_option("--no-detect-status", action="store_false", dest="detect_status",
        default=True, help="disable detection of primary and backup statuses")

    parser.add_option("-d", "--debug", action="store_true", dest="debugmode",
        default=False, help="enable debug mode logging")

    (options, args) = parser.parse_args()

    if not options.env:
        parser.print_help()
        sys.exit()
    if options.debugmode:
        logging.getLogger().setLevel(logging.DEBUG)
    if not options.product:
        parser.print_help()
        sys.exit()
    # if not options.version:
    #     parser.print_help()
    #     sys.exit()
    if options.testmode:
        logging.info("Test mode active")
    options.shutdown_on_apply = options.shutdown_on_apply[0]

    if options.shutdown_on_apply == 'n':
        logging.info("Setting options.shutdown_on_apply to False")
        options.shutdown_on_apply = False

    logging.info("Shutdown setting: %s" % options.shutdown_on_apply)

    # now we override the settings with the options
    if options.xmlurl and not options.xmlfile:
        settings.CMDB_URL = options.xmlurl
        xmlfile = None
    elif options.xmlfile:
        logging.info('Settings XML file to Local')
        xmlfile = open(options.xmlfile, 'r')
        settings.CMDB_URL = None

    settings.env = options.env.lower()
    settings.product = options.product

    logging.info('CMDB_URL: %s' % settings.CMDB_URL)

    # load the cmdb API client
    cmdbapi_class = libsolace.plugin_registry(settings.SOLACE_CMDB_PLUGIN, settings=settings)

    # configure the client ( what init would normally do, but the plugin system
    # lacks the ability to implement stuff in init )
    cmdbapi = cmdbapi_class(settings=settings, environment=options.env)

    # get the list of vpns to provision
    vpns = cmdbapi.get_vpns_by_owner(options.product, environment=options.env)

    logging.info('VPNs: %s' % json.dumps(str(vpns), ensure_ascii=False))
    if vpns == []:
        logging.warn("No VPN found with that owner / componentName")
        raise Exception

    logging.info("VPNS %s" % vpns)

    # Call main with environment from command line
    for vpn in vpns:
        users = cmdbapi.get_users_of_vpn(vpn['id'], environment=options.env)
        logging.info(users)
        queues = cmdbapi.get_queues_of_vpn(vpn['id'], environment=options.env)
        logging.info(queues)

        logging.info('Found vpn %s' % json.dumps(str(vpn), ensure_ascii=False))
        logging.info('Found users %s' % users)
        logging.info('Found queues %s' % queues)
        logging.info("Provisioning %s" % vpn['id'])

        result = SolaceProvision(
            vpn_dict = vpn,
            queue_dict = queues,
            environment = options.env,
            client_profile = options.clientprofile,
            users_dict = users,
            testmode = options.testmode,
            shutdown_on_apply = options.shutdown_on_apply,
            version = options.soltr_version,
            detect_status = options.detect_status,
            create_queues = options.create_queues
        )
