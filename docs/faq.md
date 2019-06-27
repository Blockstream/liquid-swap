# Frequently Asked Questions

### How should I solve an 'Unsupported wallet version' error?
If you created a wallet with Liquid 0.14, your wallet version is unsupported by the Swap Tool.
To solve the problem you can:
1. Restart liquidd (0.17) with the flag `-upgradewallet`, or
2. Create a new wallet (`liquid-cli createwallet`) and send funds to it from your existing wallet.

If possible, the second solution should be preferred as it is safer.
