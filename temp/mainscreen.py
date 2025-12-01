import time
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import random
from PyQt5.QtGui import QFont





class mainwindow(object):
    def __init__(self):
        self.window = None
        
    def setupUi(self, MainWindow):
        self.window = mainwindow
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(603, 631)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(230, 390, 141, 41))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.statistic)
        
        
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(230, 470, 141, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.exit)
        
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(240, 200, 141, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(220, 80, 291, 61))
        font = QtGui.QFont()
        font.setPointSize(28)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        
        
        
        self.label_23 = QtWidgets.QLabel(self.centralwidget)
        self.label_23.setGeometry(QtCore.QRect(70, 10, 121, 31))
        self.label_23.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_23.setFrameShape(QtWidgets.QFrame.Box)
        self.label_23.setLineWidth(1)
        self.label_23.setText("")
        self.label_23.setObjectName("label_2")
        
        
        start = time.time()
        local_time = time.ctime(start)
        self.label_23.setText(local_time)
        
        
        
        
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(230, 320, 141, 41))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.text)
        
        
        
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(180, 240, 241, 41))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("4 Word wordle")
        self.comboBox.addItem("5 Word wordle")
        self.comboBox.addItem("6 Word wordle")
        self.comboBox.setItemText(3, "")
        text = str(self.comboBox.currentText())
       
        
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 603, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "PRoFILE / STATISTIC"))
        self.pushButton_2.setText(_translate("MainWindow", "EXIT"))
        self.label.setText(_translate("MainWindow", "DIFFICULTY"))
        self.label_2.setText(_translate("MainWindow", "WORDLE"))
        self.pushButton_3.setText(_translate("MainWindow", "PLAY"))
     
        
    
    def exit(self):
        exit()
        
    def statistic(self):
        # MainWindow.close()
        # MainWindow3.show()
        print("h")
    def text(self):
        gg = (self.comboBox.currentText())
        if gg == "5 Word wordle":
            
            self.window.close()
            # MainWindow4.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
   
    ui = mainwindow()
    ui2 = losedialog()
    ui3 =  statistic()
    ui4 =                           ()
    
    
    MainWindow1 = QtWidgets.QMainWindow()
    MainWindow3 = QtWidgets.QMainWindow()
    MainWindow4 = QtWidgets.QMainWindow()
    MainWindow2 = QtWidgets.QMainWindow()
    
    ui3.setupUi(MainWindow3)
    ui2.setupUi(MainWindow2)
    ui.setupUi(MainWindow1)
    ui4.setupUi(MainWindow4)
    
    MainWindow1.show()
    sys.exit(app.exec_())
    
