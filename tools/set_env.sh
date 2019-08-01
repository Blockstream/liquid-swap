#!/bin/sh

echo "** Setting environment variables..."
ELEMENTSDIR1="$HOME/elementsdir1"
ELEMENTSDIR2="$HOME/elementsdir2"
ELEMENTSPATH=$(echo ${1:-"$HOME/elements/src"} | sed 's,/$,,')
OTCPATH=$(echo ${2:-"${PWD}"} | sed 's,/$,,')

echo "ELEMENTSPATH: $ELEMENTSPATH"
echo "OTCPATH:    $OTCPATH"

C1="$ELEMENTSDIR1/elements.conf"
C2="$ELEMENTSDIR2/elements.conf"

export ELEMENTSPATH
export OTCPATH
export ELEMENTSDIR1
export ELEMENTSDIR2
export C1
export C2

${OTCPATH}/tools/cleanup.sh

echo "** Creating aliases e1d e1c e2d e2c"
ELEMENTSPATH=$(echo ${1:-"$HOME/elements/src"} | sed 's,/$,,')
alias e1d="$ELEMENTSPATH/elementsd -conf=$C1"
alias e1c="$ELEMENTSPATH/elements-cli -conf=$C1"
alias e2d="$ELEMENTSPATH/elementsd -conf=$C2"
alias e2c="$ELEMENTSPATH/elements-cli -conf=$C2"

export e1d
export e1c
export e2d
export e2c
