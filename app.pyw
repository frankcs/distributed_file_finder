from references import *
from ui_prog.searcher_prog import Form
from ui_prog.global_options_prog import GlobalOptionsDialog
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

WATCHES=["D:\\"]
FIRSTIME=False
class Sys_Tray(QDialog):
    def __init__(self):
        super(Sys_Tray, self).__init__()
        self.db_search_manager=db_manager("./data/files_db.db",WATCHES)
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
        dialog=GlobalOptionsDialog(parent=self)
        if dialog.exec_():pass

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


