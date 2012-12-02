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
    def __init__(self, app):
        super(Sys_Tray, self).__init__()
        self.createActions()
        self.createTrayIcon()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("images/Search Folder.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #el paso de app para captura el close
        self.app=app
        #para salvar las watches una vez quitada la app
        #self.connect(self.app,SIGNAL('lastWindowClosed ()'),self.save_watches)
        #self.trayIcon.activated.connect(self.iconActivated)
        self.trayIcon.setIcon(icon)
        self.trayIcon.show()
        self.showMessage()
        self.watches=WATCHES
        self.db_search_manager=db_manager("./data/files_db.db")
        if FIRSTIME:
            self.db_search_manager.reset_database()
        self.watches=self.db_search_manager.retrieve_watches()
        self.fs_handler= octopus_handler(self.db_search_manager)
        self.dict_watch_obs={}
        self.db_search_manager.delete_all_file_data()
        self.update_watches(self.watches)

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

    #def iconActivated(self, reason):
    #    if reason== QtGui.QSystemTrayIcon.DoubleClick:
    #        self.new_search()
    #    elif reason == QtGui.QSystemTrayIcon.MiddleClick:
    #        self.showMessage()

    def new_search(self):
        Form(self).show()

    def show_options(self):
        dialog=GlobalOptionsDialog(watches=[x for x in self.watches],parent=self)
        if dialog.exec_():
            self.update_watches(dialog.watches)
            self.save_watches()

    def update_watches(self, new_watches):
        self.trayIcon.showMessage("Procesando",
            "Octopus está actualizando sus índices")
        #cerrar todas las ventanas
        for x in Form.instances:
            x.close()
        #deshabilitar las opciones de nueva búsqueda
        self.new_SearchAction.setEnabled(False)
        #si las viejas watchs no están en la nueva lista las quito
        to_delete=[]
        for old_watch in self.dict_watch_obs.keys():
            if not old_watch in new_watches:
                self.db_search_manager.delete_all_within_path(old_watch)
                self.dict_watch_obs[old_watch].unschedule_all()
                self.dict_watch_obs[old_watch].stop()
                to_delete.append(old_watch)
        for x in to_delete:
            del self.dict_watch_obs[x]
        for new_watch in new_watches:
            if not new_watch in self.dict_watch_obs.keys():
                self.db_search_manager.insert_everything_under_path(new_watch)
                self.dict_watch_obs[new_watch]=Observer()
                self.dict_watch_obs[new_watch].schedule(self.fs_handler,new_watch, recursive=True)
                self.dict_watch_obs[new_watch].start()
        self.trayIcon.showMessage("Terminado",
            "Octopus ha actualizado sus índices")
        #habilitar las opciones de nueva búsqueda
        self.new_SearchAction.setEnabled(True)
        self.watches=new_watches

    def save_watches(self):
        self.db_search_manager.persist_watches(self.watches)

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
    tray=Sys_Tray(app)
    app.exec_()
main()


