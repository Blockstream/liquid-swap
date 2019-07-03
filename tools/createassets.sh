#!/bin/sh
#
# create 2 asset for a elementsregest with 2 nodes

rm -f .logs

# wally.base58check_from_bytes(b'\x4b' + b'\x00'*20)
DUMMY_ADDR=XBMEr9McFXkiLWTVqTyuNQR1CqKkMPMn6L

${LIQUIDPATH}/liquid-cli -conf=$C1 getwalletinfo >> .logs
${LIQUIDPATH}/liquid-cli -conf=$C2 getwalletinfo >> .logs

${LIQUIDPATH}/liquid-cli -conf=$C1 sendtoaddress $(${LIQUIDPATH}/liquid-cli -conf=$C1 getnewaddress) 21000000 "" "" true >> .logs
${LIQUIDPATH}/liquid-cli -conf=$C1 generatetoaddress 2 $DUMMY_ADDR >> .logs
${LIQUIDPATH}/liquid-cli -conf=$C1 sendtoaddress $(${LIQUIDPATH}/liquid-cli -conf=$C2 getnewaddress) 100 >> .logs
${LIQUIDPATH}/liquid-cli -conf=$C1 generatetoaddress 2 $DUMMY_ADDR >> .logs
${LIQUIDPATH}/liquid-cli -conf=$C1 issueasset 10 0 >> .logs
${LIQUIDPATH}/liquid-cli -conf=$C1 generatetoaddress 2 $DUMMY_ADDR >> .logs
ASSET1=$(${LIQUIDPATH}/liquid-cli -conf=$C1 getbalance | jq -r 'del(.bitcoin) | keys[0]')
${LIQUIDPATH}/liquid-cli -conf=$C2 issueasset 20 0 >> .logs
${LIQUIDPATH}/liquid-cli -conf=$C2 generatetoaddress 2 $DUMMY_ADDR >> .logs
ASSET2=$(${LIQUIDPATH}/liquid-cli -conf=$C2 getbalance | jq -r 'del(.bitcoin) | keys[0]')

echo "ASSET1: "$ASSET1
echo "ASSET2: "$ASSET2

export ASSET1
export ASSET2
