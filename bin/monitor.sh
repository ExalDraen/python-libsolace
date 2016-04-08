#!/bin/bash

while true; do

./bin/solace-metrics.py -e prod --clients
./bin/solace-metrics.py -e prod --vpns
./bin/solace-metrics.py -e prod --spool
#./bin/solace-list-vpns.py -e prod | xargs -i{} ./bin/solace-metrics.py -e prod --spool --filter {}

sleep 60
done;

