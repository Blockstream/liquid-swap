#!/bin/bash
set -exo pipefail

echo "Dir{Cache ${PIP_CACHE_DIR}}" >> /etc/apt/apt.conf
echo "Dir::Cache ${PIP_CACHE_DIR};" >> /etc/apt/apt.conf


mkdir -p ${PIP_CACHE_DIR}/archives/partial
find ${PIP_CACHE_DIR}


apt update -qq
apt upgrade --no-install-recommends -yqq
apt install --no-install-recommends -yqq curl python3-pip python3-setuptools python3-pkg-resources python3-wheel python3-virtualenv virtualenv jq

virtualenv -p python3 venv
source venv/bin/activate
pip install .[CLI,GUI]

pip install pycodestyle
# exclude copied and generated files
# ignore E125, E129, W605 and pycodestyle defaults
pycodestyle --exclude='*/qt*,*liquidrpc.py,*resource_rc.py' --ignore='E125,E129,W605,E121,E123,E126,E226,E24,E704,W503,W504' liquidswap/

SHA256SUM_ELEMENTS=9a0f6be1118e20979d2f8d359e9ad8a608f372addbb4896dc26c18cc8eb826b4
if [ ! -f ${PIP_CACHE_DIR}/elements.tar.gz ]; then
    curl -sL -o ${PIP_CACHE_DIR}/elements.tar.gz https://github.com/ElementsProject/elements/releases/download/elements-0.18.1.1/elements-0.18.1.1-x86_64-linux-gnu.tar.gz
    echo "${SHA256SUM_ELEMENTS}  ${PIP_CACHE_DIR}/elements.tar.gz" | sha256sum --check
fi
tar xzf ${PIP_CACHE_DIR}/elements.tar.gz -C .
ln -s elements-0.18.1.1 elements

. ./tools/set_env.sh "${PWD}/elements/bin" "$PWD"
./tools/simpleswap.sh
