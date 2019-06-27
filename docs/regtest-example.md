# Regtest CLI example

## Setting up a test environment

The following scripts will initialize two different Liquid regtest instances connected
to each other on your local network. Their respective data directories are defined and created by
`/tools/set_env.sh` and located in `~/liquiddir1/` and `~/liquiddir2/`.

Ensure CLI is installed,
```
liquidswap-cli --help
```

The following script will create aliases such as `l1c`, `l2c`, `l1d`, `l2d`,
`C1`, `C2` for liquid-cli, liquidd and liquid.conf files respectively. To set
the environment variables run,
```
. ./tools/set_env.sh "{path to liquid binaries}"
```

To test your newly created environment variables,
```
$ type l1c
l1c is aliased to `{path to liquid binaries}/liquid-cli -conf={home folder}/liquiddir1/liquid.conf'

$ echo $C1
{home folder}/liquiddir1/liquid.conf
```

Start liquid liquid regtest instances,
```
./tools/start_liquid_instances.sh
```

Create a assets and export asset labels,
```
. ./tools/createassets.sh
```

Use `l1c` and `l2c` to query the nodes and test your setup,
```
l1c getbalance
l2c getwalletinfo
```

To stop the regtest instances at any point or after running the example,
```
./tools/stop_liquid_instances.sh
```

## Simulate a swap

If the testing environment was not created using the setup scripts provided,
replace `C1` and `C2` variables with your regtest `liquid.conf` files.
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
$ l1c generate 1
$ l1c getbalance
$ l2c getbalance
```

You can now stop the regtest instances.
