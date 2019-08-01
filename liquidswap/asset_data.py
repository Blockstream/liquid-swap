from liquidswap.exceptions import (
    InvalidAssetIdError,
    InvalidAssetLabelError,
)


class AssetsData(object):
    """Structure to handle asset data"""

    def __init__(self):
        self.labels = dict()
        self.balances = dict()
        # keys are expected to be always the same

        # labels not coming from elements-cli, they are intended only for
        # receiving purposes and have no balance
        self.temp_labels = dict()

    def update(self, connection):
        """Update all assets label and balance"""

        updated_balances = connection.getbalance()
        updated_labels = connection.dumpassetlabels()

        # Update labels
        for label, asset_id in updated_labels.items():
            if label == 'bitcoin':
                label = 'L-BTC'
            self.labels.update({asset_id: label})
            # add zero balance if missing
            # FIXME: consider using collection.ChainMap
            self.balances.setdefault(asset_id, 0)

        # Update balances, need to access labels
        for k, balance in updated_balances.items():
            # key can be an asset_id with no label, a label in updated labels
            # or a newly received asset_id
            asset_id = k if k in self.labels else updated_labels.get(k, k)

            self.balances.update({asset_id: balance})
            # label is asset_id if missing
            self.labels.setdefault(asset_id, asset_id)

    def add_temp_label(self, asset_id, label='', allow_update=True):
        """Add a temporary asset id"""

        if not is_valid_asset_id(asset_id):
            raise InvalidAssetIdError('Invalid asset id: {}'.format(asset_id))

        if asset_id in self.labels:
            # FIXME: change this message once it's possible to edit labels from
            #        elements-cli
            msg = 'Asset already in the wallet, modify its label editing the' \
                   'elements.conf'
            raise InvalidAssetIdError(msg)

        if not allow_update and asset_id in self.temp_labels:
            msg = 'Asset label already set: {}'.format(
                self.temp_labels[asset_id])
            raise InvalidAssetLabelError(msg)

        self.temp_labels.update({asset_id: label if label else asset_id})

    def get_label(self, asset_id):
        return {**self.labels, **self.temp_labels}.get(asset_id, asset_id)

    def get_balance(self, asset_id):
        return self.balances.get(asset_id, 0)


def is_valid_asset_id(asset_id):
    return (
        isinstance(asset_id, str) and
        len(asset_id) == 64 and
        all(c in '0123456789abcdef' for c in asset_id)
    )
