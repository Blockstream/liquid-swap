import logging

from liquidswap.constants import (
    PROPOSED_KEYS,
    ACCEPTED_KEYS,
    ELEMENTS_MIN_VERSION,
    WALLET_MIN_VERSION,
    OWN_PROPOSAL_ERROR_MSG,
    NETWORK_REGTEST,
    NETWORK_MAINNET,
    NETWORK_NAMES,
)
from liquidswap.exceptions import (
    UnexpectedValueError,
    UnsupportedLiquidVersionError,
    UnsupportedWalletVersionError,
    LockedWalletError,
    InvalidAddressError,
    OwnProposalError,
)


def btc2sat(btc):
    return round(btc * 10**8)


def sat2btc(sat):
    return round(sat * 10**-8, 8)

def values2btc(m, a):
    if a is None:
        return {k: sat2btc(v) for k, v in m.items()}
    else:
        ret = []
        for k, v in m.items():
            dict_addr = {k: sat2btc(v)}
            if k in a:
                dict_addr["asset"] = a[k]
            ret.append(dict_addr)
        return ret

def sort_dict(d):
    return {k: v for k, v in sorted(d.items())}


def get_chain_index(chain):
    if chain == 'liquidv1':
        network = NETWORK_MAINNET
    else:
        network = NETWORK_REGTEST
    return network


def is_mine(address, connection):
    if not connection.validateaddress(address)['isvalid']:
        raise InvalidAddressError('Invalid address: {}'.format(address))
    return connection.getaddressinfo(address)['ismine']


def check_not_mine(address, connection):
    """Raise an OwnProposalError if address is owned by the wallet
    """
    if is_mine(address, connection):
        raise OwnProposalError(OWN_PROPOSAL_ERROR_MSG)


def get_status(proposal):
    """Deduce status of a decoded proposal from keys in the map
    """
    if set(proposal) == set(PROPOSED_KEYS):
        return 'proposed'
    elif set(proposal) == set(ACCEPTED_KEYS):
        return 'accepted'
    else:
        raise UnexpectedValueError('Unexpected proposal {}'.format(proposal))


def check_liquid_version(connection):
    """Raise error if Liquid version is below min supported
    """
    network_info = connection.getnetworkinfo()
    if network_info.get('version', 0) < ELEMENTS_MIN_VERSION:
        msg = 'Unsupported liquid version, must be at least {}'.format(
            ELEMENTS_MIN_VERSION)
        raise UnsupportedLiquidVersionError(msg)


def check_wallet_version(connection):
    """Raise error if wallet version is below min supported
    """
    wallet_info = connection.getwalletinfo()
    if wallet_info.get('walletversion', 0) < WALLET_MIN_VERSION:
        msg = 'Unsupported wallet version, must be at least {}'.format(
            WALLET_MIN_VERSION)
        raise UnsupportedWalletVersionError(msg)


def check_wallet_unlocked(connection):
    """Raise error if wallet is locked
    """
    wallet_info = connection.getwalletinfo()
    if wallet_info.get('unlocked_until', 1) == 0:
        raise LockedWalletError('Wallet locked, please unlock it to proceed')


def check_network(expected_network, connection):
    """Raise error if expected network and node network mismatch
    """
    network = get_chain_index(connection.getblockchaininfo().get('chain'))
    if network != expected_network:
        msg = 'Network mismatch: tool expecting {}, node using {}.'.format(
            NETWORK_NAMES[expected_network], NETWORK_NAMES[network])
        raise UnexpectedValueError(msg)


def do_initial_checks(connection, expected_network):
    """Do initial checks
    """
    check_liquid_version(connection)
    check_wallet_version(connection)
    check_network(expected_network, connection)


def set_logging(verbose):
    """Set logging level
    """

    logging.basicConfig(format='liquidswap %(levelname)s %(message)s')
    if verbose == 1:
        logging.root.setLevel(logging.INFO)
    elif verbose > 1:
        logging.root.setLevel(logging.DEBUG)


def compute_receiver_fee(connection, tx, proposer_fee):
    """Compute transaction fees of an accepted proposal
    """

    outputs = connection.decoderawtransaction(tx)['vout']
    fees = [o['value'] for o in outputs if o['scriptPubKey']['type'] == 'fee']
    if len(fees) != 1:
        raise UnexpectedValueError('Missing fee')
    receiver_fee = btc2sat(fees[0]) - proposer_fee
    if receiver_fee <= 0:
        msg = 'Proposer fee higher than transaction fee ({}, {})'.format(
            proposer_fee, btc2sat(fees[0]))
        raise UnexpectedValueError(msg)
    return receiver_fee
