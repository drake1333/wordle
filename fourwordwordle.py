import time
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import random
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

import enchant
dictionary = {
    1: ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d"],
    2:  ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m"],
    3:  ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n"],
    4:  ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s"],
    5:  ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x"]
        
}



class fourwordwordle(object):
    def __init__(self):
        self.counter = 0
        self.winstreak =0
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(834, 499)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 40, 61, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.back)
        
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(370, 400, 61, 31))
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.clicked.connect(self.next)
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(330, 50, 55, 16))
        self.label.setText(self.randomword())
        self.label.setObjectName("label")
        self.winstreak2 = QtWidgets.QLabel(self.centralwidget)
        self.winstreak2.setGeometry(QtCore.QRect(160, 40, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.winstreak2.setFont(font)
        self.winstreak2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.winstreak2.setText(str(self.winstreak))
        self.winstreak2.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.winstreak2.setObjectName("winstreak2")
        
        self.Winstreak = QtWidgets.QLabel(self.centralwidget)
        self.Winstreak.setGeometry(QtCore.QRect(80, 40, 81, 21))
        
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Winstreak.setFont(font)
        self.Winstreak.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.Winstreak.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.Winstreak.setObjectName("Winstreak")
        
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(40, 110, 761, 271))
        self.widget.setObjectName("widget")
        
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        
        regex = QRegExp("^[a-zA-Z]+$")
        validator = QRegExpValidator(regex)
        self.lineEdit_a = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_a.setObjectName("lineEdit_a")
        self.lineEdit_a.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_a, 0, 0, 1, 1)
        self.lineEdit_a.setValidator(validator)
        self.lineEdit_a.textChanged.connect(self.change)
         
        self.lineEdit_b = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_b.setObjectName("lineEdit_b")
        self.lineEdit_b.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_b, 0, 1, 1, 1)
        self.lineEdit_b.setValidator(validator)
        self.lineEdit_b.textChanged.connect(self.change)
        
        self.lineEdit_c = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_c.setObjectName("lineEdit_c")
        self.lineEdit_c.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_c, 0, 2, 1, 1)
        self.lineEdit_c.setValidator(validator)
        self.lineEdit_c.textChanged.connect(self.change)
        
        self.lineEdit_d = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_d.setObjectName("lineEdit_d")
        self.gridLayout.addWidget(self.lineEdit_d, 0, 3, 1, 1)
        self.lineEdit_d.setMaxLength(1)
        self.lineEdit_d.setValidator(validator)
        self.lineEdit_d.textChanged.connect(self.change)
        self.lineEdit_d.returnPressed.connect(self.enter)
       
        
        self.lineEdit_f = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_f.setObjectName("lineEdit_f")
        self.lineEdit_f.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_f, 1, 0, 1, 1)
        self.lineEdit_f.setValidator(validator)
        self.lineEdit_f.textChanged.connect(self.change)
        
        self.lineEdit_g = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_g.setObjectName("lineEdit_g")
        self.lineEdit_g.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_g, 1, 1, 1, 1)
        self.lineEdit_g.setValidator(validator)
        self.lineEdit_g.textChanged.connect(self.change)
        
        self.lineEdit_h = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_h.setObjectName("lineEdit_h")
        self.lineEdit_h.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_h, 1, 2, 1, 1)
        self.lineEdit_h.setValidator(validator)
        self.lineEdit_h.textChanged.connect(self.change)
        
        self.lineEdit_m = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_m.setObjectName("lineEdit_m")
        self.lineEdit_m.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_m, 1, 3, 1, 1)
        self.lineEdit_m.setValidator(validator)
        self.lineEdit_m.textChanged.connect(self.change)
        self.lineEdit_m.returnPressed.connect(self.enter)
       
        
        self.lineEdit_j = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_j.setObjectName("lineEdit_j")
        self.lineEdit_j.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_j, 2, 0, 1, 1)
        self.lineEdit_j.setValidator(validator)
        self.lineEdit_j.textChanged.connect(self.change)
        
        self.lineEdit_k = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_k.setObjectName("lineEdit_k")
        self.lineEdit_k.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_k, 2, 1, 1, 1)
        self.lineEdit_k.setValidator(validator)
        self.lineEdit_k.textChanged.connect(self.change)
        
        self.lineEdit_l = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_l.setObjectName("lineEdit_l")
        self.lineEdit_l.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_l, 2, 2, 1, 1)
        self.lineEdit_l.setValidator(validator)
        self.lineEdit_l.textChanged.connect(self.change)
        
        self.lineEdit_n = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_n.setObjectName("lineEdit_n")
        self.lineEdit_n.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_n, 2, 3, 1, 1)
        self.lineEdit_n.setValidator(validator)
        self.lineEdit_n.textChanged.connect(self.change)
        self.lineEdit_n.returnPressed.connect(self.enter)
        
        
        self.lineEdit_p = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_p.setObjectName("lineEdit_p")
        self.lineEdit_p.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_p, 3, 0, 1, 1)
        self.lineEdit_p.setValidator(validator)
        self.lineEdit_p.textChanged.connect(self.change)
        
        self.lineEdit_q = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_q.setObjectName("lineEdit_q")
        self.lineEdit_q.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_q, 3, 1, 1, 1)
        self.lineEdit_q.setValidator(validator)
        self.lineEdit_q.textChanged.connect(self.change)
        
        self.lineEdit_r = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_r.setObjectName("lineEdit_r")
        self.lineEdit_r.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_r, 3, 2, 1, 1)
        self.lineEdit_r.setValidator(validator)
        self.lineEdit_r.textChanged.connect(self.change)
        
        self.lineEdit_s = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_s.setObjectName("lineEdit_s")
        self.lineEdit_s.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_s, 3, 3, 1, 1)
        self.lineEdit_s.setValidator(validator)
        self.lineEdit_s.textChanged.connect(self.change)
        self.lineEdit_s.returnPressed.connect(self.enter)
       
        
        self.lineEdit_u = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_u.setObjectName("lineEdit_u")
        self.lineEdit_u.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_u, 4, 0, 1, 1)
        self.lineEdit_u.setValidator(validator)
        self.lineEdit_u.textChanged.connect(self.change)
        
        self.lineEdit_v = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_v.setObjectName("lineEdit_v")
        self.lineEdit_v.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_v, 4, 1, 1, 1)
        self.lineEdit_v.setValidator(validator)
        self.lineEdit_v.textChanged.connect(self.change)
        
        self.lineEdit_w = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_w.setObjectName("lineEdit_w")
        self.lineEdit_w.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_w, 4, 2, 1, 1)
        self.lineEdit_w.setValidator(validator)
        self.lineEdit_w.textChanged.connect(self.change)
        
        self.lineEdit_x = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_x.setObjectName("lineEdit_x")
        self.lineEdit_x.setMaxLength(1)
        self.gridLayout.addWidget(self.lineEdit_x, 4, 3, 1, 1)
        self.lineEdit_x.setValidator(validator)
        self.lineEdit_x.textChanged.connect(self.change)
        self.lineEdit_x.returnPressed.connect(self.enter)
        
        
        self.gridLayout.addWidget(self.lineEdit_x, 4, 3, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 834, 26))
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
        self.pushButton.setText(_translate("MainWindow", "Back"))
        self.pushButton_2.setText(_translate("MainWindow", "Next"))
        self.Winstreak.setText(_translate("MainWindow", "WinStreak:"))
        
    def randomword(self):
        with open ("4-wordsource.txt", "r") as file:
            t = random.randrange(1, 50)
            uu = file.readlines()[t]
            e = str(uu.upper().strip())
            return e
    
    def change(self,text):
        letterbox = QtWidgets.QDialog()
        letter = letterbox.sender()
        letter.setText(text.upper())
   
    def enter(self):
        d = enchant.Dict("en_US")
        self.counter += 1
        g = dictionary[self.counter]
        a = []
        j = 0
        e = self.label.text()
        for xx in g:
            widget= getattr(self,xx)
            oo = widget.text() 
            a.append(oo)
            
        if "" in a:
            self.notenoughletter()
            return 
        
        p = "".join(a)
        
        if not d.check(p):
            self.notaword()
            return
        
        for x in range(4):
                y = getattr(self,g[x])
                y.setReadOnly(True)
                if e[x] == a[x]:
                    y.setStyleSheet("background-color: rgb(0, 170, 0);")
                    j +=1
                    
                elif a[x] in e:
                    y.setStyleSheet("background-color: rgb(255, 255, 0);")
                    
                else:
                    y.setStyleSheet("background-color: rgb(255, 0, 0);")   
                    
                if j ==4:
                    self.pushButton_2.setEnabled(True)
                    
        
        if self.counter == 4:
            self.losedialogbox()
    
    def  notaword(self):
        letterbox = QtWidgets.QMessageBox()
        letterbox.setWindowTitle("lose")
        letterbox.setText("invalid word")
        letterbox.exec_()
        
        g = dictionary[self.counter]
        for x in g:
            widget= getattr(self,x)
            widget.clear()
        self.counter -=1    
    
    def next( self):
        self.winstreak += 1
        self.counter = 0
        ui5.setupUi(MainWindow5)
        MainWindow5.show()
        
    def  notenoughletter(self):
        letterbox = QtWidgets.QMessageBox()
        letterbox.setWindowTitle("lose")
        letterbox.setText("Not enough letter")
        letterbox.exec_()
       
        g = dictionary[self.counter]
        for x in g:
            widget= getattr(self,x)
            widget.clear()
        self.counter -=1
            
    def losedialogbox(self):
        losebox = QtWidgets.QMessageBox()
        losebox.setWindowTitle("lose")
        losebox.setText("You lose")
        losebox.exec_()
        losebox.clickedButton(self.hidewindow())
    
    def hidewindow(self):
        MainWindow5.hide()
            
    def back(self):
        # MainWindow4.close()
        # MainWindow.show()
        print("j")
    

    
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # ui = mainwindow()
    # ui2 = losedialog()
    # ui3 =  statistic()
    ui5 = fourwordwordle()


    # MainWindow1 = QtWidgets.QMainWindow()
    # MainWindow3 = QtWidgets.QMainWindow()
    MainWindow5 = QtWidgets.QMainWindow()
    # MainWindow2 = QtWidgets.QMainWindow()

    # ui3.setupUi(MainWindow3)
    # ui2.setupUi(MainWindow2)
    # ui.setupUi(MainWindow1)
    ui5.setupUi(MainWindow5)

    MainWindow5.show()
    sys.exit(app.exec_())