from designer_generated_ui.download import Ui_Dialog
from references import *
class DownDialog(QDialog,Ui_Dialog):
    def __init__(self, parent=None, name="Download" ,info=None):
        super(DownDialog,self).__init__(parent)
        self.setupUi(self)
        self.connect(self.pushButton,SIGNAL('clicked()'), self.cancel)
        self.info=info
        self.setWindowTitle(name)
        updth=Thread(target=self.update)
        updth.daemon=True
        updth.start()

    def update(self):
        pass

    def cancel(self):
        self.close()

