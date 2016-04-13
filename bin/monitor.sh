#!/bin/bash

while true; do

./bin/solace-metrics.py -e prod --clients &
./bin/solace-metrics.py -e prod --vpns
./bin/solace-metrics.py -e prod --spool
./bin/solace-metrics.py -e prod --client-spools
#./bin/solace-list-vpns.py -e prod | xargs -i{} ./bin/solace-metrics.py -e prod --spool --filter {}
echo "sleeping"
sleep 10
done;

