# Create an installer
Create an installer for your OS using [fbs](https://build-system.fman.io/manual/)

```
virtualenv -p python3 fbsvenv
source fbsvenv/bin/activate
./tools/fbs/setup.sh
fbs freeze
fbs installer
```

Remove all created files
```
./tools/fbs/cleanup.sh
```
