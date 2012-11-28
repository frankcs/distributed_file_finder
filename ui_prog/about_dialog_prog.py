__author__ = 'Frank'

from references import *

class AboutDialog(QDialog,Ui_Dialog_about):
    def __init__(self, parent=None):
        super(AboutDialog,self).__init__(parent)
        self.setupUi(self)
        self.connect(self.pushButton_ok,SIGNAL('clicked()'),self.close)