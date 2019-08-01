# Regtest CLI example

## Setting up a test environment

The following scripts will initialize two different liquid elements regtest instances connected
to each other on your local network. Their respective data directories are defined and created by
`/tools/set_env.sh` and located in `~/elementsdir1/` and `~/elementsdir2/`.

Ensure CLI is installed.
```
liquidswap-cli --help
```

The following script will create aliases such as `e1c`, `e2c`, `e1d`, `e2d`,
`C1`, `C2` for elements-cli, elementsd and elements.conf files respectively. To set
the environment variables run,
```
. ./tools/set_env.sh "{path to elements binaries}"
```

To test your newly created environment variables,
```
$ type e1c
e1c is aliased to `{path to elements binaries}/elements-cli -conf={home folder}/elementsdir1/elements.conf'

$ echo $C1
{home folder}/elementsdir1/elements.conf
```

Start elements regtest instances,
```
./tools/start_liquid_instances.sh
```

Create a assets and export asset labels,
```
. ./tools/createassets.sh
```

Use `e1c` and `e2c` to query the nodes and test your setup,
```
e1c getbalance
e2c getwalletinfo
```

To stop the regtest instances at any point or after running the example,
```
./tools/stop_liquid_instances.sh
```

## Simulate a swap

If the testing environment was not created using the setup scripts provided,
replace `C1` and `C2` variables with your regtest `elements.conf` files.
To execute a swap in regtest mode,
```
liquidswap-cli --regtest -c $C1 propose $ASSET1 1 $ASSET2 2 --output proposal.txt
liquidswap-cli --regtest -c $C2 info proposal.txt
liquidswap-cli --regtest -c $C2 accept proposal.txt --output accepted.txt
liquidswap-cli --regtest -c $C1 info accepted.txt
liquidswap-cli --regtest -c $C1 finalize accepted.txt --send
```
To view the result,
```
$ e1c generatetoaddress 1 $(e1c getnewaddress)
$ e1c getbalance
$ e2c getbalance
```

You can now stop the regtest instances.
