#!/bin/sh

echo "** Stopping liquid regtest instances..."
${LIQUIDPATH}/liquid-cli -conf=$C1 stop
${LIQUIDPATH}/liquid-cli -conf=$C2 stop
