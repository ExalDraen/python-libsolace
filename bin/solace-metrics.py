#!/usr/bin/env python

"""

Gather solace metrics from SEMP API and pump them into influxdb

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


def pump_metrics(environment, obj, measurement, influx_client=None, tag_key_name=None):
    """
    Sends the metrics off to influxDB, currently ignores nested key value sets. FIXME TODO

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

    print json.dumps(obj, sort_keys=False, indent=4, separators=(',', ': '))

    t = {}
    for k in p["stats"]:
        logging.debug("Key: %s value %s" % (k, p["stats"][k]))
        try:
            t[k] = long(p["stats"][k])
        except Exception, ve:
            logging.debug("skipping")
            pass

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
    parser.add_option("--client-users", action="store_true", dest="clientusers", help="gather client user stats", default=False)
    parser.add_option("--vpns", action="store_true", dest="vpns", help="gather vpns stats", default=False)
    parser.add_option("--retention", action="store", dest="retention", help="retension time eg 1h, 90m, 12h, 7d, and 4w", default="4w")
    parser.add_option("--set-retention", action="store_true", dest="update_retention", default=False, help="update the retention default policy")

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
        connection.x.show.client.name = "*"
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
            pump_metrics(options.env, c, "client-stats", client, ["name", "message-vpn"])

        logging.info("Clients Gather and Commit Time: %s" % (time.time() - startTime))

    if options.clientusers:
        connection.x = SolaceXMLBuilder("show client users stats")
        connection.x.show.client_username.name = "*"
        connection.x.show.client_username.stats

        # measurement point start
        startTime = time.time()

        # set time now immediately before we request
        timeNow = get_time()

        # get the clients
        clients = connection.rpc(str(connection.x), primaryOnly=True)

        # iterate over values of interest.
        logging.info(clients[0])
        for c in clients[0]['rpc-reply']['rpc']['show']['client-username']['client-usernames']:
            logging.debug(c)
            pump_metrics(options.env, c, "client-stats", client, ["name", "message-vpn"])

        logging.info("Client Users Gather and Commit Time: %s" % (time.time() - startTime))

    """
    Gather VPN Stats
    """
    if options.vpns:
        connection.x = SolaceXMLBuilder("show clients stats")
        connection.x.show.message_vpn.vpn_name = "*"
        connection.x.show.message_vpn.stats

        startTime = time.time()

        # set time now immediately before we request
        timeNow = get_time()

        vpns = connection.rpc(str(connection.x), primaryOnly=True)

        # iterate over vpns
        for v in vpns[0]['rpc-reply']['rpc']['show']['message-vpn']['vpn']:
            logging.debug(v)
            pump_metrics(options.env, v, "vpn-stats", client, ["name"])

        logging.info("Vpns Gather and Commit Time: %s" % (time.time() - startTime))
