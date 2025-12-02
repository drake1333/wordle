from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
import config  # CHANGED: Import entire module
from database import authenticate_user, register_user
from utils import refresh_daily_button_state

class LoginUI(object):
    def __init__(self, window_refs, main_ui_instance):
        self.DialogWindowLogin = window_refs["login"]
        self.MainWindowMain = window_refs["main"]
        self.SignupWindow = window_refs["signup"]
        self.main_ui_instance = main_ui_instance

    def setupUi(self, Dialog):
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(420, 420)
        
        self.title = QtWidgets.QLabel(Dialog); self.title.setGeometry(QtCore.QRect(150, 30, 140, 60)); f=QFont(); f.setPointSize(20); f.setBold(True); self.title.setFont(f); self.title.setText("Log-In")
        
        self.groupBox = QtWidgets.QGroupBox(Dialog); self.groupBox.setGeometry(QtCore.QRect(80, 110, 260, 250))
        
        self.lbl_user = QtWidgets.QLabel(self.groupBox); self.lbl_user.setGeometry(QtCore.QRect(20, 12, 100, 16)); self.lbl_user.setText("Username:")
        self.user_edit = QtWidgets.QLineEdit(self.groupBox); self.user_edit.setGeometry(QtCore.QRect(20, 30, 220, 34))
        
        self.lbl_pw = QtWidgets.QLabel(self.groupBox); self.lbl_pw.setGeometry(QtCore.QRect(20, 72, 100, 16)); self.lbl_pw.setText("Password:")
        self.pw_edit = QtWidgets.QLineEdit(self.groupBox); self.pw_edit.setGeometry(QtCore.QRect(20, 90, 220, 34)); self.pw_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.login_btn = QtWidgets.QPushButton(self.groupBox); self.login_btn.setGeometry(QtCore.QRect(80, 150, 100, 34)); self.login_btn.setText("LOGIN"); self.login_btn.clicked.connect(self.login_check)
        
        self.label_signup = QtWidgets.QLabel(self.groupBox); self.label_signup.setGeometry(QtCore.QRect(60, 190, 140, 20)); self.label_signup.setText("<a href='#'>Sign-up</a>"); self.label_signup.setAlignment(Qt.AlignCenter)
        self.label_signup.setOpenExternalLinks(False)
        self.label_signup.linkActivated.connect(self.open_signup)

    def login_check(self):
        username = self.user_edit.text().strip()
        password = self.pw_edit.text()
        
        if username == "" or password == "":
            QMessageBox.warning(None, "Error", "Please enter username and password")
            return
            
        if authenticate_user(username, password):
            # CHANGED: Update the actual config module variable
            config.CURRENT_USER = username
            refresh_daily_button_state(self.main_ui_instance)
            try:
                self.DialogWindowLogin.hide()
                self.MainWindowMain.show()
            except Exception:
                pass
        else:
            QMessageBox.warning(None, "Error", "Invalid username or password")

    def open_signup(self, *args):
        try:
            self.DialogWindowLogin.hide()
            self.SignupWindow.show()
        except Exception:
            pass

class SignupUI(object):
    def __init__(self, window_refs):
        self.DialogWindowLogin = window_refs["login"]
        self.SignupWindow = window_refs["signup"]

    def setupUi(self, Dialog):
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(420, 460)
        
        self.title = QtWidgets.QLabel(Dialog); self.title.setGeometry(QtCore.QRect(160, 20, 120, 40)); f = QFont(); f.setPointSize(20); f.setBold(True); self.title.setFont(f); self.title.setText("Sign-Up")
        self.groupBox = QtWidgets.QGroupBox(Dialog); self.groupBox.setGeometry(QtCore.QRect(60, 80, 300, 300))
        
        self.lbl_user = QtWidgets.QLabel(self.groupBox); self.lbl_user.setGeometry(QtCore.QRect(20, 20, 100, 16)); self.lbl_user.setText("Username:")
        self.user_edit = QtWidgets.QLineEdit(self.groupBox); self.user_edit.setGeometry(QtCore.QRect(20, 40, 260, 34))
        
        self.lbl_pw = QtWidgets.QLabel(self.groupBox); self.lbl_pw.setGeometry(QtCore.QRect(20, 82, 100, 16)); self.lbl_pw.setText("Password:")
        self.pw_edit = QtWidgets.QLineEdit(self.groupBox); self.pw_edit.setGeometry(QtCore.QRect(20, 102, 260, 34)); self.pw_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.lbl_confirm = QtWidgets.QLabel(self.groupBox); self.lbl_confirm.setGeometry(QtCore.QRect(20, 144, 140, 16)); self.lbl_confirm.setText("Confirm Password:")
        self.pw_confirm = QtWidgets.QLineEdit(self.groupBox); self.pw_confirm.setGeometry(QtCore.QRect(20, 164, 260, 34)); self.pw_confirm.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.signup_btn = QtWidgets.QPushButton(self.groupBox); self.signup_btn.setGeometry(QtCore.QRect(60, 210, 80, 34)); self.signup_btn.setText("Sign-up"); self.signup_btn.clicked.connect(self.save_user)
        self.cancel_btn = QtWidgets.QPushButton(self.groupBox); self.cancel_btn.setGeometry(QtCore.QRect(160, 210, 80, 34)); self.cancel_btn.setText("Cancel"); self.cancel_btn.clicked.connect(self.back_to_login)

    def save_user(self):
        username = self.user_edit.text().strip()
        password = self.pw_edit.text()
        confirm = self.pw_confirm.text()
        
        if username == "" or password == "" or confirm == "":
            QMessageBox.warning(None, "Error", "All fields are required.")
            return
        if password != confirm:
            QMessageBox.warning(None, "Error", "Passwords do not match.")
            return
            
        success, message = register_user(username, password)
        
        if success:
            QMessageBox.information(None, "Success", message)
            self.SignupWindow.hide()
            self.DialogWindowLogin.show()
        else:
            QMessageBox.warning(None, "Error", message)

    def back_to_login(self):
        try:
            self.SignupWindow.hide()
            self.DialogWindowLogin.show()
        except Exception:
            pass