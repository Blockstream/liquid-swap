#!/bin/sh

echo "** Setting environment variables..."
LIQUIDDIR1="$HOME/liquiddir1"
LIQUIDDIR2="$HOME/liquiddir2"
LIQUIDPATH=$(echo ${1:-"$HOME/liquid/src"} | sed 's,/$,,')
OTCPATH=$(echo ${2:-"${PWD}"} | sed 's,/$,,')

echo "LIQUIDPATH: $LIQUIDPATH"
echo "OTCPATH:    $OTCPATH"

C1="$LIQUIDDIR1/liquid.conf"
C2="$LIQUIDDIR2/liquid.conf"

export LIQUIDPATH
export OTCPATH
export LIQUIDDIR1
export LIQUIDDIR2
export C1
export C2

${OTCPATH}/tools/cleanup.sh

echo "** Creating aliases l1d l1c l2d l2c"
alias l1d="$LIQUIDPATH/liquidd -conf=$C1"
alias l1c="$LIQUIDPATH/liquid-cli -conf=$C1"
alias l2d="$LIQUIDPATH/liquidd -conf=$C2"
alias l2c="$LIQUIDPATH/liquid-cli -conf=$C2"

export l1d
export l1c
export l2d
export l2c
