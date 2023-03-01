import argparse
import os
import sys

from PyQt5.QtWidgets import (
    QMessageBox,
    QApplication,
    QMainWindow,
    QFileDialog,
    QDialog
)
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp, Qt

from liquidswap import swap
from liquidswap.encode import encode_payload, decode_payload
from liquidswap.asset_data import AssetsData
from liquidswap.connect import ConnCtx, DEFAULT_REGTEST_RPC_PORT
from liquidswap.constants import PROPOSED_KEYS, ACCEPTED_KEYS
from liquidswap.constants import PROPOSED_KEYS, ACCEPTED_KEYS, NETWORK_REGTEST, NETWORK_MAINNET
from liquidswap.exceptions import LiquidSwapError
from liquidswap import __version__
from liquidswap.util import (
    btc2sat,
    sat2btc,
    get_status,
    do_initial_checks,
    check_wallet_unlocked,
    compute_receiver_fee,
    set_logging,
    check_not_mine,
)

from liquidswap.gui.qt.dialogaddnewasset import Ui_AddNewAssetDialog
from liquidswap.gui.qt.dialogcopy import Ui_CopyDialog
from liquidswap.gui.qt.dialogpaste import Ui_PasteDialog
from liquidswap.gui.qt.dialogurl import Ui_URLDialog
from liquidswap.gui.qt.windowaccept import Ui_AcceptWindow
from liquidswap.gui.qt.windowfinalize import Ui_FinalizeWindow
from liquidswap.gui.qt.windowpropose import Ui_ProposeWindow
from liquidswap.gui.qt.windowstart import Ui_StartWindow


def f2s(f):
    return '{:.8f}'.format(f)


def set_re_float(line_edit):
    line_edit.setValidator(QRegExpValidator(QRegExp('^\d*\.?\d+$'), line_edit))
# TODO: add regex also for asset id


def set_balance_label(asset_data, combo_box, label):
    asset_id = combo_box.currentData()
    if asset_id:
        label.setText('/ {:.8f}'.format(asset_data.get_balance(asset_id)))
    else:
        label.setText('')


def set_url_tip(service_url, action):
    if service_url:
        action.setStatusTip('Elements Node URL: {}'.format(service_url))


def set_conf_tip(elements_conf_file, action):
    if elements_conf_file:
        action.setStatusTip('elements.conf: {}'.format(elements_conf_file))


def setup_toolbar(parent, window):
    set_url_tip(parent.credentials['service_url'], window.actionURL)
    set_conf_tip(parent.credentials['elements_conf_file'], window.actionConf)

    window.actionNew.triggered.connect(
        lambda: InitialWindow(parent=parent))

    window.actionExit.triggered.connect(
        lambda: parent.close())

    window.actionConf.triggered.connect(
        lambda: parent.change_conf_file(window.actionConf))

    window.actionURL.triggered.connect(
        lambda: parent.change_service_url(window.actionURL))

    link = 'https://github.com/Blockstream/liquid-swap/'
    help_msg = 'Version: {}<br><br>For additional details, see our ' \
               '<a href="{}">GitHub page</a>.'.format(__version__, link)
    window.actionAbout.triggered.connect(
        lambda: QMessageBox.information(parent, 'Help', help_msg))


def copy_to_clipboard(text):
    # TODO: test in different os
    cb = QApplication.clipboard()
    cb.clear(mode=cb.Clipboard)
    cb.setText(text, mode=cb.Clipboard)


class AddNewAssetDialog(QDialog, Ui_AddNewAssetDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)


class CopyDialog(QDialog, Ui_CopyDialog):
    def __init__(self, parent=None, text='', title='', suggested_name=''):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        if title:
            self.setWindowTitle(title)

        self.textBrowser.setText(text)

        self.buttonExport.clicked.connect(
            lambda: self.export(text, suggested_name))

        self.buttonCopy.clicked.connect(
            lambda: copy_to_clipboard(text))

        self.buttonOk.clicked.connect(
            lambda: self.done(1))

        self.buttonCancel.clicked.connect(
            lambda: self.done(0))

    def export(self, text, suggested_name):
        filename, _ = QFileDialog.getSaveFileName(self, 'Choose file',
                                                  suggested_name)
        if filename:
            with open(filename, 'w') as fw:
                fw.write(text)
                self.done(1)


