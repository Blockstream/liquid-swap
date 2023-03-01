import logging
import random
import os

from liquidswap.exceptions import (
    SameAssetError,
    InvalidAddressError,
    OwnProposalError,
    UnexpectedValueError,
    MissingValueError,
    FeeRateError,
    UnblindError,
    UnsignedTransactionError,
    InvalidTransactionError,
)
from liquidswap.constants import (
    NLOCKTIME,
    IS_REPLACEABLE,
    DUMMY_ADDRESS,
    DUMMY_ADDRESS_CONFIDENTIAL,
)
from liquidswap.util import (
    btc2sat,
    sat2btc,
    values2btc,
    is_mine,
    sort_dict,
    get_chain_index,
)


# TODO: investigate cases when an output have more than one address
#       (currently code may behave unexpectedly)


def propose(amount_p, asset_p,
            amount_r, asset_r,
            connection,
            fee_rate=None):
    """Propose a swap

    Proposer (p) sends amount_p of asset_p.
    Receiver (r) is asked to send amount_r of asset_r.
    """

    logging.info('Proposing a swap [1/3]')
    logging.info('Send {} (sat) of asset {}'.format(amount_p, asset_p))
    logging.info('Receive {} (sat) of asset {}'.format(amount_r, asset_r))
    logging.info('Fee rate: {}'.format(fee_rate or 'default'))

    if not all([amount_p, asset_p, amount_r, asset_r]):
        raise MissingValueError('Missing or zero parameter')

    if asset_p == asset_r:
        raise SameAssetError('Swaps between the same asset are currently not '
                             'supported.')

    network = get_chain_index(connection.getblockchaininfo().get('chain'))

    c_address_p = connection.getnewaddress()
    u_address_p = connection.getaddressinfo(c_address_p)['unconfidential']
    elements_version = connection.getnetworkinfo()['version']

    if elements_version < 210000:
        txu = connection.createrawtransaction(
            [],
            {DUMMY_ADDRESS_CONFIDENTIAL[network]: sat2btc(amount_p)},
            NLOCKTIME,
            IS_REPLACEABLE,
            {DUMMY_ADDRESS_CONFIDENTIAL[network]: asset_p}
        )
    else:
        txu = connection.createrawtransaction(
            [],
            [{DUMMY_ADDRESS_CONFIDENTIAL[network]: sat2btc(amount_p), 'asset': asset_p}],
            NLOCKTIME,
            IS_REPLACEABLE
        )

    # FIXME: consider locking unspents.
    details = {
        # 'lockUnspents': False,
    }
    if fee_rate is not None:
        details.update({'feeRate': fee_rate})

    logging.debug('Selecting inputs to fund swap transaction (proposer)')
    txf = connection.fundrawtransaction(
        txu,
        details
    )['hex']

    inputs = connection.decoderawtransaction(txf)['vin']
    outputs = connection.decoderawtransaction(txf)['vout']

    # collect details (keys) for each input
    keys = ['txid', 'vout', 'amount', 'asset', 'amountblinder', 'assetblinder']
    unspents = connection.listunspent()
    unspents_details = list()
    for input_ in inputs:
        for unspent in unspents:
            if (input_['txid'] == unspent['txid'] and
                input_['vout'] == unspent['vout']):
                unspent['amount'] = btc2sat(unspent.pop('amount'))
                unspents_details.append({k: unspent[k] for k in keys})

    if len(inputs) != len(unspents_details):
        raise MissingValueError('Unable to collect unspent details')

    # construct maps for amount and asset to feed (again) createrawtransaction
    map_amount = dict()
    map_asset = dict()

    # map unconfidential addresses to confidential addresses
    map_confidential = dict()

    for output in outputs:
        u_address = None
        if 'addresses' in output['scriptPubKey']:
            u_address = output['scriptPubKey']['addresses'][0]
        elif 'address' in output['scriptPubKey']:
            u_address = output['scriptPubKey']['address']

        if u_address is not None:
            if u_address == DUMMY_ADDRESS[network]:
                key = u_address
            else:
                c_address = connection.getaddressinfo(
                    u_address)['confidential']
                map_confidential.update({u_address: c_address})
                key = c_address

            map_amount.update({key: btc2sat(output['value'])})
            map_asset.update({key: output['asset']})

        elif output['scriptPubKey']['type'] == 'fee':
            map_amount.update({'fee': btc2sat(output['value'])})

    # add asset and amount to receive
    map_amount.update({c_address_p: amount_r})
    map_asset.update({c_address_p: asset_r})
    map_confidential.update({u_address_p: c_address_p})

    if elements_version < 210000:
        tx = connection.createrawtransaction(
            inputs,
            values2btc(map_amount, None),
            NLOCKTIME,
            IS_REPLACEABLE,
            map_asset
        )
    else:
        tx = connection.createrawtransaction(
            inputs,
            values2btc(map_amount, map_asset),
            NLOCKTIME,
            IS_REPLACEABLE
        )

    logging.debug('Proposer address: {}'.format(u_address_p))
    logging.debug('Address map: {}'.format(map_confidential))
    logging.debug('Unspents_details: {}'.format(unspents_details))
    return {
        'tx': tx,
        'u_address_p': u_address_p,
        'map_confidential': map_confidential,
        'unspents_details': unspents_details,
    }


