# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'local_options.ui'
#
# Created: Tue Nov 27 20:35:58 2012
#      by: PyQt4 UI code generator 4.9
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog_local_opt(object):
    def setupUi(self, Dialog_local_opt):
        Dialog_local_opt.setObjectName(_fromUtf8("Dialog_local_opt"))
        Dialog_local_opt.resize(215, 149)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("images/Options.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_local_opt.setWindowIcon(icon)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(Dialog_local_opt)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox_pattern_opt = QtGui.QGroupBox(Dialog_local_opt)
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
        self.verticalLayout_2.addWidget(self.groupBox_pattern_opt)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.pushButton_save = QtGui.QPushButton(Dialog_local_opt)
        self.pushButton_save.setObjectName(_fromUtf8("pushButton_save"))
        self.horizontalLayout_2.addWidget(self.pushButton_save)
        self.pushButton_cancel = QtGui.QPushButton(Dialog_local_opt)
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.horizontalLayout_2.addWidget(self.pushButton_cancel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.retranslateUi(Dialog_local_opt)
        QtCore.QMetaObject.connectSlotsByName(Dialog_local_opt)

    def retranslateUi(self, Dialog_local_opt):
        Dialog_local_opt.setWindowTitle(QtGui.QApplication.translate("Dialog_local_opt", "Opciones", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_pattern_opt.setTitle(QtGui.QApplication.translate("Dialog_local_opt", "Opciones de comparación de patrón", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_contains.setText(QtGui.QApplication.translate("Dialog_local_opt", "Contiene", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_starts_with.setText(QtGui.QApplication.translate("Dialog_local_opt", "Comienza con", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_ends_with.setText(QtGui.QApplication.translate("Dialog_local_opt", "Termina en", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_save.setText(QtGui.QApplication.translate("Dialog_local_opt", "Guardar", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_cancel.setText(QtGui.QApplication.translate("Dialog_local_opt", "Cancelar", None, QtGui.QApplication.UnicodeUTF8))

