#!/usr/bin/env python

"""

Gather solace metrics from SEMP API and pump them into influxdb


TESTING


docker run -d --name=grafana -p 3000:3000 grafana/grafana

docker run -d --name=influxdb2 -p 8083:8083 -p 8086:8086 -e ADMIN_USER="root" -e INFLUXDB_INIT_PWD="admin" -e PRE_CREATE_DB="db1;db2;db3" unixunion/influxdb:latest


"""

import logging
import sys

logging.basicConfig(format='[%(module)s] %(filename)s:%(lineno)s %(asctime)s %(levelname)s %(message)s',
                    stream=sys.stderr)
import libsolace.settingsloader as settings
from libsolace.SolaceAPI import SolaceAPI
from libsolace.SolaceXMLBuilder import SolaceXMLBuilder
from optparse import OptionParser
import simplejson as json
import sys
import pprint
import demjson
from time import gmtime, strftime
import time

try:
    from influxdb import InfluxDBClient
except Exception, e:
    print "Unable to import influxdb, try pip install influxdb"

pp = pprint.PrettyPrinter(indent=4, width=20)


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        else:
            try:
                out[str(name[:-1])] = long(x)
            except Exception, e:
                # strip out non number
                pass

    flatten(y)
    # print json.dumps(out, sort_keys=False, indent=4, separators=(',', ': '))
    return out


def pump_metrics(environment, obj, measurement, influx_client=None, tag_key_name=None, tags={}):
    """
    Sends the metrics off to influxDB, currently ignores nested key value sets. FIXME TODO

    :param tags:
    :param tag_key_name: keys in the object which are to be tags e.g. name, message-vpn, client-username
    :param environment:
    :param obj:
    :param measurement:
    :param influx_client:
    :return:
    """

    if tag_key_name is None:
        tag_key_name = ["name", "message-vpn"]
    j = demjson.encode(obj)
    p = json.loads(j)

    t = flatten_json(obj)
    # print json.dumps(p, sort_keys=False, indent=4, separators=(',', ': '))

    # print "Keys to plot"
    # print json.dumps(t, sort_keys=False, indent=4, separators=(',', ': '))

    json_body = [{
        "measurement": measurement,
        "tags": {
            "environment": environment
        },
        "fields": t,
        "time": timeNow
    }]

    for k in tag_key_name:
        if p.has_key(k):
            json_body[0]['tags'][k] = p[k]
        else:
            logging.warn("Key %s is not present, this is only a warning" % k)

    for tag in tags:
        json_body[0]['tags'][tag] = tags[tag]

    # print json.dumps(json_body, sort_keys=False, indent=4, separators=(',', ': '))
    # client.write_points(json_body)

    try:
        influx_client.write_points(json_body)
    except Exception, e:
        logging.error(e.message)
        logging.error("Unable to write to influxdb")


def get_time():
    return strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())


timeNow = get_time();

