import click
import json
import logging
import sys
from collections import namedtuple

from liquidswap import swap
from liquidswap.encode import encode_payload, decode_payload
from liquidswap.connect import ConnCtx, DEFAULT_REGTEST_RPC_PORT
from liquidswap.constants import PROPOSED_KEYS, ACCEPTED_KEYS, NETWORK_REGTEST, NETWORK_MAINNET
from liquidswap.util import (
    set_logging,
    do_initial_checks,
    get_status,
    check_wallet_unlocked,
    btc2sat,
    sat2btc,
    is_mine,
    check_not_mine,
)


def critical(title='', message='', start_over=True):
    """Function to prompt critical error message

    Its interface matches requirements from ConnCtx
    """
    logging.error(message)
    if start_over:
        sys.exit(1)


ConnParams = namedtuple('ConnParams', ['credentials', 'network'])


@click.group()
@click.option('-u', '--service-url', default=None, type=str,
              help='Specify Elements node URL for authentication.')
@click.option('-c', '--conf-file', default=None, type=str,
              help='Specify elements.conf file for authentication.')
@click.option('-r', '--regtest', is_flag=True, help='Use with regtest.')
@click.option('-v', '--verbose', count=True,
              help='Print more information, may be used multiple times.')
@click.version_option()
@click.pass_context
def cli(ctx, service_url, conf_file, regtest, verbose):
    """Liquid Swap Tool Command-Line Interface
    """

    set_logging(verbose)

    network = NETWORK_MAINNET if not regtest else NETWORK_REGTEST
    credentials = {
        'elements_conf_file': conf_file,
        'service_url': service_url,
        'service_port': (None if network == NETWORK_MAINNET else DEFAULT_REGTEST_RPC_PORT),
    }

    ctx.obj = ConnParams(credentials, network)


@cli.command(short_help='Show proposal in human readable format')
@click.argument('payload', type=click.File('r'))
@click.pass_obj
def info(obj, payload):
    """Show proposal in human readable format

    Proposal could be either in two status: proposed or accepted.
    """

    with ConnCtx(obj.credentials, critical) as cc:
        connection = cc.connection
        do_initial_checks(connection, obj.network)

        proposal = decode_payload(payload.read())
        status = get_status(proposal)

        if status == 'proposed':
            (tx, address_p, amount_p, asset_p, fee_p, amount_r, asset_r,
             map_amount, map_asset, unspents_details) = swap.parse_proposed(
                *[proposal[k] for k in PROPOSED_KEYS],
                connection)
            is_proposer = is_mine(address_p, connection)
            proposer_leg_is_funded, receiver_leg_is_funded = True, False
            fee_r = 0

        elif status == 'accepted':
            (signed_tx, amount_p, asset_p, fee_p, amount_r, asset_r,
             fee_r) = swap.parse_accepted(
                *[proposal[k] for k in ACCEPTED_KEYS],
                connection)
            is_proposer = is_mine(proposal['u_address_p'], connection)
            proposer_leg_is_funded, receiver_leg_is_funded = True, True

        d = {
            'status': status,
            'legs': [
                {
                    'incoming': not is_proposer,
                    'funded': proposer_leg_is_funded,
                    'asset': asset_p,
                    'amount': sat2btc(amount_p),
                    'fee': sat2btc(fee_p),
                },
                {
                    'incoming': is_proposer,
                    'funded': receiver_leg_is_funded,
                    'asset': asset_r,
                    'amount': sat2btc(amount_r),
                    'fee': sat2btc(fee_r),
                },
            ]
        }
        click.echo(json.dumps(d, indent=4))


@cli.command(short_help='Propose a swap')
@click.argument('asset_p', type=str)
@click.argument('amount_p', type=float)
@click.argument('asset_r', type=str)
@click.argument('amount_r', type=float)
@click.option('-o', '--output', type=click.File('w'))
@click.option('-f', '--fee-rate', type=float, default=None,
              help='Fee rate in BTC/Kb, if not set, it will be determined by '
                   'the wallet.')
@click.pass_obj
def propose(obj, asset_p, amount_p, asset_r, amount_r, output, fee_rate):
    """Propose a swap

    A swap consists in sending AMOUNT_P of ASSET_P and receiving AMOUNT_R of
    ASSET_R.
    """

    with ConnCtx(obj.credentials, critical) as cc:
        connection = cc.connection
        do_initial_checks(connection, obj.network)

        proposal = swap.propose(btc2sat(amount_p), asset_p,
                                btc2sat(amount_r), asset_r,
                                connection, fee_rate)
        encoded_payload = encode_payload(proposal)
        click.echo(encoded_payload, file=output)


@cli.command(short_help='Accept a swap')
@click.argument('payload', type=click.File('r'))
@click.option('-o', '--output', type=click.File('w'))
@click.option('-f', '--fee-rate', type=float, default=None,
              help='Fee rate in BTC/Kb, if not set, it will be determined by '
                   'the wallet.')
@click.pass_obj
def accept(obj, payload, output, fee_rate):
    """Accept a swap

    Fund and (partially) sign a proposed transaction.
    """

    with ConnCtx(obj.credentials, critical) as cc:
        connection = cc.connection
        do_initial_checks(connection, obj.network)
        proposal = decode_payload(payload.read())

        check_wallet_unlocked(connection)
        check_not_mine(proposal['u_address_p'], connection)

        ret = swap.parse_proposed(
            *[proposal[k] for k in PROPOSED_KEYS],
            connection)
        accepted_swap = swap.accept(*ret, connection, fee_rate)
        encoded_payload = encode_payload(accepted_swap)
        click.echo(encoded_payload, file=output)


@cli.command(short_help='Finalize a swap')
@click.argument('payload', type=click.File('r'))
@click.option('--send', '-s', is_flag=True, help="Send the transaction.")
@click.pass_obj
def finalize(obj, payload, send):
    """Finalize a swap

    Sign the remaining inputs, print the transaction or broadcast it.
    """

    with ConnCtx(obj.credentials, critical) as cc:
        connection = cc.connection
        do_initial_checks(connection, obj.network)
        proposal = decode_payload(payload.read())
        check_wallet_unlocked(connection)
        check_not_mine(proposal['u_address_r'], connection)

        (incomplete_tx, _, _, _, _, _, _) = swap.parse_accepted(
            *[proposal[k] for k in ACCEPTED_KEYS],
            connection)

        ret = swap.finalize(incomplete_tx, connection, broadcast=send)

        if send:
            d = {'broadcast': True, 'txid': ret}
        else:
            d = {'broadcast': False, 'transaction': ret}

        click.echo(json.dumps(d, indent=4))
