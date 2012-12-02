__author__ = 'Frank'

from references import *

class GlobalOptionsDialog(QDialog,Ui_Dialog_global_opt):
    default_dir="/"
    def __init__(self, watches=[path.realpath("/")] ,parent=None):
        super(GlobalOptionsDialog,self).__init__(parent)
        #poner la opción marcada
        self.setupUi(self)
        self.connect(self.pushButton_browse,SIGNAL('clicked()'),self.browse)
        self.connect(self.pushButton_save,SIGNAL('clicked()'),self.save)
        self.connect(self.pushButton_cancel,SIGNAL('clicked()'),self.close)
        self.connect(self.listWidget,SIGNAL('itemClicked (QListWidgetItem *)'),self.item_selected)
        self.connect(self.pushButton_add,SIGNAL('clicked()'),self.add)
        self.connect(self.pushButton_remove,SIGNAL('clicked()'),self.remove)
        self.watches=watches
        self.listWidget.addItems(watches)
        self.current_item= None
        self.pushButton_remove.setEnabled(False)

    def browse(self):
        dir_result=QFileDialog.getExistingDirectory(self,"Descargar",
            "/home",
            QFileDialog.ShowDirsOnly
            | QFileDialog.DontResolveSymlinks)
        if dir_result:
            self.lineEdit_root.setText(dir_result)

    def item_selected(self, item):
        self.pushButton_remove.setEnabled(True)
        self.current_item=item

    def add(self):
        text=self.lineEdit_root.text()
        if text:
            if path.isdir(text):
                result=self.is_subpath(text)
                if not result:
                    result= self.is_superpath(text)
                    if result:
                        follow=QMessageBox.question(self, "Proceder?", "El directorio especificado contiene algunas de las direcciones ya monitoreadas, estas se eliminarán. Está seguro?",
                            buttons= QMessageBox.Ok|QMessageBox.Cancel)
                        #no añadir la nueva dirección por que no quieres reescribir
                        if  follow == QMessageBox.Cancel:
                            return
                        else:
                            for subpath in result:
                                self.watches.remove(subpath)
                    self.watches.append(text)
                else:
                    QMessageBox.warning(self,"Atención", "El directorio seleccionado está siendo monitoreado por un observador en {}".format(result))
            else:
                QMessageBox.critical(self,"Error", "Directorio no válido")
            self.listWidget.clear()
            self.listWidget.addItems(self.watches)

    def is_subpath(self,path):
        for x in self.watches:
            if path.startswith(x):
                return x

    def is_superpath(self,path):
        result = []
        for x in self.watches:
            if x.startswith(path):
                result.append(x)
        return result

    def remove(self):
        if self.current_item:
            toremove = self.current_item.text()
            self.watches.remove(toremove)
            self.listWidget.clear()
            self.listWidget.addItems(self.watches)
            self.current_item=None
            self.pushButton_remove.setEnabled(False)

    def save(self):
        if not self.watches:
            QMessageBox.critical(self,"Error", "La lista de rutas a monitorear no debe ser vacía")
            return
        self.accept()