def parse_proposed(tx,
                   u_address_p,
                   map_confidential,
                   unspents_details,
                   connection):
    """Parse a proposed swap

    Receiver checks correctness of proposal and deduce its details.
    """

    logging.info('Parsing swap proposal')
    logging.debug('Proposer address: {}'.format(u_address_p))
    logging.debug('Address map: {}'.format(map_confidential))
    logging.debug('Unspents_details: {}'.format(unspents_details))

    network = get_chain_index(connection.getblockchaininfo().get('chain'))

    is_proposer = is_mine(u_address_p, connection)
    if is_proposer:
        logging.info('Parsing own proposal')

    dtx = connection.decoderawtransaction(tx)
    logging.debug('Decoded proposer transaction: {}'.format(dtx))
    outputs = dtx['vout']

    # Deduce details of the swap (amount_p,r, asset_p,r) from the tx
    # Construct maps to feed createrawtransaction

    amount_p = amount_r = fee_p = 0
    asset_p = asset_r = ''

    map_amount_p = dict()
    map_asset_p = dict()

    for output in outputs:
        u_address = None
        if 'addresses' in output['scriptPubKey']:
            u_address = output['scriptPubKey']['addresses'][0]
        elif 'address' in output['scriptPubKey']:
            u_address = output['scriptPubKey']['address']

        if u_address is not None:
            if u_address == DUMMY_ADDRESS[network]:
                if asset_p:
                    raise UnexpectedValueError('Found more than one dummy '
                                               'address')
                amount_p = btc2sat(output['value'])
                asset_p = output['asset']
                logging.debug('Proposer: amount {} (sat), asset {}'.format(
                    amount_p, asset_p))

                # dummy address will be replaced, do not include it in the maps
                continue

            elif u_address == u_address_p:
                if asset_r:
                    raise UnexpectedValueError('Found more than one proposer '
                                               'address')
                amount_r = btc2sat(output['value'])
                asset_r = output['asset']
                logging.debug('Receiver: amount {} (sat), asset {}'.format(
                    amount_r, asset_r))

            c_address = map_confidential.get(u_address, '')
            if not c_address:
                raise MissingValueError('Missing address in map_confidential')

            if not connection.validateaddress(c_address)['isvalid']:
                raise InvalidAddressError('Invalid address: {}'.format(
                    c_address))

            if u_address != connection.getaddressinfo(
                c_address)['unconfidential']:
                msg = 'Unmatching confidential-unconfidential address: {}, ' \
                      '{}'.format(c_address, u_address)
                raise UnexpectedValueError(msg)

            map_amount_p.update({c_address: btc2sat(output['value'])})
            map_asset_p.update({c_address: output['asset']})

        elif output['scriptPubKey']['type'] == 'fee':
            fee_p = btc2sat(output['value'])
            logging.debug('Proposer: fee {} (sat)'.format(fee_p))

    if amount_p == 0 or asset_p == '':
        raise MissingValueError('Missing dummy address')
    elif amount_r == 0 or asset_r == '':
        raise MissingValueError('Missing proposer address in the transaction')
    elif fee_p == 0:
        raise MissingValueError('Missing fee')

    c_address_p = map_confidential[u_address_p]

    logging.debug('Proposer map amount: {}'.format(map_amount_p))
    logging.debug('Proposer map asset: {}'.format(map_asset_p))

    return (tx,
            c_address_p, amount_p, asset_p, fee_p,
            amount_r, asset_r, map_amount_p, map_asset_p,
            unspents_details)


