# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './liquidswap/gui/ui/dialogaddnewasset.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AddNewAssetDialog(object):
    def setupUi(self, AddNewAssetDialog):
        AddNewAssetDialog.setObjectName("AddNewAssetDialog")
        AddNewAssetDialog.resize(660, 127)
        self.gridLayout_2 = QtWidgets.QGridLayout(AddNewAssetDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.lineEditAsset = QtWidgets.QLineEdit(AddNewAssetDialog)
        self.lineEditAsset.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lineEditAsset.setText("")
        self.lineEditAsset.setMaxLength(64)
        self.lineEditAsset.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditAsset.setObjectName("lineEditAsset")
        self.gridLayout.addWidget(self.lineEditAsset, 0, 1, 1, 1)
        self.labelLabel = QtWidgets.QLabel(AddNewAssetDialog)
        self.labelLabel.setObjectName("labelLabel")
        self.gridLayout.addWidget(self.labelLabel, 1, 0, 1, 1)
        self.labelAsset = QtWidgets.QLabel(AddNewAssetDialog)
        self.labelAsset.setObjectName("labelAsset")
        self.gridLayout.addWidget(self.labelAsset, 0, 0, 1, 1)
        self.lineEditLabel = QtWidgets.QLineEdit(AddNewAssetDialog)
        self.lineEditLabel.setMaxLength(64)
        self.lineEditLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditLabel.setObjectName("lineEditLabel")
        self.gridLayout.addWidget(self.lineEditLabel, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddNewAssetDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(AddNewAssetDialog)
        self.buttonBox.accepted.connect(AddNewAssetDialog.accept)
        self.buttonBox.rejected.connect(AddNewAssetDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddNewAssetDialog)

    def retranslateUi(self, AddNewAssetDialog):
        _translate = QtCore.QCoreApplication.translate
        AddNewAssetDialog.setWindowTitle(_translate("AddNewAssetDialog", "Add New Asset"))
        self.labelLabel.setText(_translate("AddNewAssetDialog", "Label:"))
        self.labelAsset.setText(_translate("AddNewAssetDialog", "Asset Id:"))

