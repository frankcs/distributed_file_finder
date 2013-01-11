__author__ = 'Frank'
from references import *
from ui_prog.local_options_prog import LocalOptionsDialog
from ui_prog.about_dialog_prog import AboutDialog
from ui_prog.download_prog import DownDialog
from network.downloadinfo import DownloadInfo
from threading import Thread
import os

class Form(QMainWindow,Ui_MainWindow):
    instances = []# to provide sdi
    def __init__(self,broker, parent=None):
        super(Form,self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        Form.instances.append(self)
        #initializing
        self.match_opt=LocalOptionsDialog.contains
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
        self.selected_touple=None


    def show_dialog_about(self):
        dialog=AboutDialog(self)
        dialog.exec_()

    def show_dialog_options(self):
        dialog=LocalOptionsDialog(self.match_opt,self)
        if dialog.exec_():
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
            for list in results:
                for x in list:
                    t1=QTableWidgetItem(x[1])
                    t1.setFlags(Qt.ItemIsSelectable)
                    t1.setTextColor(QColor('Black'))
                    t1.setBackgroundColor (QColor('whitesmoke'))
                    dir="SI" if x[2] else "NO"
                    t2=QTableWidgetItem(dir)
                    t2.setFlags(Qt.ItemIsSelectable)
                    t2.setTextColor(QColor('Black'))
                    t3=QTableWidgetItem(x[3])
                    t3.setFlags(Qt.ItemIsSelectable)
                    t3.setTextColor(QColor('Black'))
                    t4=QTableWidgetItem(x[0])
                    t4.setFlags(Qt.ItemIsSelectable)
                    t4.setTextColor(QColor('Black'))

                    self.tableWidget_result.insertRow(self.current_pos)
                    self.tableWidget_result.setItem(self.current_pos,0,t1)
                    self.tableWidget_result.setItem(self.current_pos,1,t2)
                    self.tableWidget_result.setItem(self.current_pos,2,t3)
                    self.tableWidget_result.setItem(self.current_pos,3,t4)

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
        self.disable_buttons()
        self.tableWidget_result.selectRow(item.row())
        name= self.tableWidget_result.item(item.row(),0).text()
        is_dir=self.tableWidget_result.item(item.row(),1).text()
        source=self.tableWidget_result.item(item.row(),2).text()
        path=self.tableWidget_result.item(item.row(),3).text()
        self.selected_touple=(name,is_dir,source,path)
        if is_dir=='NO' or source=='localhost':
            self.enable_buttons()

    def download(self):
        destdir = QFileDialog.getExistingDirectory(self,"Descargar",
            "/home",
            QFileDialog.ShowDirsOnly
            | QFileDialog.DontResolveSymlinks)
        self.lineEdit_input.setText(dir)# just for test
        #now the code for downloading the file
        if destdir:
            info=DownloadInfo()
            dialog=DownDialog(parent=self,info=info)
            dialog.show()
            self.broker.connection.Download(os.path.join(self.selected_touple[3],
                self.selected_touple[0]),
                self.selected_touple[2],destdir,info)

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