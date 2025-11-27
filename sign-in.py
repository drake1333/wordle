from PyQt5 import QtCore, QtGui, QtWidgets
from database import get_db
import sqlite3


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        self.Dialog = Dialog  # store reference

        Dialog.setObjectName("Dialog")
        Dialog.resize(459, 450)

        # --- UI Elements (unchanged) ---
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(190, 70, 111, 61))
        self.label.setStyleSheet("font: 18pt \"MS Shell Dlg 2\";")
        self.label.setObjectName("label")

        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(120, 140, 241, 251))
        self.groupBox.setAutoFillBackground(True)
        self.groupBox.setTitle("")

        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setGeometry(QtCore.QRect(10, 30, 221, 31))
        self.lineEdit.setObjectName("lineEdit")

        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_2.setGeometry(QtCore.QRect(10, 100, 221, 31))
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)

        self.lineEdit_5 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_5.setGeometry(QtCore.QRect(10, 170, 221, 31))
        self.lineEdit_5.setEchoMode(QtWidgets.QLineEdit.Password)

        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(10, 80, 55, 16))

        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(10, 0, 71, 16))

        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(10, 150, 111, 16))

        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(80, 220, 93, 28))
        self.pushButton.clicked.connect(self.save_user)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    # -------------------------------
    #       SAVE TO DATABASE
    # -------------------------------
    def save_user(self):
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        confirm = self.lineEdit_5.text()

        if username == "" or password == "" or confirm == "":
            self.show_msg("All fields are required.")
            return

        if password != confirm:
            self.show_msg("Passwords do not match.")
            return

        conn, cursor = get_db()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                           (username, password))
            conn.commit()
            self.show_msg("Account created successfully!")
            self.Dialog.close()

        except sqlite3.IntegrityError:
            self.show_msg("Username already exists.")

        finally:
            conn.close()

    def show_msg(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Message")
        msg.setText(text)
        msg.exec_()

    # -------------------------------

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Sign-Up"))
        self.label_2.setText(_translate("Dialog", "Password:"))
        self.label_3.setText(_translate("Dialog", "Username:"))
        self.pushButton.setText(_translate("Dialog", "Sign-up"))
        self.label_5.setText(_translate("Dialog", "Confirm Password:"))
