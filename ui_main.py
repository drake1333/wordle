from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox, QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout
import config  
from utils import load_options, save_options, apply_options

class MainWindowUI(object):
    def __init__(self, window_refs, main_ui_instance):
        self.MainWindowMain = window_refs["main"]
        self.MainWindow4 = window_refs["4"]
        self.MainWindow5 = window_refs["5"]
        self.MainWindow6 = window_refs["6"]
        self.MainWindowDaily = window_refs["daily"]
        self.MainWindowStat = window_refs["stat"]
        
        self.ui4 = window_refs["ui4"]
        self.ui5 = window_refs["ui5"]
        self.ui6 = window_refs["ui6"]
        self.uiDaily = window_refs["uiDaily"]
        self.uiStat = window_refs["uiStat"]
        self.main_ui_instance = main_ui_instance

    def setupUi(self, MainWindow):
        self.window = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(620, 620)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(220, 30, 280, 60))
        f = QFont(); f.setPointSize(28); f.setBold(True); self.title.setFont(f); self.title.setText("PyWordle")
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(250, 110, 140, 20))
        f2 = QFont(); f2.setPointSize(12); self.label.setFont(f2); self.label.setText("DIFFICULTY")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(180, 140, 260, 36))
        self.comboBox.addItems(["4 Word wordle","5 Word wordle","6 Word wordle"])
        
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(220, 200, 180, 340))
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        
        self.pushButton_4 = QtWidgets.QPushButton(self.widget); self.pushButton_4.setText("PLAY"); self.pushButton_4.clicked.connect(self.play_clicked); self.gridLayout.addWidget(self.pushButton_4,0,0)
        self.pushButton_3 = QtWidgets.QPushButton(self.widget); self.pushButton_3.setText("DAILY WORD"); self.pushButton_3.clicked.connect(self.daily_clicked); self.gridLayout.addWidget(self.pushButton_3,1,0)
        self.pushButton_stat = QtWidgets.QPushButton(self.widget); self.pushButton_stat.setText("STATISTIC"); self.pushButton_stat.clicked.connect(self.statistic_clicked); self.gridLayout.addWidget(self.pushButton_stat,2,0)
        self.pushButton_opt = QtWidgets.QPushButton(self.widget); self.pushButton_opt.setText("OPTIONS"); self.pushButton_opt.clicked.connect(self.options_clicked); self.gridLayout.addWidget(self.pushButton_opt,3,0)
        self.pushButton_exit = QtWidgets.QPushButton(self.widget); self.pushButton_exit.setText("EXIT"); self.pushButton_exit.clicked.connect(QtWidgets.qApp.quit); self.gridLayout.addWidget(self.pushButton_exit,4,0)
        
        MainWindow.setCentralWidget(self.centralwidget)

    def play_clicked(self):
        sel = self.comboBox.currentText()
        try:
            self.MainWindowMain.hide()
            if sel.startswith("4"):
                self.ui4.__init__()
                self.ui4.setupUi(self.MainWindow4, self.MainWindowMain)
                self.MainWindow4.show()
            elif sel.startswith("5"):
                self.ui5.__init__()
                self.ui5.setupUi(self.MainWindow5, self.MainWindowMain)
                self.MainWindow5.show()
            else:
                self.ui6.__init__()
                self.ui6.setupUi(self.MainWindow6, self.MainWindowMain)
                self.MainWindow6.show()
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not open game: {e}")

    def daily_clicked(self):
        if not config.CURRENT_USER:
             QMessageBox.warning(None, "Error", "You must be logged in to play the Daily Word.")
             return
             
        try:
            self.MainWindowMain.hide()
            self.uiDaily.__init__()
            self.uiDaily.setupUi(self.MainWindowDaily, self.MainWindowMain, self.main_ui_instance)
            self.MainWindowDaily.show()
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not open daily: {e}")

    def statistic_clicked(self):
        try:
            self.MainWindowMain.hide()
            self.uiStat.load_stats()
            self.MainWindowStat.show()
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not open statistics: {e}")

    def options_clicked(self):
        opts = load_options()
        dlg = QDialog()
        dlg.setWindowTitle("Options")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Select Theme:"))
        theme_combo = QComboBox(); theme_combo.addItems(["Light","Dark","Blue"]); theme_combo.setCurrentText(opts.get("theme","Light"))
        layout.addWidget(theme_combo)
        
        layout.addWidget(QLabel("Select Font:"))
        font_combo = QComboBox(); font_combo.addItems(["Default","Arial","Courier New"]); font_combo.setCurrentText(opts.get("font","Default"))
        layout.addWidget(font_combo)
        
        row = QtWidgets.QHBoxLayout()
        apply_btn = QPushButton("Apply"); close_btn = QPushButton("Close")
        row.addWidget(apply_btn); row.addWidget(close_btn)
        layout.addLayout(row)
        dlg.setLayout(layout)
        
        def do_apply():
            new_opts = {"theme": theme_combo.currentText(), "font": font_combo.currentText()}
            save_options(new_opts)
            apply_options(new_opts)
            QMessageBox.information(dlg, "Options","Options applied")
            
        apply_btn.clicked.connect(do_apply)
        close_btn.clicked.connect(dlg.close)
        dlg.exec_()