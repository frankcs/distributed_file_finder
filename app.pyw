from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
from qt_references import *
from searcher import *
from about import *
from options import *
from os import path
from sentry import octopus_handler,db_manager,Observer,Thread

class AboutDialog(QDialog,Ui_Dialog_about):
    def __init__(self, parent=None):
        super(AboutDialog,self).__init__(parent)
        self.setupUi(self)
        self.connect(self.pushButton_ok,SIGNAL('clicked()'),self.close)

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

class Form(QMainWindow,Ui_MainWindow):
    instances = []# to provide sdi
    def __init__(self,broker, parent=None):
        super(Form,self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        Form.instances.append(self)
        #initializing
        self.dir=OptionsDialog.default_dir
        self.match_opt=OptionsDialog.contains
        self.broker=broker
        self.text=""
        self.cancel=True
        self.setupUi(self)
        self.tableWidget_result.setShowGrid(False)
        self.current_pos=0
        self.connect(self.action_quit,SIGNAL("triggered()"),self.close)
        self.connect(self.action_new_search,SIGNAL("triggered()"), self.new_search)
        self.connect(self.action_about,SIGNAL("triggered()"),self.show_dialog_about)
        self.connect(self.action_options,SIGNAL("triggered()"),self.show_dialog_options)
        self.connect(self,SIGNAL('destroyed()'),self.updateInstances)
        self.connect(self.pushButton_search,SIGNAL('clicked()'),self.search)
        self.connect(self.lineEdit_input,SIGNAL('returnPressed()'),self.search)
        self.connect(self.pushButton_download,SIGNAL('clicked()'),self.download)
        self.connect(self.tableWidget_result,SIGNAL('itemClicked (QTableWidgetItem *)'),self.select_row)
        self.lineEdit_input.setText('Escriba su patrón de búsqueda aquí')
        self.lineEdit_input.selectAll()
        self.lineEdit_input.setFocus()
        self.disable_buttons()
        self.lineEdit_input.selectAll()
        self.lineEdit_input.setFocus()


    def show_dialog_about(self):
        dialog=AboutDialog(self)
        dialog.exec_()

    def show_dialog_options(self):
        dialog=OptionsDialog(self.match_opt,self.dir,self)
        if dialog.exec_():
            self.dir=dialog.lineEdit_root.text()
            self.match_opt=dialog.match_options


    def disable_buttons(self):
        self.pushButton_download.setEnabled(False)
        self.pushButton_copy_route.setEnabled(False)
        self.pushButton_open.setEnabled(False)

    def enable_buttons(self):
        self.pushButton_download.setEnabled(True)
        self.pushButton_copy_route.setEnabled(True)
        self.pushButton_open.setEnabled(True)

    def new_search(self):
        self.broker.new_search()
    
    def search(self):
        if not self.cancel:
            self.cancel=True
            return
        self.text=self.lineEdit_input.text()
        #do the search and add to the list widget
        if self.text:
            #limpiar el listWidget
            self.tableWidget_result.clearContents()
            self.tableWidget_result.setRowCount(0)
            self.current_pos=0
            #Desactivar los botones
            self.disable_buttons()
            self.lineEdit_input.setEnabled(False)
            t=Thread(target=self.update_results)
            t.daemon=True
            t.start()

    def update_results(self):
        self.cancel=False
        self.setWindowTitle('Buscando :"{}"'.format(self.text))
        self.pushButton_search.setText("Cancelar")
        results=self.broker.search(self.text,self.match_opt)
        try:
            for x in results:
                t1=QTableWidgetItem(x[1])
                t1.setFlags(Qt.ItemIsSelectable)
                t1.setTextColor(QColor('Black'))
                t1.setBackgroundColor (QColor('whitesmoke'))
                t2=QTableWidgetItem(x[0])
                t2.setFlags(Qt.ItemIsSelectable)
                t2.setTextColor(QColor('Black'))

                self.tableWidget_result.insertRow(self.current_pos)
                self.tableWidget_result.setItem(self.current_pos,0,t1)
                self.tableWidget_result.setItem(self.current_pos,1,t2)
                self.current_pos+=1
                if self.current_pos%200==0:
                 self.setWindowTitle('Resultados para "{}": más de {}'.format(self.text,self.current_pos))
                if self.cancel:
                    results.send(self.cancel)
        except : pass
        self.pushButton_search.setText("Buscar")
        self.lineEdit_input.setEnabled(True)
        self.setWindowTitle('Octopus: {} resultados para "{}"'.format(self.current_pos,self.text))
        self.cancel=True

    def select_row(self, item):
        self.enable_buttons()
        self.tableWidget_result.selectRow(item.row())

    def download(self):
        dir = QFileDialog.getExistingDirectory(self,"Descargar",
            "/home",
            QFileDialog.ShowDirsOnly
            | QFileDialog.DontResolveSymlinks)
        self.lineEdit_input.setText(dir)# just for test
        #now the code for downloading the file

    @staticmethod
    def updateInstances():
        Form.instances = [window for window\
                      in Form.instances if is_alive(window)]

def is_alive(qobj):
    import sip
    try:
        sip.unwrapinstance(qobj)
    except RuntimeError:
        return False
    return True

WATCHES=["D:\\"]
FIRSTIME=True
class Sys_Tray(QDialog):
    def __init__(self):
        super(Sys_Tray, self).__init__()
        self.db_search_manager=db_manager("./files_db.db",WATCHES)
        if FIRSTIME:
            self.db_search_manager.populate_database()
            QMessageBox.warning(self,"Alert", "Created Database")

        self.fs_handler= octopus_handler(self.db_search_manager)
        observer=Observer()
        observer.schedule(self.fs_handler,WATCHES[0], recursive=True)
        observer.start()
        #Finalizada la creación de visor de eventos y de la conexión con la base de datos
        #creando el tray
        self.createActions()
        self.createTrayIcon()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("images/Search Folder.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.trayIcon.activated.connect(self.iconActivated)
        self.trayIcon.setIcon(icon)
        self.trayIcon.show()
        self.showMessage()

    def createActions(self):
        self.new_SearchAction = QtGui.QAction("Nueva Búsqueda", self,
            triggered=self.new_search)
        self.set_action_icon(self.new_SearchAction,"images/Search Folder.png")

        self.global_optionsAction=QtGui.QAction("Opciones Globales", self,
            triggered=self.show_options)
        self.set_action_icon(self.global_optionsAction,"images/Options.png")

        self.quitAction = QtGui.QAction("&Quit", self,
            triggered=QtGui.qApp.quit)
        self.set_action_icon(self.quitAction,"images/Button - Shutdown.png")

    def set_action_icon(self,action,path):
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(path)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        action.setIcon(icon1)

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.new_SearchAction)
        self.trayIconMenu.addAction(self.global_optionsAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

    def iconActivated(self, reason):
        if reason== QtGui.QSystemTrayIcon.DoubleClick:
            self.new_search()
        elif reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.showMessage()

    def new_search(self):
        Form(self).show()

    def show_options(self):
        QMessageBox.warning(self,"Error", "Not implemented yet")

    def search(self,pattern, match_option):
        return self.db_search_manager.search_result(pattern, match_option)

    def showMessage(self):
        self.trayIcon.showMessage("Hola",
            "Octopus está desde ahora vigilando sus ficheros.")

def main():
    app=QApplication(sys.argv)

    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        QtGui.QMessageBox.critical(None, "Systray",
            "I couldn't detect any system tray on this system.")
        sys.exit(1)

    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    tray=Sys_Tray()
    app.exec_()
main()


