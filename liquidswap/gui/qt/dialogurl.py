# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './liquidswap/gui/ui/dialogurl.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_URLDialog(object):
    def setupUi(self, URLDialog):
        URLDialog.setObjectName("URLDialog")
        URLDialog.resize(500, 100)
        self.gridLayout = QtWidgets.QGridLayout(URLDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(URLDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEditURL = QtWidgets.QLineEdit(URLDialog)
        self.lineEditURL.setMaxLength(2000)
        self.lineEditURL.setObjectName("lineEditURL")
        self.horizontalLayout.addWidget(self.lineEditURL)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(URLDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(URLDialog)
        self.buttonBox.accepted.connect(URLDialog.accept)
        self.buttonBox.rejected.connect(URLDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(URLDialog)

    def retranslateUi(self, URLDialog):
        _translate = QtCore.QCoreApplication.translate
        URLDialog.setWindowTitle(_translate("URLDialog", "Specify Liquid Node URL"))
        self.label.setText(_translate("URLDialog", "Liquid Node URL: "))
        self.lineEditURL.setPlaceholderText(_translate("URLDialog", "http://user:authdata@localhost:7041"))

