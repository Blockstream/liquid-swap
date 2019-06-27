#!/bin/sh

$OTCPATH/tools/cleanup.sh

#TODO: add core instance to validate pegins
echo "** Warning: pegins are not validated"

echo "** Raising two connected liquid regtest instances"
${LIQUIDPATH}/liquidd -conf=$C1
${LIQUIDPATH}/liquidd -conf=$C2
