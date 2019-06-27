#!/bin/bash

set -e

./tools/start_liquid_instances.sh > /dev/null
sleep 10
. ./tools/createassets.sh > /dev/null

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

liquidswap-cli -r -c $C1 propose $ASSET1 1 $ASSET2 2 -o proposal_simple.txt
liquidswap-cli -r -c $C2 info proposal_simple.txt
liquidswap-cli -r -c $C2 accept proposal_simple.txt -o accepted_simple.txt
liquidswap-cli -r -c $C1 info accepted_simple.txt
liquidswap-cli -r -c $C1 finalize accepted_simple.txt -s

./tools/stop_liquid_instances.sh > /dev/null
rm *_simple.txt
