#!/bin/sh

echo "** Stopping elements regtest instances..."
${ELEMENTSPATH}/elements-cli -conf=$C1 stop
${ELEMENTSPATH}/elements-cli -conf=$C2 stop
