# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'options.ui'
#
# Created: Mon Oct 15 08:51:59 2012
#      by: PyQt4 UI code generator 4.9
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(310, 201)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("images/Options.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout_4 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_root = QtGui.QLabel(Dialog)
        self.label_root.setObjectName(_fromUtf8("label_root"))
        self.verticalLayout_2.addWidget(self.label_root)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lineEdit_root = QtGui.QLineEdit(Dialog)
        self.lineEdit_root.setMinimumSize(QtCore.QSize(250, 0))
        self.lineEdit_root.setObjectName(_fromUtf8("lineEdit_root"))
        self.horizontalLayout_2.addWidget(self.lineEdit_root)
        self.pushButton_browse = QtGui.QPushButton(Dialog)
        self.pushButton_browse.setMaximumSize(QtCore.QSize(30, 16777215))
        self.pushButton_browse.setObjectName(_fromUtf8("pushButton_browse"))
        self.horizontalLayout_2.addWidget(self.pushButton_browse)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.groupBox_pattern_opt = QtGui.QGroupBox(Dialog)
        self.groupBox_pattern_opt.setObjectName(_fromUtf8("groupBox_pattern_opt"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_pattern_opt)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.radioButton_contains = QtGui.QRadioButton(self.groupBox_pattern_opt)
        self.radioButton_contains.setChecked(True)
        self.radioButton_contains.setObjectName(_fromUtf8("radioButton_contains"))
        self.verticalLayout.addWidget(self.radioButton_contains)
        self.radioButton_starts_with = QtGui.QRadioButton(self.groupBox_pattern_opt)
        self.radioButton_starts_with.setObjectName(_fromUtf8("radioButton_starts_with"))
        self.verticalLayout.addWidget(self.radioButton_starts_with)
        self.radioButton_ends_with = QtGui.QRadioButton(self.groupBox_pattern_opt)
        self.radioButton_ends_with.setObjectName(_fromUtf8("radioButton_ends_with"))
        self.verticalLayout.addWidget(self.radioButton_ends_with)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addWidget(self.groupBox_pattern_opt)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QtGui.QSpacerItem(118, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.pushButton_save = QtGui.QPushButton(Dialog)
        self.pushButton_save.setObjectName(_fromUtf8("pushButton_save"))
        self.horizontalLayout_3.addWidget(self.pushButton_save)
        self.pushButton_cancel = QtGui.QPushButton(Dialog)
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.horizontalLayout_3.addWidget(self.pushButton_cancel)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Opciones", None, QtGui.QApplication.UnicodeUTF8))
        self.label_root.setText(QtGui.QApplication.translate("Dialog", "<html><head/><body><p>Directorio raíz local:</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_browse.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_pattern_opt.setTitle(QtGui.QApplication.translate("Dialog", "Opciones de comparación de patrón", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_contains.setText(QtGui.QApplication.translate("Dialog", "Contiene", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_starts_with.setText(QtGui.QApplication.translate("Dialog", "Comienza con", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_ends_with.setText(QtGui.QApplication.translate("Dialog", "Termina en", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_save.setText(QtGui.QApplication.translate("Dialog", "Guardar", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_cancel.setText(QtGui.QApplication.translate("Dialog", "Cancelar", None, QtGui.QApplication.UnicodeUTF8))

