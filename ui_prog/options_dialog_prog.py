__author__ = 'Frank'

from references import *

class OptionsDialog(QDialog,Ui_Dialog):
    contains=0;
    begin_with=1;
    end_with=2;
    default_dir="/"
    def __init__(self,match_options, root_dir,parent=None):
        super(OptionsDialog,self).__init__(parent)
        #poner la opción marcada
        self.setupUi(self)
        self.lineEdit_root.setText(root_dir)
        self.match_options=match_options;
        if self.match_options==OptionsDialog.contains:
            self.radioButton_contains.toggle()
        elif self.match_options==OptionsDialog.begin_with:
            self.radioButton_starts_with.toggle()
        else:
            self.radioButton_ends_with.toggle()
        self.connect(self.pushButton_browse,SIGNAL('clicked()'),self.browse)
        self.connect(self.pushButton_save,SIGNAL('clicked()'),self.save)
        self.connect(self.pushButton_cancel,SIGNAL('clicked()'),self.close)

    def browse(self):
        dir_result=QFileDialog.getExistingDirectory(self,"Descargar",
            "/home",
            QFileDialog.ShowDirsOnly
            | QFileDialog.DontResolveSymlinks)
        if dir_result:
            self.lineEdit_root.setText(dir_result)

    def save(self):
        #poner regunta para comprobar si es una dirección válida de disco, si no lo es sacar cartelón
        if not path.isdir(self.lineEdit_root.text()):
            QMessageBox.warning(self,"Error", "Directorio no válido")
            return;
        if self.radioButton_contains.isChecked():
            self.match_options=OptionsDialog.contains
        elif self.radioButton_starts_with.isChecked():
            self.match_options=OptionsDialog.begin_with
        else:
            self.match_options=OptionsDialog.end_with
        self.accept()