from designer_generated_ui.download import Ui_Dialog
from references import *
from threading import Timer
class DownDialog(QDialog,Ui_Dialog):
    def __init__(self, parent=None, name="Download" ,info=None):
        super(DownDialog,self).__init__(parent)
        self.setupUi(self)
        self.connect(self.pushButton,SIGNAL('clicked()'), self.cancel)
        self.info=info
        self.setWindowTitle(name)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        updth=Thread(target=self.update)
        updth.daemon=True
        updth.start()

    def update(self):
        Timer(0.5, self.update).start()
        self.progressBar.setValue(self.info.ratio)

    def cancel(self):
        self.info.cancel=True
        self.close()

