import time
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import random
from PyQt5.QtGui import QFont



class losedialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(150, 80, 131, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.okbutton = QtWidgets.QPushButton(Dialog)
        self.okbutton.setGeometry(QtCore.QRect(160, 200, 93, 28))
        self.okbutton.setObjectName("okbutton")
        self.okbutton.clicked.connect(self.back)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "You Lose"))
        self.okbutton.setText(_translate("Dialog", "Ok"))

    def back(self):
        # MainWindow2.close()
        # MainWindow4.close()
        # MainWindow.show()
        
        print("h")