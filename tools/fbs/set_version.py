#!/usr/bin/env python3

from liquidswap import __version__

with open('src/build/settings/base.json') as f:
    new_text = f.read().replace('VERSION', __version__)

with open('src/build/settings/base.json', 'w') as f:
    f.write(new_text)
