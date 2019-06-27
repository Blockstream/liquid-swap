# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './liquidswap/gui/ui/dialogpaste.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PasteDialog(object):
    def setupUi(self, PasteDialog):
        PasteDialog.setObjectName("PasteDialog")
        PasteDialog.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(PasteDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(PasteDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setAcceptRichText(False)
        self.textBrowser.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextEditorInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.textBrowser.setOpenLinks(False)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonImport = QtWidgets.QPushButton(PasteDialog)
        self.buttonImport.setObjectName("buttonImport")
        self.horizontalLayout.addWidget(self.buttonImport)
        self.buttonCancel = QtWidgets.QPushButton(PasteDialog)
        self.buttonCancel.setObjectName("buttonCancel")
        self.horizontalLayout.addWidget(self.buttonCancel)
        self.buttonOk = QtWidgets.QPushButton(PasteDialog)
        self.buttonOk.setObjectName("buttonOk")
        self.horizontalLayout.addWidget(self.buttonOk)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(PasteDialog)
        QtCore.QMetaObject.connectSlotsByName(PasteDialog)

    def retranslateUi(self, PasteDialog):
        _translate = QtCore.QCoreApplication.translate
        PasteDialog.setWindowTitle(_translate("PasteDialog", "Paste Proposal"))
        self.textBrowser.setHtml(_translate("PasteDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.buttonImport.setText(_translate("PasteDialog", "Import…"))
        self.buttonCancel.setText(_translate("PasteDialog", "Cancel"))
        self.buttonOk.setText(_translate("PasteDialog", "OK"))

