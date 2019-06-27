from setuptools import setup, find_packages

from liquidswap import __version__


setup(
    name='liquidswap',
    version=__version__,
    python_requires='>=3.5',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click==7.0',
        'PyQt5==5.11.3',
    ],
    entry_points={
        'console_scripts': [
            'liquidswap-cli=liquidswap.cli:cli',
        ],
        'gui_scripts': [
            'liquidswap-gui=liquidswap.gui.app:main',
        ],
    },
    description='Tool to swap Issued Asset on the Liquid Network using Confidential Transactions',
    url='https://github.com/blockstream/liquid-swap',
    author='Blockstream',
    license='LGPL3',
)
