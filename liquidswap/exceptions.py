class LiquidSwapError(Exception):
    """Base class for all tool errors"""
    pass


class SameAssetError(LiquidSwapError):
    """Swap between the same asset are not supported"""


class InvalidAddressError(LiquidSwapError):
    """Found an invalid address"""


class OwnProposalError(LiquidSwapError):
    """Parsing your own proposal"""


class UnexpectedValueError(LiquidSwapError):
    """Found an unexpected value"""


class MissingValueError(LiquidSwapError):
    """An value the tool expects is missing"""


class FeeRateError(LiquidSwapError):
    """Invalid fee rate value"""


class UnblindError(LiquidSwapError):
    """Unable to fully unblind the transaction"""


class UnsignedTransactionError(LiquidSwapError):
    """Transaction is not fully signed"""


class InvalidTransactionError(LiquidSwapError):
    """Transaction won't be accepted by mempool"""


class UnsupportedLiquidVersionError(LiquidSwapError):
    """Liquid version running is below minimum supported"""


class UnsupportedWalletVersionError(LiquidSwapError):
    """Wallet version is below minimum supported"""


class LockedWalletError(LiquidSwapError):
    """Wallet is locked"""


class InvalidAssetIdError(LiquidSwapError):
    """Asset id or already in the wallet"""


class InvalidAssetLabelError(LiquidSwapError):
    """Asset label already set"""