def accept(tx_p,
           c_address_p, amount_p, asset_p, fee_p,
           amount_r, asset_r,
           map_amount_p, map_asset_p, unspents_details_p,
           connection,
           fee_rate=None):
    """Accept a (parsed) swap proposal

    Fund, blind and sign the transaction. Should be used with outputs from
    parse_proposed.
    """

    logging.info('Accepting swap proposal [2/3]')

    c_address_r = connection.getnewaddress()
    u_address_r = connection.validateaddress(c_address_r)['unconfidential']
    u_address_p = connection.validateaddress(c_address_p)['unconfidential']
    elements_version = connection.getnetworkinfo()['version']
    logging.debug('Receiver address: {}'.format(u_address_r))
    logging.debug('Proposer address: {}'.format(u_address_p))

    if elements_version < 210000:
        txu = connection.createrawtransaction(
            [],
            {c_address_p: sat2btc(amount_r)},
            NLOCKTIME,
            IS_REPLACEABLE,
            {c_address_p: asset_r}
        )
    else:
        txu = connection.createrawtransaction(
            [],
            [{c_address_p: sat2btc(amount_r), 'asset': asset_r}],
            NLOCKTIME,
            IS_REPLACEABLE
        )

    details = {
        # 'lockUnspents': False,
    }
    if fee_rate is not None:
        details.update({'feeRate': fee_rate})

    logging.debug('Selecting inputs to fund swap transaction (receiver)')
    tx_r = connection.fundrawtransaction(
        txu,
        details,
    )['hex']
    inputs_r = connection.decoderawtransaction(tx_r)['vin']
    outputs_r = connection.decoderawtransaction(tx_r)['vout']

    # collect details (keys) for each input
    keys = ['txid', 'vout', 'amount', 'asset', 'amountblinder', 'assetblinder']
    unspents_r = connection.listunspent()
    unspents_details_r = list()
    for input_ in inputs_r:
        for unspent in unspents_r:
            if (input_['txid'] == unspent['txid'] and
                input_['vout'] == unspent['vout']):
                unspent['amount'] = btc2sat(unspent.pop('amount'))
                unspents_details_r.append({k: unspent[k] for k in keys})

    unspents_details = unspents_details_p + unspents_details_r

    # deduce fees and maps for outputs and amounts from tx_r
    map_amount_r = dict()
    map_asset_r = dict()

    for output in outputs_r:
        u_address = None
        if 'addresses' in output['scriptPubKey']:
            u_address = output['scriptPubKey']['addresses'][0]
        elif 'address' in output['scriptPubKey']:
            u_address = output['scriptPubKey']['address']

        if u_address is not None:
            if u_address == u_address_p:
                c_address = c_address_p
            else:
                c_address = connection.getaddressinfo(
                    u_address)['confidential']

            map_amount_r.update({c_address: btc2sat(output['value'])})
            map_asset_r.update({c_address: output['asset']})

        elif output['scriptPubKey']['type'] == 'fee':
            # map_amount_r is updated later with the cumulative fee
            fee_r = btc2sat(output['value'])

    # proposer maps do not include the dummy address
    map_amount_p.update({c_address_r: amount_p})
    map_asset_p.update({c_address_r: asset_p})

    # join inputs and outputs from p and r
    inputs_p = connection.decoderawtransaction(tx_p)['vin']

    inputs = inputs_p + inputs_r
    random.seed(os.urandom(32))
    random.shuffle(inputs)

    map_amount = dict()
    map_asset = dict()

    map_amount.update(map_amount_p)
    map_amount.update(map_amount_r)
    map_amount.update({'fee': fee_p + fee_r})

    map_asset.update(map_asset_p)
    map_asset.update(map_asset_r)

    logging.debug('Creating swap transaction')
    # createrawtransaction with the inputs from the 2 transactions
    if elements_version < 210000:
        tx = connection.createrawtransaction(
            inputs,
            sort_dict(values2btc(map_amount, None)),
            NLOCKTIME,
            IS_REPLACEABLE,
            sort_dict(map_asset)
        )
    else:
        tx = connection.createrawtransaction(
            inputs,
            values2btc(sort_dict(map_amount), map_asset),
            NLOCKTIME,
            IS_REPLACEABLE
        )

    # inputs may be reordered by createrawtransaction
    inputs = connection.decoderawtransaction(tx)['vin']

    # pack blinders, assetblinders, assets and amounts
    amountblinders = list()
    assetblinders = list()
    assets = list()
    amounts = list()

    for input_ in inputs:
        for unspent_details in unspents_details:
            if (input_['txid'] == unspent_details['txid'] and
                input_['vout'] == unspent_details['vout']):
                amountblinders.append(unspent_details['amountblinder'])
                assetblinders.append(unspent_details['assetblinder'])
                assets.append(unspent_details['asset'])
                amounts.append(unspent_details['amount'])

    if len(inputs) != len(amounts):
        raise MissingValueError('Missing data in unspent details')

    logging.debug('Blinding swap transaction')
    # blind transaction
    btx = connection.rawblindrawtransaction(
        tx,
        amountblinders,
        [sat2btc(v) for v in amounts],
        assets,
        assetblinders
    )

    logging.debug('Signing swap transaction (receiver inputs)')
    # sign transaction
    stx = connection.signrawtransactionwithwallet(btx)['hex']

    logging.debug('Dumping blinding keys (so that the swap partner can fully '
                  'unblind the transaction)')
    # dump bliding private keys
    blinding_keys = dict()
    for c_address in map_amount:
        if (c_address != 'fee' and
            connection.getaddressinfo(c_address)['ismine']):
            blinding_key = connection.dumpblindingkey(c_address)
            blinding_keys.update({c_address: blinding_key})

    min_relay_fee = connection.getnetworkinfo()['relayfee']
    dtx = connection.decoderawtransaction(stx)
    # TODO: estimate impact of missing signatures
    estimated_vsize_vb = dtx['vsize']
    estimated_fee_rate = (fee_p + fee_r) * 10**-5 / estimated_vsize_vb

    if estimated_fee_rate < min_relay_fee:
        msg = 'Fee rate too low: please specify an higher fee rate or reject' \
              ' the proposal ({:.8f}, min: {})'.format(estimated_fee_rate,
                                                       min_relay_fee)
        raise FeeRateError(msg)

    logging.debug('Blinding keys: {}'.format(blinding_keys))
    return {
        'tx': stx,
        'blinding_keys': blinding_keys,
        'u_address_p': u_address_p,
        'u_address_r': u_address_r,
    }


