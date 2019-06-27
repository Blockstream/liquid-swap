#!/bin/sh

echo "** Erasing and (re)creating liquiddir regtest directories"
rm -rf "$LIQUIDDIR1"
rm -rf "$LIQUIDDIR2"
mkdir $LIQUIDDIR1
mkdir $LIQUIDDIR2
cp $OTCPATH/tools/conf/liquid1.conf $C1
cp $OTCPATH/tools/conf/liquid2.conf $C2
echo "datadir=$HOME/liquiddir1" >> $C1
echo "datadir=$HOME/liquiddir2" >> $C2
