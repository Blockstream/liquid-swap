WALLET_MIN_VERSION = 169900
LIQUID_MIN_VERSION = 170000

NLOCKTIME = 0
IS_REPLACEABLE = True

# Use a p2sh-segwit (current liquid default) confidential dummy address so that
# fundrawtransaction allocates the right fees.
DUMMY_ADDRESS = {
    # regtest: wally.base58check_from_bytes(b'\x4b' + b'\x00'*20),
    False: 'XBMEr9McFXkiLWTVqTyuNQR1CqKkMPMn6L',
    # mainnet: wally.base58check_from_bytes(b'\x27' + b'\x00'*20),
    True: 'GhBXQEdEh35AtuSNxMzRutcgYg3nkvq5Wb',
}
# dummy_pubkey = b'\x02'*33
DUMMY_ADDRESS_CONFIDENTIAL = {
    # regtest: wally.confidential_addr_from_addr(dummy_add, 0x04, dummy_pubkey)
    False: 'Azpj2QQw8ZGASK99L4BVKvH2xW9jerD9QrLenKUML7sQXMqJKJyYSwp99dASLbF5aR'
           'qXifmnTFhVzbZn',
    # mainnet: wally.confidential_addr_from_addr(dummy_add, 0x0c, dummy_pubkey)
    True: 'VJL5bwudesLgrLxF4SPVyxvoWrDJhBpKf9YxQgVpMzfuLDSGndbWS832vZmKoV5KhrC'
          '2RC4SKzvn2ZbE',
}
# FIXME: if the receiver wallet set another addresstype, then this choice may
#        lead to an incorrect fee estimation. In addition, for better anonimity
#        it would be better if all the address types are equal.

PROPOSED_KEYS = ['tx', 'u_address_p', 'map_confidential', 'unspents_details']
ACCEPTED_KEYS = ['tx', 'blinding_keys', 'u_address_p', 'u_address_r']

OWN_PROPOSAL_ERROR_MSG = 'Unable to continue swap. This proposal was created' \
                         ' by the same wallet. The Liquid Swap Tool requires' \
                         ' swaps to be between different wallets.'