def parse_accepted(signed_tx,
                   blinding_keys,
                   u_address_p,
                   u_address_r,
                   connection):
    """Parse an accepted swap proposal

    Proposer checks correctness of the accepted proposal and deduce its
    details.
    """

    logging.info('Parsing accepted swap proposal')
    logging.debug('Blinding keys: {}'.format(blinding_keys))
    logging.debug('Proposer address: {}'.format(u_address_p))
    logging.debug('Receiver address: {}'.format(u_address_r))

    # There should be a way for the proposer to recognize his proposal, e.g.
    # proposer sends his proposal signed, receiver includes it in what he sends
    # back, proposer verify that signed tx actually includes what he proposed

    is_proposer = is_mine(u_address_p, connection)
    is_receiver = is_mine(u_address_r, connection)

    if is_receiver:
        # FIXME: once this will be implemented, the case where the node owns
        # both addresses must be handled
        raise OwnProposalError('Parsing an own accepted proposal is not '
                               'implemented yet.')
    elif not is_proposer:
        raise UnexpectedValueError('Unable to proceed: both proposer and '
                                   'receiver addresses ({}, {}) are not owned '
                                   'by the wallet'.format(u_address_p,
                                                          u_address_r))

    amount_p = amount_r = 0
    asset_p = asset_r = ''

    logging.debug('Importing blinding keys')
    # import blinding keys to fully unblind the transaction
    for c_address, blinding_key in blinding_keys.items():
        connection.importblindingkey(c_address, blinding_key)

    logging.debug('Unblinding transaction to analyze it')
    unblinded_tx = connection.unblindrawtransaction(signed_tx)['hex']
    decoded_tx = connection.decoderawtransaction(unblinded_tx)
    logging.debug('Decoded unblinded transaction: {}'.format(decoded_tx))

    if decoded_tx['locktime'] != NLOCKTIME:
        msg = 'Unexpected nLocktime value: expected {}, found {}'.format(
            decoded_tx['nlocktime'], NLOCKTIME)
        raise UnexpectedValueError(msg)

    # TODO: the same thing should happen for IS_REPLACEABLE

    # deduce tx inputs owned by receiver
    receiver_unspents = connection.listunspent()
    amounts_in = dict()
    for input_ in decoded_tx['vin']:
        for unspent in receiver_unspents:
            if (input_['txid'] == unspent['txid'] and
                input_['vout'] == unspent['vout']):
                asset = unspent['asset']
                amount = btc2sat(unspent['amount'])

                amounts_in.update({asset: amounts_in.get(asset, 0) + amount})
                break

    # deduce tx outputs owned by receiver
    amounts_out = dict()
    for output in decoded_tx['vout']:
        if 'value' not in output:
            raise UnblindError('Transaction is not fully unblinded')

        u_address = None
        if 'addresses' in output['scriptPubKey']:
            u_address = output['scriptPubKey']['addresses'][0]
        elif 'address' in output['scriptPubKey']:
            u_address = output['scriptPubKey']['address']

        if u_address is not None:
            amount = btc2sat(output['value'])
            asset = output['asset']

            if u_address == u_address_r:
                if asset_p:
                    raise UnexpectedValueError('Found more than one receiver '
                                               'address')
                amount_p = amount
                asset_p = asset
            elif u_address == u_address_p:
                if asset_r:
                    raise UnexpectedValueError('Found more than one proposer '
                                               'address')
                amount_r = amount
                asset_r = asset

            if connection.getaddressinfo(u_address)['ismine']:
                amounts_out.update({asset: amounts_out.get(asset, 0) + amount})

        elif output['scriptPubKey']['type'] == 'fee':
            asset_fee = output['asset']
            fee_tot = btc2sat(output['value'])

    if amount_p == 0 or asset_p == '':
        raise ValueError('Missing receiver address in transaction')
    if amount_r == 0 or asset_r == '':
        raise ValueError('Missing proposer address in transaction')

    tx_balance = {k: amounts_out.get(k, 0) - amounts_in.get(k, 0) for k in
                  set(list(amounts_in) + list(amounts_out))}

    expected_keys = set([asset_r, asset_p, asset_fee])
    if expected_keys != set(tx_balance):
        msg = 'Unexpected keys in transaction balance: found {}, expected {}' \
              ', balance'.format(tx_balance.keys(), expected_keys, tx_balance)
        raise UnexpectedValueError(msg)

    if asset_fee not in (asset_p, asset_r):
        fee_p = -tx_balance[asset_fee]
        fee_r = fee_tot - fee_p

    # in case one of the asset is the same as the fee, deduce fees from the
    # (unsafe) amount given to the function, if fees are acceptable, the amount
    # is assumed to be acceptable too
    if asset_fee == asset_p:
        fee_p = -tx_balance[asset_p] - amount_p
        fee_r = fee_tot - fee_p

    if asset_fee == asset_r:
        fee_p = amount_r - tx_balance[asset_r]
        fee_r = fee_tot - fee_p

    if fee_tot <= 0 or fee_p <= 0 or fee_r <= 0:
        raise UnexpectedValueError(
            'Unexpected fees: tot {}, proposer {}, ''receiver {}'.format(
                fee_tot, fee_p, fee_r))

    if asset_fee != asset_p and -tx_balance[asset_p] != amount_p:
        raise UnexpectedValueError(
            'Unexpected amount sent by proposer: found {}, expected {}'.format(
                -tx_balance[asset_p], amount_p))

    if asset_fee != asset_r and tx_balance[asset_r] != amount_r:
        raise UnexpectedValueError(
            'Unexpected amount sent by receiver: found {}, expected {}'.format(
                tx_balance[asset_r], amount_r))

    logging.debug('Proposer: amount {} (sat), asset {}, fee {} (sat)'.format(
        amount_p, asset_p, fee_p))
    logging.debug('Receiver: amount {} (sat), asset {}, fee {} (sat)'.format(
        amount_r, asset_r, fee_r))
    return (signed_tx,
            amount_p, asset_p, fee_p,
            amount_r, asset_r, fee_r)


def finalize(pstx, connection, broadcast=False):
    """Sign and send an accepted proposal

    Should be used only after parse_accepted.
    """

    logging.info('Finalizing swap [3/3]')
    logging.debug('Signing swap transaction (proposer inputs)')
    # sign the remaining inputs
    ret = connection.signrawtransactionwithwallet(pstx)

    if not ret['complete']:
        raise UnsignedTransactionError('Transaction has some unsigned inputs')

    tx = ret['hex']
    if broadcast:
        logging.info('Broadcasting transaction')
        return connection.sendrawtransaction(tx)
    else:
        logging.info('Testing transaction against mempool')
        if not connection.testmempoolaccept([tx])[0]['allowed']:
            raise InvalidTransactionError('Invalid transaction: will not be '
                                          'allowed by mempool')

        return tx
