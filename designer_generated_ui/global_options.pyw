# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'global_options.ui'
#
# Created: Tue Nov 27 21:28:09 2012
#      by: PyQt4 UI code generator 4.9
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog_global_opt(object):
    def setupUi(self, Dialog_global_opt):
        Dialog_global_opt.setObjectName(_fromUtf8("Dialog_global_opt"))
        Dialog_global_opt.resize(346, 256)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("images/Options.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_global_opt.setWindowIcon(icon)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog_global_opt)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_new_watch = QtGui.QLabel(Dialog_global_opt)
        self.label_new_watch.setObjectName(_fromUtf8("label_new_watch"))
        self.verticalLayout.addWidget(self.label_new_watch)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lineEdit_root = QtGui.QLineEdit(Dialog_global_opt)
        self.lineEdit_root.setMinimumSize(QtCore.QSize(250, 0))
        self.lineEdit_root.setObjectName(_fromUtf8("lineEdit_root"))
        self.horizontalLayout_2.addWidget(self.lineEdit_root)
        self.pushButton_browse = QtGui.QPushButton(Dialog_global_opt)
        self.pushButton_browse.setMaximumSize(QtCore.QSize(30, 16777215))
        self.pushButton_browse.setObjectName(_fromUtf8("pushButton_browse"))
        self.horizontalLayout_2.addWidget(self.pushButton_browse)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.listWidget = QtGui.QListWidget(Dialog_global_opt)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout_2.addWidget(self.listWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton_add = QtGui.QPushButton(Dialog_global_opt)
        self.pushButton_add.setObjectName(_fromUtf8("pushButton_add"))
        self.horizontalLayout.addWidget(self.pushButton_add)
        self.pushButton_remove = QtGui.QPushButton(Dialog_global_opt)
        self.pushButton_remove.setObjectName(_fromUtf8("pushButton_remove"))
        self.horizontalLayout.addWidget(self.pushButton_remove)
        spacerItem = QtGui.QSpacerItem(28, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_save = QtGui.QPushButton(Dialog_global_opt)
        self.pushButton_save.setObjectName(_fromUtf8("pushButton_save"))
        self.horizontalLayout.addWidget(self.pushButton_save)
        self.pushButton_cancel = QtGui.QPushButton(Dialog_global_opt)
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.horizontalLayout.addWidget(self.pushButton_cancel)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.retranslateUi(Dialog_global_opt)
        QtCore.QMetaObject.connectSlotsByName(Dialog_global_opt)

    def retranslateUi(self, Dialog_global_opt):
        Dialog_global_opt.setWindowTitle(QtGui.QApplication.translate("Dialog_global_opt", "Opciones", None, QtGui.QApplication.UnicodeUTF8))
        self.label_new_watch.setText(QtGui.QApplication.translate("Dialog_global_opt", "<html><head/><body><p>Añada su nueva dirección local para monitorear:</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_browse.setText(QtGui.QApplication.translate("Dialog_global_opt", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_add.setText(QtGui.QApplication.translate("Dialog_global_opt", "Añadir", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_remove.setText(QtGui.QApplication.translate("Dialog_global_opt", "Eliminar", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_save.setText(QtGui.QApplication.translate("Dialog_global_opt", "Guardar", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_cancel.setText(QtGui.QApplication.translate("Dialog_global_opt", "Cancelar", None, QtGui.QApplication.UnicodeUTF8))

