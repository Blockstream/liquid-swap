# Authentication

Liquid Swap Tool needs to connect with a Elements daemon (elementsd) in order to query wallet data, broadcast transactions etc.
If Elements uses the default configurations, the tool will look for those 
automatically.
Otherwise it is possible to specify the Elements Node URL
(for example `http://user:password@host:port`) using the `-u` argument. You can also provide the path to the local elements.conf file using the `-c` argument.

For example, depending on what you have set for your Elements node, the commands might look like the following to start liquidswap:

```
liquidswap-cli -c ~/your_elements_dir/elements.conf

liquidswap-cli -u http://user:password@localhost:7041
```

If the Elements GUI (elements-qt) is used instead of the Elements daemon, add a line with `server=1` in the 
elements.conf, or launch it with `elements-qt -server`.

### Elements Node URL Example using the GUI
You can also specify the rpc credentials to use, as well as the location of the config file, using the GUI itself once opened.

For instance, suppose elementsd was launched locally with flags 
`-rpcuser=user -rpcpassword=password`.
To specify the credentials for node authentication, from the menu bar go to 
_Edit_ -> _Authentication_ -> Elements Node URL…_, and insert 
`http://user:password@localhost:7041`. 

### Elements Configuration File Example using the GUI
If you would rather authenticate using the credentials stored in elements.conf, and the file is not in the
default location, it must be specified within the tool.
To select it, from the menu bar go to 
_Edit_ -> _Authentication_ -> _Specify elements.conf…_ and choose the
configuration file used to start elementsd.

## Multi-wallet
When running Elements with multiple wallets, wallet-level RPC methods must specify
the wallet for which they are intended in each request.
To make the tool work within such a setting, it is necessary to either unload
all wallets except one, or specify the wallet in the Elements node URL.

For instance, if elementsd is running locally, with rpc user 'user' and password
'password', and the desired wallet name is 'wallet2', the URL must be set 
to: `http://user:password@localhost:7041/wallet/wallet2`.
