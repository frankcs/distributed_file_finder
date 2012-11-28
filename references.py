__author__ = 'Frank'

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QTableWidgetItem
from PyQt4.QtGui import QColor

from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from designer_generated_ui.about import Ui_Dialog_about
from designer_generated_ui.options import Ui_Dialog
from designer_generated_ui.searcher import Ui_MainWindow
from data.db_module import db_manager
from data.sentry import octopus_handler,Observer,sys
from PyQt4 import QtCore,QtGui
from os import path
