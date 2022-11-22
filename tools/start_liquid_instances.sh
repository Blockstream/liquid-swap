#!/bin/sh

$OTCPATH/tools/cleanup.sh

#TODO: add core instance to validate pegins
echo "** Warning: pegins are not validated"

echo "** Raising two connected elements regtest instances"
${ELEMENTSPATH}/elementsd -conf=$C1
${ELEMENTSPATH}/elementsd -conf=$C2

${ELEMENTSPATH}/elements-cli -conf=$C1 -rpcwait createwallet ""
${ELEMENTSPATH}/elements-cli -conf=$C2 -rpcwait createwallet ""
${ELEMENTSPATH}/elements-cli -conf=$C1 rescanblockchain
${ELEMENTSPATH}/elements-cli -conf=$C2 rescanblockchain
