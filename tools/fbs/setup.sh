#!/bin/sh

# FIXME: consider changing repo structure instead of moving files around

mkdir -p src/main/python
mkdir -p src/main/icons/base
mkdir -p src/main/icons/linux
mkdir -p src/main/icons/mac
mkdir -p src/build/settings

cp tools/fbs/base.json src/build/settings/
cp tools/fbs/linux.json src/build/settings/
cp tools/fbs/mac.json src/build/settings/
cp tools/fbs/main.py src/main/python/

python tools/fbs/set_version.py

ICON=liquidswap/gui/ui/icons/app-icon.png
ICON_FOLDER=src/main/icons/

convert -alpha on -resize x16 $ICON ${ICON_FOLDER}Icon.ico

convert -alpha on -resize x16 $ICON ${ICON_FOLDER}base/16.png
convert -alpha on -resize x24 $ICON ${ICON_FOLDER}base/24.png
convert -alpha on -resize x32 $ICON ${ICON_FOLDER}base/32.png
convert -alpha on -resize x48 $ICON ${ICON_FOLDER}base/48.png
convert -alpha on -resize x64 $ICON ${ICON_FOLDER}base/64.png

convert -alpha on -resize x128 $ICON ${ICON_FOLDER}linux/128.png
convert -alpha on -resize x256 $ICON ${ICON_FOLDER}linux/256.png
convert -alpha on -resize x512 $ICON ${ICON_FOLDER}linux/512.png
convert -alpha on -resize x1024 $ICON ${ICON_FOLDER}linux/1024.png

convert -alpha on -resize x128 $ICON ${ICON_FOLDER}mac/128.png
convert -alpha on -resize x256 $ICON ${ICON_FOLDER}mac/256.png
convert -alpha on -resize x512 $ICON ${ICON_FOLDER}mac/512.png
convert -alpha on -resize x1024 $ICON ${ICON_FOLDER}mac/1024.png
