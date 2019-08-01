#!/bin/sh

$OTCPATH/tools/cleanup.sh

#TODO: add core instance to validate pegins
echo "** Warning: pegins are not validated"

echo "** Raising two connected elements regtest instances"
${ELEMENTSPATH}/elementsd -conf=$C1
${ELEMENTSPATH}/elementsd -conf=$C2