class PasteDialog(QDialog, Ui_PasteDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.buttonImport.clicked.connect(
            lambda: self.import_())

        self.buttonOk.clicked.connect(
            lambda: self.done(1))

        self.buttonCancel.clicked.connect(
            lambda: self.done(0))

    def import_(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Choose file')
        if filename:
            with open(filename, 'r') as fr:
                text = fr.read()
                self.textBrowser.setText(text)
                self.done(1)


class URLDialog(QDialog, Ui_URLDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.lineEditURL.setText(parent.credentials['service_url'])


class ProposeWindow(QMainWindow, Ui_ProposeWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(parent)

        setup_toolbar(parent, self)

        with ConnCtx(parent.credentials, parent.critical, True) as cc:
            parent.asset_data.update(cc.connection)

        self.buttonReceiveAddNew.clicked.connect(
            lambda: parent.add_new_asset(
                self.comboBoxReceiveAsset))
        self.buttonGenerateProposal.clicked.connect(
            lambda: self.generate_proposal(parent))

        # combo boxes
        self.comboBoxSendAsset.addItem('')
        for asset_id, label in parent.asset_data.labels.items():
            self.comboBoxSendAsset.addItem(label, asset_id)

        # available balance is shown in the status tip
        self.comboBoxSendAsset.currentTextChanged.connect(
            lambda: set_balance_label(
                parent.asset_data,
                self.comboBoxSendAsset,
                self.labelSendAvailable))

        self.comboBoxReceiveAsset.addItem('')
        for asset_id, label in parent.asset_data.labels.items():
            self.comboBoxReceiveAsset.addItem(label, asset_id)
        for asset_id, label in parent.asset_data.temp_labels.items():
            self.comboBoxReceiveAsset.addItem(label, asset_id)

        set_re_float(self.lineEditSendAmount)
        set_re_float(self.lineEditReceiveAmount)

    def generate_proposal(self, parent):
        asset_p = self.comboBoxSendAsset.currentData()
        amount_p = btc2sat(float(self.lineEditSendAmount.text() or 0))
        asset_r = self.comboBoxReceiveAsset.currentData()
        amount_r = btc2sat(float(self.lineEditReceiveAmount.text() or 0))

        with ConnCtx(parent.credentials, parent.critical) as cc:
            connection = cc.connection
            fee_rate = float(connection.getnetworkinfo()['relayfee'])

            proposal = swap.propose(amount_p=amount_p, asset_p=asset_p,
                                    amount_r=amount_r, asset_r=asset_r,
                                    connection=connection,
                                    fee_rate=fee_rate)

            encoded_payload = encode_payload(proposal)
            parent.copy_dialog(text=encoded_payload,
                               suggested_name='proposal.txt')


class AcceptWindow(QMainWindow, Ui_AcceptWindow):
    def __init__(self, parent, proposal):
        QMainWindow.__init__(self, parent)
        self.setupUi(parent)

        setup_toolbar(parent, self)

        self.buttonAccept.clicked.connect(
            lambda: self.accept(parent, proposal))

        with ConnCtx(parent.credentials, parent.critical, True) as cc:
            connection = cc.connection
            parent.asset_data.update(connection)
            check_not_mine(proposal['u_address_p'], connection)

            (tx, address_p, amount_p, asset_p, fee_p, amount_r, asset_r,
             map_amount, map_asset, unspents_details) = swap.parse_proposed(
                *[proposal[k] for k in PROPOSED_KEYS],
                connection=connection)

            self.labelProposerAmountValue.setText(f2s(sat2btc(amount_p)))
            self.labelProposerAssetValue.setText(
                parent.asset_data.get_label(asset_p))
            self.labelReceiverAmountValue.setText(f2s(sat2btc(amount_r)))
            self.labelReceiverAssetValue.setText(
                parent.asset_data.get_label(asset_r))

    def accept(self, parent, proposal):
        with ConnCtx(parent.credentials, parent.critical) as cc:
            connection = cc.connection
            check_wallet_unlocked(connection)
            check_not_mine(proposal['u_address_p'], connection)

            ret = swap.parse_proposed(
                *[proposal[k] for k in PROPOSED_KEYS],
                connection=connection)

            fee_rate = float(connection.getnetworkinfo()['relayfee'])
            accepted_swap = swap.accept(*ret, connection, fee_rate)
            encoded_payload = encode_payload(accepted_swap)

            tx = accepted_swap['tx']
            fee_p = ret[4]
            fee_r = compute_receiver_fee(connection, tx, fee_p)
            msg = 'Are you sure you want to accept this swap?\n\n' \
                  'Paying fees {:.8f} L-BTC.\n\nReceiving address: {}.'.format(
                    sat2btc(fee_r), accepted_swap['u_address_r'])
            ans = QMessageBox.question(parent, 'Confirm', msg)
            if ans == QMessageBox.Yes:
                parent.copy_dialog(text=encoded_payload,
                                   suggested_name='accepted.txt')


class FinalizeWindow(QMainWindow, Ui_FinalizeWindow):
    def __init__(self, parent, proposal):
        QMainWindow.__init__(self, parent)
        self.setupUi(parent)

        setup_toolbar(parent, self)

        self.buttonExecute.clicked.connect(
            lambda: self.finalize(
                parent,
                proposal,
                broadcast=True))

        with ConnCtx(parent.credentials, parent.critical, True) as cc:
            connection = cc.connection
            parent.asset_data.update(connection)
            check_not_mine(proposal['u_address_r'], connection)

            (tx, amount_p, asset_p, fee_p, amount_r, asset_r,
             fee_r) = swap.parse_accepted(
                *[proposal[k] for k in ACCEPTED_KEYS],
                connection=connection)

            self.labelProposerAmountValue.setText(f2s(sat2btc(amount_p)))
            self.labelProposerAssetValue.setText(
                parent.asset_data.get_label(asset_p))
            self.labelReceiverAmountValue.setText(f2s(sat2btc(amount_r)))
            self.labelReceiverAssetValue.setText(
                parent.asset_data.get_label(asset_r))

    def finalize(self, parent, proposal, broadcast=False):

        with ConnCtx(parent.credentials, parent.critical) as cc:
            connection = cc.connection
            check_wallet_unlocked(connection)
            check_not_mine(proposal['u_address_r'], connection)

            (incomplete_tx, _, _, fee_p, _, _, _) = swap.parse_accepted(
                *[proposal[k] for k in ACCEPTED_KEYS],
                connection=connection)

            msg = 'Are you sure you want to execute this swap?\n\n' \
                  'Paying fees {:.8f} L-BTC.'.format(sat2btc(fee_p))
            ans = QMessageBox.question(parent, 'Confirm', msg)
            if ans != QMessageBox.Yes:
                return

            ret = swap.finalize(incomplete_tx, connection, broadcast)
            if broadcast:
                msg = 'Transaction ID: {}'.format(ret)
                QMessageBox.information(parent, 'Transaction sent', msg)
                InitialWindow(parent)
            else:
                parent.copy_dialog(text=ret,
                                   title='Copy Transaction Hex',
                                   suggested_name='transaction.txt')


class InitialWindow(QMainWindow, Ui_StartWindow):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)

        self.setupUi(parent)
        setup_toolbar(parent, self)
        parent.asset_data = AssetsData()

        self.buttonStart.clicked.connect(
            lambda: ProposeWindow(parent))

        self.buttonContinue.clicked.connect(
            lambda: parent.paste_dialog())


class LiquidSwapToolWindow(QMainWindow):
    """Parent window holding session data"""

    def __init__(self, service_url=None, elements_conf_file=None,
                 network=NETWORK_REGTEST):
        QMainWindow.__init__(self)

        self.credentials = {
            'elements_conf_file': elements_conf_file,
            'service_url': service_url,
            'service_port': (None if network == NETWORK_MAINNET else DEFAULT_REGTEST_RPC_PORT),
        }
        self.network = network
        self.asset_data = AssetsData()

        self.center()

        with ConnCtx(self.credentials, self.critical) as cc:
            do_initial_checks(cc.connection, network)

        InitialWindow(parent=self)

    def center(self):
        # TODO: test in different os
        fg = self.frameGeometry()
        d = QApplication.desktop()
        s = d.screenNumber(d.cursor().pos())
        cp = d.screenGeometry(s).center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

    def critical(self, title, message, start_over=False):
        QMessageBox.critical(self, title, message)
        if start_over:
            InitialWindow(self)

    def change_conf_file(self, action):
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Choose elements.conf',
            self.credentials['elements_conf_file'] or os.path.expanduser('~'))
        if not filename:
            return
        try:
            with open(filename, 'r') as r:
                temp = self.credentials
                temp['elements_conf_file'] = filename
                with ConnCtx(temp, self.critical) as cc:
                    do_initial_checks(cc.connection, self.network)
                    self.credentials = temp
                    set_conf_tip(self.credentials['elements_conf_file'],
                                 action)
        except IOError:
            # FIXME: is this reachable?
            pass

    def change_service_url(self, action):
        d = URLDialog(self)
        ret = d.exec_()
        if ret:
            temp = self.credentials
            temp['service_url'] = d.lineEditURL.text()
            with ConnCtx(temp, self.critical) as cc:
                do_initial_checks(cc.connection, self.network)
                self.credentials = temp
                set_url_tip(self.credentials['service_url'], action)

    def add_new_asset(self, combo_box):
        d = AddNewAssetDialog(self)
        ret = d.exec_()
        if ret:
            id = d.lineEditAsset.text().lower()
            label = d.lineEditLabel.text()
            try:
                self.asset_data.add_temp_label(id, label, allow_update=False)
                label = self.asset_data.get_label(id)
                combo_box.addItem(label, id)
                combo_box.setCurrentText(label)
            except LiquidSwapError as e:
                QMessageBox.critical(self, 'Swap Error', str(e))
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def copy_dialog(self, text='', title='', suggested_name=''):
        d = CopyDialog(self, text, title, suggested_name)
        if d.exec_():
            InitialWindow(self)

    def paste_dialog(self):
        d = PasteDialog(self)
        if d.exec_():
            self.check_proposal(d.textBrowser.toPlainText())

    def check_proposal(self, payload):
        try:
            proposal = decode_payload(payload)
            status = get_status(proposal)
        except Exception as e:
            QMessageBox.critical(self, 'Error',
                                 'Unable to decode proposal: {}'.format(e))
            InitialWindow(self)
        else:
            if status == 'proposed':
                AcceptWindow(self, proposal)
            else:
                FinalizeWindow(self, proposal)


def handle_high_resolution_display():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Liquid Swap Tool Graphical User Interface')
    parser.add_argument('--version', action='version',
                        version='v{}'.format(__version__))
    parser.add_argument('-c', '--conf-file',
                        help='Specify elements.conf file for authentication.')
    parser.add_argument('-u', '--service-url',
                        help='Specify Elements node URL for authentication.')
    parser.add_argument('-r', '--regtest', action='store_true',
                        help='Use with regtest.')
    parser.add_argument('-v', '--verbose', action='count',
                        help='Be more verbose, may be used multiple times.')
    args = parser.parse_args()
    set_logging(args.verbose or 0)

    return {
        'service_url': args.service_url,
        'elements_conf_file': args.conf_file,
        'network': NETWORK_REGTEST if args.regtest else NETWORK_MAINNET
    }


def main(parse=True):
    handle_high_resolution_display()
    app = QApplication(sys.argv)
    kwargs = parse_args() if parse else {'network': NETWORK_MAINNET}
    ex = LiquidSwapToolWindow(**kwargs)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
