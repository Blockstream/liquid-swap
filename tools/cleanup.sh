#!/bin/sh

echo "** Erasing and (re)creating elementsdir regtest directories"
rm -rf "$ELEMENTSDIR1"
rm -rf "$ELEMENTSDIR2"
mkdir $ELEMENTSDIR1
mkdir $ELEMENTSDIR2
cp $OTCPATH/tools/conf/elements1.conf $C1
cp $OTCPATH/tools/conf/elements2.conf $C2
echo "datadir=$HOME/elementsdir1" >> $C1
echo "datadir=$HOME/elementsdir2" >> $C2
