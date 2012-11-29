__author__ = 'Frank'

from references import *

class LocalOptionsDialog(QDialog,Ui_Dialog_local_opt):
    contains=0;
    begin_with=1;
    end_with=2;
    def __init__(self,match_options,parent=None):
        super(LocalOptionsDialog,self).__init__(parent)
        #poner la opción marcada
        self.match_options=match_options
        self.setupUi(self)
        if self.match_options==LocalOptionsDialog.contains:
            self.radioButton_contains.toggle()
        elif self.match_options==LocalOptionsDialog.begin_with:
            self.radioButton_starts_with.toggle()
        else:
            self.radioButton_ends_with.toggle()
        self.connect(self.pushButton_save,SIGNAL('clicked()'),self.save)
        self.connect(self.pushButton_cancel,SIGNAL('clicked()'),self.close)

    def save(self):
        if self.radioButton_contains.isChecked():
            self.match_options=LocalOptionsDialog.contains
        elif self.radioButton_starts_with.isChecked():
            self.match_options=LocalOptionsDialog.begin_with
        else:
            self.match_options=LocalOptionsDialog.end_with
        self.accept()