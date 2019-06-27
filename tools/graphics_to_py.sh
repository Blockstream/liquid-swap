#!/bin/sh

GUI=./liquidswap/gui/
UI=${GUI}ui/
QT=${GUI}qt/

pyuic5 ${UI}dialogaddnewasset.ui -o ${QT}dialogaddnewasset.py
pyuic5 ${UI}dialogcopy.ui -o ${QT}dialogcopy.py
pyuic5 ${UI}dialogpaste.ui -o ${QT}dialogpaste.py
pyuic5 ${UI}dialogurl.ui -o ${QT}dialogurl.py
pyuic5 ${UI}windowaccept.ui -o ${QT}windowaccept.py
pyuic5 ${UI}windowfinalize.ui -o ${QT}windowfinalize.py
pyuic5 ${UI}windowpropose.ui -o ${QT}windowpropose.py
pyuic5 ${UI}windowstart.ui -o ${QT}windowstart.py

if [ "$RESOURCE" ]; then
    pyrcc5 ${UI}resource.qrc -o ${GUI}resource_rc.py
fi

sed -i 's/import resource_rc/from liquidswap.gui import resource_rc/' ${QT}windowstart.py
