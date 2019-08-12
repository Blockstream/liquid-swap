#!/usr/bin/env bash
set -e

virtualenv -p python3 .venvfbs
source .venvfbs/bin/activate
pip install -r ./tools/fbs/requirements.txt
pip install .[GUI]
./tools/fbs/cleanup.sh
./tools/fbs/setup.sh
fbs freeze
fbs installer
deactivate
rm -rf .venvfbs
