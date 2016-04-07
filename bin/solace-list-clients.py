#!/usr/bin/env python

"""

Show solace clients and counts, optionally pump all stats into influxdb

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
pp = pprint.PrettyPrinter(indent=4, width=20)

if __name__ == '__main__':
    """ parse opts, read site.xml, start provisioning vpns. """

    usage = "list all vpns in an environment"
    parser = OptionParser(usage=usage)
    parser.add_option("-e", "--env", "--environment", action="store", type="string", dest="env",
                      help="environment to run job in eg:[ dev | ci1 | si1 | qa1 | pt1 | prod ]")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="toggles solace debug mode")
    parser.add_option("--details", action="store_true", dest="details", help="Show client details", default=False)
    parser.add_option("--stats", action="store_true", dest="stats", help="Show client stats", default=False)
    parser.add_option("--client", action="store", type="string", dest="client", help="client filter e.g. 'dev_*'",
                      default="*")
    parser.add_option("--influxdb", action="store_true", dest="influxdb", help="influxdb url and port", default=False)
    parser.add_option("--influxdb-host", action="store", type="string", dest="influxdb_host", help="influxdb hostname", default="defiant")
    parser.add_option("--influxdb-port", action="store", type="int", dest="influxdb_port", help="influxdb port", default=8086)
    parser.add_option("--influxdb-user", action="store", type="string", dest="influxdb_user", help="influxdb user", default="root")
    parser.add_option("--influxdb-pass", action="store", type="string", dest="influxdb_pass", help="influxdb pass", default="root")
    parser.add_option("--influxdb-db", action="store", type="string", dest="influxdb_db", help="influxdb db name", default="solace-clients")


    (options, args) = parser.parse_args()

    if not options.env:
        parser.print_help()
        sys.exit()
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if options.influxdb:
        logging.info("Connecting to influxdb")
        from influxdb import InfluxDBClient
        try:
            client = InfluxDBClient(options.influxdb_host, options.influxdb_port, options.influxdb_user,
                                    options.influxdb_pass, options.influxdb_db)
            try:
                client.create_database(options.influxdb_db)
            except Exception, e:
                logging.warn("Unable to create database, does it already exist?")
        except Exception, e:
            logging.error("Unable to connect to influxdb")
            sys.exit(1)

    # forces read-only
    options.testmode = True
    settings.env = options.env.lower()

    logging.info("Connecting to appliance in %s, testmode:%s" % (settings.env, options.testmode))
    connection = SolaceAPI(settings.env, testmode=options.testmode)

    if options.details:
        connection.x = SolaceXMLBuilder("show clients details")
        connection.x.show.client.name = options.client
        connection.x.show.client.detais
    elif options.stats:
        connection.x = SolaceXMLBuilder("show clients stats")
        connection.x.show.client.name = options.client
        connection.x.show.client.stats

    # get the clients
    clients = connection.rpc(str(connection.x), primaryOnly=True)
    count = 0

    # print clients[0]

    timeNow = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())

    startTime = time.time()

    for c in clients[0]['rpc-reply']['rpc']['show']['client']['primary-virtual-router']['client']:
        j = demjson.encode(c)
        p = json.loads(j)

        if options.stats:
            t = {}
            for k in p["stats"]:
                logging.debug("Key: %s value %s" % (k, p["stats"][k]))

                try:
                    t[k] = long(p["stats"][k])
                except Exception, ve:
                    logging.debug("skipping")
                    pass

            json_body = [{
                "measurement": "client-stats",
                "tags": {
                    "message-vpn": p['message-vpn'],
                    "name": p['name']
                },
                "fields": t,
                "time": timeNow
            }]


        # print json.dumps(json_body)

        # print json.dumps(json_body, sort_keys=False, indent=4, separators=(',', ': '))
        client.write_points(json_body)

    logging.info("Total Clients: %s" % count)
    logging.info("Time Taken: %s" % (time.time()-startTime) )