if __name__ == '__main__':
    """ Gather metrics from Solace's SEMP API and places the results into influxdb """

    usage = "list all vpns in an environment"
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--env", "--environment", action="store", type="string", dest="env",
                      help="environment to run job in eg:[ dev | ci1 | si1 | qa1 | pt1 | prod ]")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="toggles solace debug mode")

    parser.add_option("--influxdb-host", action="store", type="string", dest="influxdb_host", help="influxdb hostname",
                      default="defiant")
    parser.add_option("--influxdb-port", action="store", type="int", dest="influxdb_port", help="influxdb port",
                      default=8086)
    parser.add_option("--influxdb-user", action="store", type="string", dest="influxdb_user", help="influxdb user",
                      default="root")
    parser.add_option("--influxdb-pass", action="store", type="string", dest="influxdb_pass", help="influxdb pass",
                      default="root")
    parser.add_option("--influxdb-db", action="store", type="string", dest="influxdb_db", help="influxdb db name",
                      default="solace")

    parser.add_option("--clients", action="store_true", dest="clients", help="gather clients stats", default=False)
    # parser.add_option("--client-users", action="store_true", dest="clientusers", help="gather client user stats",
    #                   default=False)
    parser.add_option("--client-spools", action="store_true", dest="clientspools", help="gather client spool stats",
                      default=False)

    parser.add_option("--vpns", action="store_true", dest="vpns", help="gather vpns stats", default=False)
    parser.add_option("--spool", action="store_true", dest="spool", help="gather spool stats", default=False)

    parser.add_option("--filter", action="store", type="string", dest="filter", help="filter e.g. '*' / 'prod_foo'",
                      default="*")

    parser.add_option("--retention", action="store", dest="retention",
                      help="retension time eg 1h, 90m, 12h, 7d, and 4w", default="4w")
    parser.add_option("--set-retention", action="store_true", dest="update_retention", default=False,
                      help="update the retention default policy")

    (options, args) = parser.parse_args()

    if not options.env:
        parser.print_help()
        sys.exit()
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.info("Connecting to influxdb")

    try:
        client = InfluxDBClient(options.influxdb_host, options.influxdb_port, options.influxdb_user,
                                options.influxdb_pass, options.influxdb_db)
        try:
            logging.info("Creating database %s" % options.influxdb_db)
            client.create_database(options.influxdb_db)
        except Exception, e:
            logging.warn("Unable to create database, does it already exist?")
            # client.create_retention_policy("30d", "4w", 1, options.influxdb_db, True)
    except Exception, e:
        logging.error("Unable to connect to influxdb")
        sys.exit(1)

    if options.update_retention:
        logging.info("Altering retention policies")
        client.alter_retention_policy("default", duration="4w", replication=1, default=True)

    # forces read-only
    options.testmode = True
    settings.env = options.env.lower()

    logging.info("Connecting to appliance in %s, testmode:%s" % (settings.env, options.testmode))
    connection = SolaceAPI(settings.env, testmode=options.testmode)

    """
    Gather client stats, this is quite slow if you have MANY clients!
    """
    if options.clients:
        connection.x = SolaceXMLBuilder("show clients stats")
        connection.x.show.client.name = options.filter
        connection.x.show.client.stats

        # measurement point start
        startTime = time.time()

        # set time now immediately before we request
        timeNow = get_time()

        # get the clients
        clients = connection.rpc(str(connection.x), primaryOnly=True)

        # iterate over values of interest.
        for c in clients[0]['rpc-reply']['rpc']['show']['client']['primary-virtual-router']['client']:
            logging.debug(c)
            pump_metrics(options.env, c, "client-stats", influx_client=client, tag_key_name=["name", "message-vpn"])

        logging.info("Clients Gather and Commit Time: %s" % (time.time() - startTime))

    if options.clientspools:
        # get client spool stats
        connection.x = SolaceXMLBuilder("show clients spool stats")
        connection.x.show.client.name = options.filter
        connection.x.show.client.message_spool_stats

        # measurement point start
        startTime = time.time()

        # set time now immediately before we request
        timeNow = get_time()

        # get the clients
        clients = connection.rpc(str(connection.x), primaryOnly=True)
        # print json.dumps(clients[0], sort_keys=False, indent=4, separators=(',', ': '))

        # iterate over values of interest.
        for c in clients[0]['rpc-reply']['rpc']['show']['client']['primary-virtual-router']['client']:
            print "doc start"
            print json.dumps(c, sort_keys=False, indent=4, separators=(',', ': '))
            print "doc end"

            pump_metrics(options.env, c, "client-spool-stats", influx_client=client,
                         tag_key_name=["client-username", "message-vpn", "user", "name", "client-address", "platform",
                                       "profile", "acl-profile"])

        logging.info("Clients Gather and Commit Time: %s" % (time.time() - startTime))

    # if options.clientusers:
    #     connection.x = SolaceXMLBuilder("show client users stats")
    #     connection.x.show.client_username.name = options.filter
    #     connection.x.show.client_username.stats
    #
    #     # measurement point start
    #     startTime = time.time()
    #
    #     # set time now immediately before we request
    #     timeNow = get_time()
    #
    #     # get the clients
    #     clients = connection.rpc(str(connection.x), primaryOnly=True)
    #
    #     # iterate over values of interest.
    #     print json.dumps(clients[0], sort_keys=False, indent=4, separators=(',', ': '))
    #
    #     for c in clients[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames']:
    #         logging.debug(c)
    #         pump_metrics(options.env, c, "client-stats", influx_client=client, tag_key_name=["name", "message-vpn"])
    #
    #     logging.info("Client Users Gather and Commit Time: %s" % (time.time() - startTime))

    """
    Gather VPN Stats
    """
    if options.vpns:
        connection.x = SolaceXMLBuilder("show clients stats")
        connection.x.show.message_vpn.vpn_name = options.filter
        connection.x.show.message_vpn.stats

        startTime = time.time()

        # set time now immediately before we request
        timeNow = get_time()

        vpns = connection.rpc(str(connection.x), primaryOnly=True)

        # iterate over vpns
        for v in vpns[0]['rpc-reply']['rpc']['show']['message-vpn']['vpn']:
            logging.debug(v)
            pump_metrics(options.env, v, "vpn-stats", influx_client=client, tag_key_name=["name"])

        logging.info("Vpns Gather and Commit Time: %s" % (time.time() - startTime))

    if options.spool:

        tag_keys = []
        tags = {}

        connection.x = SolaceXMLBuilder("show global spool stats")
        if options.filter == "*":
            logging.info("Not Filtering")
            connection.x.show.message_spool
        else:
            logging.info("Filtering")
            tags["message-vpn"] = options.filter
            connection.x.show.message_spool.vpn_name = options.filter
        connection.x.show.message_spool.stats

        startTime = time.time()

        # set time now immediately before we request
        timeNow = get_time()

        vpnspools = connection.rpc(str(connection.x), primaryOnly=True)

        print json.dumps(vpnspools[0], sort_keys=False, indent=4, separators=(',', ': '))
        # logging.info(vpnspools[0])

        # iterate over vpns
        # for v in vpnspools[0]['rpc-reply']['rpc']['show']['message-spool']['message-spool-stats']:
        pump_metrics(options.env, vpnspools[0]['rpc-reply']['rpc']['show']['message-spool'], "spool-stats",
                     influx_client=client, tag_key_name=tag_keys, tags=tags)

        logging.info("Spool Gather and Commit Time: %s" % (time.time() - startTime))
