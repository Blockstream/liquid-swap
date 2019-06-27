#!/usr/bin/env bash
set -e

apt update -qq
apt upgrade --no-install-recommends -yqq
apt install --no-install-recommends -yqq curl python3-pip python3-setuptools python3-pkg-resources python3-wheel python3-virtualenv virtualenv jq imagemagick python3-dev ruby ruby-dev rubygems build-essential
gem install --no-ri --no-rdoc fpm

virtualenv -p python3 .venvfbs
source .venvfbs/bin/activate
pip install -r ./tools/fbs/requirements.txt
pip install .
./tools/fbs/cleanup.sh
./tools/fbs/setup.sh
fbs freeze
fbs installer
deactivate
rm -rf .venvfbs
