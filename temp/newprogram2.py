# newprogram.py - part 1/3
# Combined app with fixes: winstreak labels on all modes, signup/login flow, daily once-per-day, visible UI text.

import sys
import os
import sqlite3
import random
import json
import time
from datetime import date
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QFont
from PyQt5.QtWidgets import QMessageBox, QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout

# Spell check library; if not installed some functionality will still run
try:
    import enchant
except Exception:
    enchant = None

# Try to import user's database helper; fallback to internal sqlite
try:
    from database import get_db
except Exception:
    def get_db():
        dbfile = "appdata.db"
        conn = sqlite3.connect(dbfile)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                          username TEXT PRIMARY KEY,
                          password TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS statistics (
                          username TEXT PRIMARY KEY,
                          wins INTEGER DEFAULT 0,
                          losses INTEGER DEFAULT 0,
                          winstreak INTEGER DEFAULT 0,
                          last_daily_play TEXT
                          )""")
        conn.commit()
        return conn, cursor

# global current user
CURRENT_USER = None

# options file
OPTIONS_FILE = "options.json"
DEFAULT_OPTIONS = {"theme": "Light", "font": "Default"}

def ensure_statistics_table():
    conn, cursor = get_db()
    cursor.execute("""CREATE TABLE IF NOT EXISTS statistics (
                      username TEXT PRIMARY KEY,
                      wins INTEGER DEFAULT 0,
                      losses INTEGER DEFAULT 0,
                      winstreak INTEGER DEFAULT 0,
                      last_daily_play TEXT
                      )""")
    conn.commit()
    # ensure columns exist (safe)
    cursor.execute("PRAGMA table_info(statistics)")
    cols = [r[1] for r in cursor.fetchall()]
    if "winstreak" not in cols:
        try:
            cursor.execute("ALTER TABLE statistics ADD COLUMN winstreak INTEGER DEFAULT 0")
        except Exception:
            pass
    if "last_daily_play" not in cols:
        try:
            cursor.execute("ALTER TABLE statistics ADD COLUMN last_daily_play TEXT")
        except Exception:
            pass
    conn.commit()
    conn.close()

ensure_statistics_table()

# dictionaries to map lineEdit object names for each attempt/row
dictionary4 = {
    1: ["lineEdit_a", "lineEdit_b", "lineEdit_c", "lineEdit_d", "lineEdit_e", "lineEdit_za"],
    2: ["lineEdit_f", "lineEdit_g", "lineEdit_h", "lineEdit_m", "lineEdit_i", "lineEdit_zb"],
    3: ["lineEdit_j", "lineEdit_k", "lineEdit_l", "lineEdit_n", "lineEdit_o", "lineEdit_zc"],
    4: ["lineEdit_p", "lineEdit_q", "lineEdit_r", "lineEdit_s", "lineEdit_t", "lineEdit_zd"],
    5: ["lineEdit_u", "lineEdit_v", "lineEdit_w", "lineEdit_x", "lineEdit_y", "lineEdit_z"]
}
# 5-letter mapping
dictionary5 = {
    1: ["lineEdit_a", "lineEdit_b", "lineEdit_c", "lineEdit_d", "lineEdit_e"],
    2: ["lineEdit_f", "lineEdit_g", "lineEdit_h", "lineEdit_m", "lineEdit_i"],
    3: ["lineEdit_j", "lineEdit_k", "lineEdit_l", "lineEdit_n", "lineEdit_o"],
    4: ["lineEdit_p", "lineEdit_q", "lineEdit_r", "lineEdit_s", "lineEdit_t"],
    5: ["lineEdit_u", "lineEdit_v", "lineEdit_w", "lineEdit_x", "lineEdit_y"]
}
# 4-letter mapping
dictionary4col = {
    1: ["lineEdit_a", "lineEdit_b", "lineEdit_c", "lineEdit_d"],
    2: ["lineEdit_f", "lineEdit_g", "lineEdit_h", "lineEdit_m"],
    3: ["lineEdit_j", "lineEdit_k", "lineEdit_l", "lineEdit_n"],
    4: ["lineEdit_p", "lineEdit_q", "lineEdit_r", "lineEdit_s"],
    5: ["lineEdit_u", "lineEdit_v", "lineEdit_w", "lineEdit_x"]
}

# --- Database helper functions ---
def update_stats_db(username, win: bool, set_last_daily_play=False, increment_winstreak_on_win=True):
    """Update stats: wins/losses and winstreak. Optionally set last_daily_play to today."""
    if not username:
        return False
    conn, cursor = get_db()
    cursor.execute("SELECT wins, losses, winstreak FROM statistics WHERE username=?", (username,))
    r = cursor.fetchone()
    if r:
        wins, losses, winstreak = r
        if win:
            cursor.execute("UPDATE statistics SET wins = wins + 1 WHERE username=?", (username,))
            if increment_winstreak_on_win:
                cursor.execute("UPDATE statistics SET winstreak = winstreak + 1 WHERE username=?", (username,))
        else:
            cursor.execute("UPDATE statistics SET losses = losses + 1 WHERE username=?", (username,))
            cursor.execute("UPDATE statistics SET winstreak = 0 WHERE username=?", (username,))
    else:
        if win:
            cursor.execute("INSERT INTO statistics (username, wins, losses, winstreak) VALUES (?, ?, ?, ?)",
                           (username, 1, 0, 1))
        else:
            cursor.execute("INSERT INTO statistics (username, wins, losses, winstreak) VALUES (?, ?, ?, ?)",
                           (username, 0, 1, 0))
    if set_last_daily_play:
        today = date.today().isoformat()
        cursor.execute("UPDATE statistics SET last_daily_play = ? WHERE username = ?", (today, username))
    conn.commit()
    conn.close()
    return True

def get_user_stats(username):
    if not username:
        return {"wins": 0, "losses": 0, "winstreak": 0, "last_daily_play": None}
    conn, cursor = get_db()
    cursor.execute("SELECT wins, losses, winstreak, last_daily_play FROM statistics WHERE username=?", (username,))
    r = cursor.fetchone()
    conn.close()
    if r:
        return {"wins": r[0] or 0, "losses": r[1] or 0, "winstreak": r[2] or 0, "last_daily_play": r[3]}
    return {"wins": 0, "losses": 0, "winstreak": 0, "last_daily_play": None}

def set_last_daily_play(username):
    if not username:
        return
    conn, cursor = get_db()
    today = date.today().isoformat()
    cursor.execute("UPDATE statistics SET last_daily_play = ? WHERE username = ?", (today, username))
    conn.commit()
    conn.close()

def can_play_daily(username):
    if not username:
        return False
    stats = get_user_stats(username)
    last = stats.get("last_daily_play")
    today = date.today().isoformat()
    return last != today

# --- Options functions ---
def load_options():
    if os.path.exists(OPTIONS_FILE):
        try:
            with open(OPTIONS_FILE, "r", encoding="utf-8") as fh:
                opts = json.load(fh)
                return {**DEFAULT_OPTIONS, **opts}
        except Exception:
            return DEFAULT_OPTIONS.copy()
    return DEFAULT_OPTIONS.copy()

def save_options(opts):
    try:
        with open(OPTIONS_FILE, "w", encoding="utf-8") as fh:
            json.dump(opts, fh)
            return True
    except Exception:
        return False

def apply_options(options):
    app = QtWidgets.QApplication.instance()
    if not app:
        return
    theme = options.get("theme", "Light")
    font_choice = options.get("font", "Default")
    if theme == "Dark":
        ss = """
        QWidget { background-color: #2b2b2b; color: #e6e6e6; }
        QLineEdit { background-color: #3a3a3a; color: #e6e6e6; }
        QPushButton { background-color: #444444; color: #e6e6e6; }
        """
    elif theme == "Blue":
        ss = """
        QWidget { background-color: #eaf6ff; color: #0a2540; }
        QLineEdit { background-color: #ffffff; color: #0a2540; }
        QPushButton { background-color: #d0ecff; color: #0a2540; }
        """
    else:
        ss = ""
    app.setStyleSheet(ss)
    if font_choice == "Arial":
        app.setFont(QFont("Arial", 10))
    elif font_choice == "Courier New":
        app.setFont(QFont("Courier New", 10))
    else:
        app.setFont(QFont())

# --- Daily word deterministic selection ---
def daily_word_from_file(filepath="dailyword.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            lines = [ln.strip() for ln in fh if ln.strip()]
    except Exception:
        lines = []
    if not lines:
        return "PYTHON"
    idx = date.today().toordinal() % len(lines)
    return lines[idx].upper()

# --- UI helpers ---
def configure_letter_edit(le: QtWidgets.QLineEdit):
    le.setMaxLength(1)
    le.setAlignment(Qt.AlignCenter)
    font = QFont()
    font.setPointSize(14)
    le.setFont(font)
    # validator letters only
    regex = QRegExp("^[A-Za-z]?$")
    le.setValidator(QRegExpValidator(regex))
    # uppercase on change
    def on_text_changed(txt):
        if txt is None:
            return
        txtu = txt.upper()
        if le.text() != txtu:
            # block signals while setting to prevent recursion
            try:
                le.blockSignals(True)
                le.setText(txtu)
            finally:
                le.blockSignals(False)
    le.textChanged.connect(on_text_changed)

# --- Function to refresh MainWindow daily button state ---
def refresh_daily_button_state(ui_instance=None):
    # ui_instance is the mainwindow object (instance of mainwindow class)
    try:
        if CURRENT_USER:
            allowed = can_play_daily(CURRENT_USER)
            try:
                # try direct instance first
                if ui_instance and hasattr(ui_instance, "pushButton_3"):
                    ui_instance.pushButton_3.setEnabled(bool(allowed))
                else:
                    # fallback to global ui (if present)
                    try:
                        ui.pushButton_3.setEnabled(bool(allowed))
                    except Exception:
                        # last fallback: search by object name
                        btn = MainWindow1.findChild(QtWidgets.QPushButton, "pushButton_3")
                        if btn:
                            btn.setEnabled(bool(allowed))
            except Exception:
                pass
        else:
            # no user logged in -> disable daily
            try:
                if ui_instance and hasattr(ui_instance, "pushButton_3"):
                    ui_instance.pushButton_3.setEnabled(False)
                else:
                    ui.pushButton_3.setEnabled(False)
            except Exception:
                pass
    except Exception:
        pass

# ------------------------------------------------------------------------
# Begin UI classes
# ------------------------------------------------------------------------

class MainWindowUI(object):
    def __init__(self):
        pass

    def setupUi(self, MainWindow):
        self.window = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(603, 631)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # Title label
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(220, 40, 291, 61))
        f = QFont(); f.setPointSize(28); f.setBold(True)
        self.label_2.setFont(f)
        self.label_2.setText("WORDLE")
        # difficulty label
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(240, 130, 141, 16))
        f2 = QFont(); f2.setPointSize(12)
        self.label.setFont(f2)
        self.label.setText("DIFFICULTY")
        # Combo box
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(180, 160, 241, 41))
        self.comboBox.addItems(["4 Word wordle", "5 Word wordle", "6 Word wordle"])
        # Buttons region
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(220, 220, 171, 311))
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        # Play
        self.pushButton_4 = QtWidgets.QPushButton(self.widget)
        self.pushButton_4.setMaximumSize(QtCore.QSize(141, 41))
        self.pushButton_4.setText("PLAY")
        self.pushButton_4.clicked.connect(self.play_clicked)
        self.gridLayout.addWidget(self.pushButton_4, 0, 0, 1, 1)
        # Daily
        self.pushButton_3 = QtWidgets.QPushButton(self.widget)
        self.pushButton_3.setMaximumSize(QtCore.QSize(141, 41))
        self.pushButton_3.setText("DAILY WORD")
        self.pushButton_3.clicked.connect(self.daily_clicked)
        self.gridLayout.addWidget(self.pushButton_3, 1, 0, 1, 1)
        # Statistic
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setMaximumSize(QtCore.QSize(141, 41))
        self.pushButton.setText("STATISTIC")
        self.pushButton.clicked.connect(self.statistic_clicked)
        self.gridLayout.addWidget(self.pushButton, 2, 0, 1, 1)
        # Options
        self.pushButton_5 = QtWidgets.QPushButton(self.widget)
        self.pushButton_5.setMaximumSize(QtCore.QSize(141, 41))
        self.pushButton_5.setText("OPTIONS")
        self.pushButton_5.clicked.connect(self.options_clicked)
        self.gridLayout.addWidget(self.pushButton_5, 3, 0, 1, 1)
        # Exit
        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        self.pushButton_2.setMaximumSize(QtCore.QSize(141, 41))
        self.pushButton_2.setText("EXIT")
        self.pushButton_2.clicked.connect(QtWidgets.qApp.quit)
        self.gridLayout.addWidget(self.pushButton_2, 4, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

    def play_clicked(self):
        sel = self.comboBox.currentText()
        try:
            MainWindow1.hide()
            if sel.startswith("4"):
                ui4.setupUi(MainWindow4)
                MainWindow4.show()
            elif sel.startswith("5"):
                ui5.setupUi(MainWindow5)
                MainWindow5.show()
            else:
                ui6.setupUi(MainWindow6)
                MainWindow6.show()
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Couldn't open game: {e}")

    def daily_clicked(self):
        try:
            MainWindow1.hide()
            uiDaily.setupUi(MainwindowDaily)
            MainwindowDaily.show()
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Couldn't open Daily: {e}")

    def statistic_clicked(self):
        try:
            MainWindow1.hide()
            uiStat.load_stats()
            MainWindowStat.show()
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Couldn't open Statistics: {e}")

    def options_clicked(self):
        opts = load_options()
        dlg = QDialog()
        dlg.setWindowTitle("Options")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Theme:"))
        theme_combo = QComboBox(); theme_combo.addItems(["Light", "Dark", "Blue"]); theme_combo.setCurrentText(opts.get("theme", "Light"))
        layout.addWidget(theme_combo)
        layout.addWidget(QLabel("Select Font:"))
        font_combo = QComboBox(); font_combo.addItems(["Default", "Arial", "Courier New"]); font_combo.setCurrentText(opts.get("font", "Default"))
        layout.addWidget(font_combo)
        btn_row = QtWidgets.QHBoxLayout()
        apply_btn = QPushButton("Apply"); close_btn = QPushButton("Close")
        btn_row.addWidget(apply_btn); btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)
        dlg.setLayout(layout)
        def do_apply():
            new_opts = {"theme": theme_combo.currentText(), "font": font_combo.currentText()}
            save_options(new_opts)
            apply_options(new_opts)
            QMessageBox.information(dlg, "Options", "Options applied.")
        apply_btn.clicked.connect(do_apply)
        close_btn.clicked.connect(dlg.close)
        dlg.exec_()
# newprogram.py - part 2/3
# Continued UI definitions and game logic

# --- Login / Signup UI ---
class LoginUI(object):
    def setupUi(self, Dialog):
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 420)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(150, 40, 120, 60))
        f = QFont(); f.setPointSize(20); f.setBold(True)
        self.label.setFont(f)
        self.label.setText("Log-In")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(70, 120, 260, 230))
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox); self.lineEdit.setGeometry(QtCore.QRect(20, 30, 220, 32))
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox); self.lineEdit_2.setGeometry(QtCore.QRect(20, 90, 220, 32)); self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.label_3 = QtWidgets.QLabel(self.groupBox); self.label_3.setGeometry(QtCore.QRect(20, 5, 90, 16)); self.label_3.setText("Username:")
        self.label_2 = QtWidgets.QLabel(self.groupBox); self.label_2.setGeometry(QtCore.QRect(20, 70, 90, 16)); self.label_2.setText("Password:")
        self.pushButton = QtWidgets.QPushButton(self.groupBox); self.pushButton.setGeometry(QtCore.QRect(80, 150, 100, 32)); self.pushButton.setText("LOGIN"); self.pushButton.clicked.connect(self.login_check)
        self.label_5 = QtWidgets.QLabel(self.groupBox); self.label_5.setGeometry(QtCore.QRect(80, 185, 100, 20)); self.label_5.setText("<a href='#'>Sign-up</a>")
        self.label_5.setOpenExternalLinks(False)
        self.label_5.linkActivated.connect(self.open_signup)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def login_check(self):
        global CURRENT_USER
        username = self.lineEdit.text().strip()
        password = self.lineEdit_2.text()
        if username == "" or password == "":
            QMessageBox.warning(None, "Error", "Please enter username and password")
            return
        conn, cursor = get_db()
        cursor.execute("SELECT username FROM users WHERE username=? AND password=?", (username, password))
        r = cursor.fetchone()
        conn.close()
        if r:
            CURRENT_USER = username
            # refresh daily button
            refresh_daily_button_state(ui)
            try:
                DialogWindowLogin.hide()
                MainWindow1.show()
            except Exception:
                pass
        else:
            QMessageBox.warning(None, "Error", "Invalid username or password")

    def open_signup(self, *args):
        try:
            DialogWindowLogin.hide()
            SignupWindow.show()
        except Exception:
            pass

class SignupUI(object):
    def setupUi(self, Dialog):
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(460, 480)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(180, 40, 140, 60)); f = QFont(); f.setPointSize(20); f.setBold(True); self.label.setFont(f); self.label.setText("Sign-Up")
        self.groupBox = QtWidgets.QGroupBox(Dialog); self.groupBox.setGeometry(QtCore.QRect(100, 120, 260, 280))
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox); self.lineEdit.setGeometry(QtCore.QRect(20, 30, 220, 32))
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox); self.lineEdit_2.setGeometry(QtCore.QRect(20, 80, 220, 32)); self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.groupBox); self.lineEdit_5.setGeometry(QtCore.QRect(20, 130, 220, 32)); self.lineEdit_5.setEchoMode(QtWidgets.QLineEdit.Password)
        self.label_3 = QtWidgets.QLabel(self.groupBox); self.label_3.setGeometry(QtCore.QRect(20, 5, 90, 16)); self.label_3.setText("Username:")
        self.label_2 = QtWidgets.QLabel(self.groupBox); self.label_2.setGeometry(QtCore.QRect(20, 55, 90, 16)); self.label_2.setText("Password:")
        self.label_5 = QtWidgets.QLabel(self.groupBox); self.label_5.setGeometry(QtCore.QRect(20, 105, 140, 16)); self.label_5.setText("Confirm Password:")
        self.pushButton = QtWidgets.QPushButton(self.groupBox); self.pushButton.setGeometry(QtCore.QRect(80, 190, 100, 32)); self.pushButton.setText("Sign-up"); self.pushButton.clicked.connect(self.save_user)
        self.backButton1 = QtWidgets.QPushButton(Dialog); self.backButton1.setGeometry(QtCore.QRect(20, 20, 60, 30)); self.backButton1.setText("Back"); self.backButton1.clicked.connect(self.back_to_login)

    def save_user(self):
        username = self.lineEdit.text().strip()
        password = self.lineEdit_2.text()
        confirm = self.lineEdit_5.text()
        if username == "" or password == "" or confirm == "":
            QMessageBox.warning(None, "Error", "All fields required.")
            return
        if password != confirm:
            QMessageBox.warning(None, "Error", "Passwords do not match.")
            return
        conn, cursor = get_db()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            # ensure statistics row exists
            cursor.execute("INSERT OR IGNORE INTO statistics (username, wins, losses, winstreak) VALUES (?, 0, 0, 0)", (username,))
            conn.commit()
            QMessageBox.information(None, "Success", "Account created successfully!")
            # go back to login screen
            SignupWindow.hide()
            DialogWindowLogin.show()
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "Error", "Username already exists.")
        finally:
            conn.close()

    def back_to_login(self):
        try:
            SignupWindow.hide()
            DialogWindowLogin.show()
        except Exception:
            pass

# --- Statistics window (no winstreak display) ---
class StatisticUI(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(620, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(20, 20, 581, 501))
        self.frame.setStyleSheet("background-color: #ffffff;")
        self.label = QtWidgets.QLabel(self.frame); self.label.setGeometry(QtCore.QRect(230, 10, 170, 40))
        f = QFont(); f.setPointSize(18); f.setBold(True); self.label.setFont(f); self.label.setText("Statistics")
        # labels
        self.label_name = QtWidgets.QLabel(self.frame); self.label_name.setGeometry(QtCore.QRect(40, 50, 300, 30)); self.label_name.setText("Name: ")
        self.label_uid = QtWidgets.QLabel(self.frame); self.label_uid.setGeometry(QtCore.QRect(40, 90, 300, 30)); self.label_uid.setText("UID: ")
        self.label_wins = QtWidgets.QLabel(self.frame); self.label_wins.setGeometry(QtCore.QRect(40, 130, 300, 30)); self.label_wins.setText("Wins: ")
        self.label_losses = QtWidgets.QLabel(self.frame); self.label_losses.setGeometry(QtCore.QRect(40, 170, 300, 30)); self.label_losses.setText("Lose: ")
        self.label_pct = QtWidgets.QLabel(self.frame); self.label_pct.setGeometry(QtCore.QRect(40, 210, 400, 30)); self.label_pct.setText("Win/Lose Percentage:")
        self.label_lastdaily = QtWidgets.QLabel(self.frame); self.label_lastdaily.setGeometry(QtCore.QRect(40, 250, 400, 30)); self.label_lastdaily.setText("Last Daily: ")
        MainWindow.setCentralWidget(self.centralwidget)
        # back button
        self.pushButton = QtWidgets.QPushButton(self.centralwidget); self.pushButton.setGeometry(QtCore.QRect(10, 40, 61, 31)); self.pushButton.setText("Back"); self.pushButton.clicked.connect(self.back)

    def back(self):
        try:
            MainWindowStat.hide()
            MainWindow1.show()
        except Exception:
            pass

    def load_stats(self):
        if not CURRENT_USER:
            QMessageBox.information(None, "No user", "No user logged in.")
            self.label_name.setText("Name: ")
            self.label_uid.setText("UID: ")
            self.label_wins.setText("Wins: ")
            self.label_losses.setText("Lose: ")
            self.label_pct.setText("Win/Lose Percentage:")
            self.label_lastdaily.setText("Last Daily: ")
            return
        stats = get_user_stats(CURRENT_USER)
        conn, cursor = get_db()
        cursor.execute("SELECT rowid FROM users WHERE username=?", (CURRENT_USER,))
        uid = cursor.fetchone()
        conn.close()
        self.label_name.setText(f"Name: {CURRENT_USER}")
        self.label_uid.setText(f"UID: {uid[0] if uid else 'N/A'}")
        wins = stats.get("wins", 0); losses = stats.get("losses", 0)
        self.label_wins.setText(f"Wins: {wins}"); self.label_losses.setText(f"Lose: {losses}")
        total = wins + losses
        pct = round(wins / total * 100, 2) if total > 0 else 0.0
        self.label_pct.setText(f"Win/Lose Percentage: {pct}%")
        self.label_lastdaily.setText(f"Last Daily: {stats.get('last_daily_play') or 'N/A'}")

# --- Game UI classes (4,5,6,daily). Each will include a winstreak label at top-right matching 5-letter placement. ---

class BaseWordle:
    """Utility base containing common helpers for building grids and checking words."""
    def __init__(self, letters_count):
        self.counter = 0
        self.winstreak = 0
        self.letters_count = letters_count
        self.max_attempts = 5
        self.english_dict = enchant.Dict("en_US") if enchant else None

    def check_word_valid(self, word):
        if not self.english_dict:
            # fallback: accept any all-alpha word of correct length
            return word.isalpha()
        return self.english_dict.check(word)

    def color_row_feedback(self, guess, target, widgets):
        # guess and target uppercase strings
        tlist = list(target)
        # first pass: exact matches
        result = [""] * len(guess)
        for i, ch in enumerate(guess):
            w = widgets[i]
            if ch == tlist[i]:
                w.setStyleSheet("background-color: rgb(0, 170, 0);")
                tlist[i] = None
                result[i] = "green"
        # second pass: present elsewhere
        for i, ch in enumerate(guess):
            w = widgets[i]
            if result[i] == "":
                if ch in tlist:
                    w.setStyleSheet("background-color: rgb(255, 255, 0);")
                    tlist[tlist.index(ch)] = None
                else:
                    w.setStyleSheet("background-color: rgb(255, 0, 0);")
# newprogram.py - part 3/3
# Continued: Implement 4-letter, 5-letter, 6-letter and Daily using BaseWordle

# --- 4-letter wordle UI ---
class FourWordle(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=4)

    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # title and winstreak (top-right)
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(320, 20, 200, 40))
        f = QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("4-Word Wordle")
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget)
        self.label_winstreak.setGeometry(QtCore.QRect(620, 20, 160, 24))
        fw = QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw)
        self.label_winstreak.setText(f"Winstreak: {get_user_stats(CURRENT_USER).get('winstreak',0)}")
        # grid
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(40, 80, 720, 360))
        self.grid = QtWidgets.QGridLayout(self.widget)
        # create 5 rows x 4 cols
        rows = [
            ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d"],
            ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m"],
            ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n"],
            ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s"],
            ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x"]
        ]
        for r, row in enumerate(rows):
            for c, name in enumerate(row):
                le = QtWidgets.QLineEdit(self.widget)
                configure_letter_edit(le)
                if c == len(row)-1:
                    le.returnPressed.connect(self.enter)
                setattr(self, name, le)
                self.grid.addWidget(le, r, c, 1, 1)
        # Next button and Back button
        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(340, 440, 120, 32)); self.next_btn.setText("Next"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.next_clicked)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20, 20, 80, 30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)

    def enter(self):
        # builds current attempt based on counter+1 mapping
        self.counter += 1
        g = dictionary4col.get(self.counter, [])
        guess_chars = []
        widgets = []
        for n in g:
            w = getattr(self, n, None)
            if w is None:
                guess_chars.append("")
            else:
                widgets.append(w)
                guess_chars.append(w.text().upper())
        if "" in guess_chars:
            QMessageBox.warning(None, "Not enough letters", "Not enough letters")
            self.counter = max(0, self.counter-1)
            return
        guess = "".join(guess_chars)
        target = self.get_target_word()
        if not self.check_word_valid(guess):
            QMessageBox.warning(None, "Invalid", "Not a valid word")
            self.counter = max(0, self.counter-1)
            return
        # color feedback
        self.color_row_feedback(guess, target, widgets)
        if guess == target:
            self.next_btn.setEnabled(True)
        if self.counter >= self.max_attempts and guess != target:
            # lost
            if CURRENT_USER:
                update_stats_db(CURRENT_USER, win=False, set_last_daily_play=False)
            QMessageBox.information(None, "Lose", f"You lose. The word was {target}")
            self.back_clicked()

    def get_target_word(self):
        # read 4-word file
        try:
            with open("4-wordsource.txt", "r", encoding="utf-8") as f:
                lines = [ln.strip().upper() for ln in f if ln.strip()]
        except Exception:
            lines = []
        if not lines:
            return "WORD"
        return random.choice(lines)

    def next_clicked(self):
        # user won and pressed Next — increment winstreak and stats
        if CURRENT_USER:
            update_stats_db(CURRENT_USER, win=True, set_last_daily_play=False)
        self.label_winstreak.setText(f"Winstreak: {get_user_stats(CURRENT_USER).get('winstreak',0)}")
        self.next_btn.setEnabled(False)
        # reset board for next game
        FourWordleUI = FourWordle()
        FourWordleUI.setupUi(MainWindow4)
        MainWindow4.show()

    def back_clicked(self):
        try:
            MainWindow4.hide()
            MainWindow1.show()
        except Exception:
            pass

# --- 5-letter wordle UI ---
class FiveWordle(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=5)

    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(320, 20, 200, 40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("5-Word Wordle")
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget); self.label_winstreak.setGeometry(QtCore.QRect(620, 20, 160, 24)); fw=QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw); self.label_winstreak.setText(f"Winstreak: {get_user_stats(CURRENT_USER).get('winstreak',0)}")
        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40, 80, 720, 360))
        self.grid = QtWidgets.QGridLayout(self.widget)
        rows = [
            ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e"],
            ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i"],
            ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o"],
            ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t"],
            ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y"]
        ]
        for r, row in enumerate(rows):
            for c, name in enumerate(row):
                le = QtWidgets.QLineEdit(self.widget)
                configure_letter_edit(le)
                if c == len(row)-1:
                    le.returnPressed.connect(self.enter)
                setattr(self, name, le)
                self.grid.addWidget(le, r, c, 1, 1)
        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(340, 440, 120, 32)); self.next_btn.setText("Next"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.next_clicked)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20, 20, 80, 30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)

    def enter(self):
        self.counter += 1
        g = dictionary5.get(self.counter, [])
        guess_chars = []; widgets = []
        for n in g:
            w = getattr(self, n, None)
            widgets.append(w)
            guess_chars.append(w.text().upper() if w else "")
        if "" in guess_chars:
            QMessageBox.warning(None, "Not enough letters", "Not enough letters")
            self.counter = max(0, self.counter-1)
            return
        guess = "".join(guess_chars)
        target = self.get_target_word()
        if not self.check_word_valid(guess):
            QMessageBox.warning(None, "Invalid", "Not a valid word")
            self.counter = max(0, self.counter-1)
            return
        self.color_row_feedback(guess, target, widgets)
        if guess == target:
            self.next_btn.setEnabled(True)
        if self.counter >= self.max_attempts and guess != target:
            if CURRENT_USER:
                update_stats_db(CURRENT_USER, win=False, set_last_daily_play=False)
            QMessageBox.information(None, "Lose", f"You lose. The word was {target}")
            self.back_clicked()

    def get_target_word(self):
        try:
            with open("5-wordsource.txt", "r", encoding="utf-8") as f:
                lines = [ln.strip().upper() for ln in f if ln.strip()]
        except Exception:
            lines = []
        if not lines:
            return "WORDS"
        return random.choice(lines)

    def next_clicked(self):
        if CURRENT_USER:
            update_stats_db(CURRENT_USER, win=True, set_last_daily_play=False)
        self.label_winstreak.setText(f"Winstreak: {get_user_stats(CURRENT_USER).get('winstreak',0)}")
        self.next_btn.setEnabled(False)
        FiveWordleUI = FiveWordle()
        FiveWordleUI.setupUi(MainWindow5)
        MainWindow5.show()

    def back_clicked(self):
        try:
            MainWindow5.hide()
            MainWindow1.show()
        except Exception:
            pass

# --- 6-letter wordle UI ---
class SixWordle(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=6)

    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(350, 20, 250, 40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("6-Word Wordle")
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget); self.label_winstreak.setGeometry(QtCore.QRect(720, 20, 160, 24)); fw=QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw); self.label_winstreak.setText(f"Winstreak: {get_user_stats(CURRENT_USER).get('winstreak',0)}")
        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40, 80, 820, 360)); self.grid = QtWidgets.QGridLayout(self.widget)
        rows = [
            ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e","lineEdit_za"],
            ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i","lineEdit_zb"],
            ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o","lineEdit_zc"],
            ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t","lineEdit_zd"],
            ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y","lineEdit_z"]
        ]
        for r, row in enumerate(rows):
            for c, name in enumerate(row):
                le = QtWidgets.QLineEdit(self.widget)
                configure_letter_edit(le)
                if c == len(row)-1:
                    le.returnPressed.connect(self.enter)
                setattr(self, name, le)
                self.grid.addWidget(le, r, c, 1, 1)
        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(380, 460, 120, 32)); self.next_btn.setText("Next"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.next_clicked)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20, 20, 80, 30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)

    def enter(self):
        self.counter += 1
        g = dictionary4.get(self.counter, [])  # dictionary4 from top maps 6-letter rows
        guess_chars = []; widgets = []
        for n in g:
            w = getattr(self, n, None)
            widgets.append(w)
            guess_chars.append(w.text().upper() if w else "")
        if "" in guess_chars:
            QMessageBox.warning(None, "Not enough letters", "Not enough letters")
            self.counter = max(0, self.counter-1)
            return
        guess = "".join(guess_chars)
        target = self.get_target_word()
        if not self.check_word_valid(guess):
            QMessageBox.warning(None, "Invalid", "Not a valid word")
            self.counter = max(0, self.counter-1)
            return
        self.color_row_feedback(guess, target, widgets)
        if guess == target:
            self.next_btn.setEnabled(True)
        if self.counter >= self.max_attempts and guess != target:
            if CURRENT_USER:
                update_stats_db(CURRENT_USER, win=False, set_last_daily_play=False)
            QMessageBox.information(None, "Lose", f"You lose. The word was {target}")
            self.back_clicked()

    def get_target_word(self):
        try:
            with open("6-wordsource.txt", "r", encoding="utf-8") as f:
                lines = [ln.strip().upper() for ln in f if ln.strip()]
        except Exception:
            lines = []
        if not lines:
            return "PYTHON"
        return random.choice(lines)

    def next_clicked(self):
        if CURRENT_USER:
            update_stats_db(CURRENT_USER, win=True, set_last_daily_play=False)
        self.label_winstreak.setText(f"Winstreak: {get_user_stats(CURRENT_USER).get('winstreak',0)}")
        self.next_btn.setEnabled(False)
        SixWordleUI = SixWordle()
        SixWordleUI.setupUi(MainWindow6)
        MainWindow6.show()

    def back_clicked(self):
        try:
            MainWindow6.hide()
            MainWindow1.show()
        except Exception:
            pass

# --- Daily Word UI (6-letter daily with winstreak label like 5-letter placement) ---
class DailyWordUI(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=6)

    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(360, 10, 260, 40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("Daily Word")
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget); self.label_winstreak.setGeometry(QtCore.QRect(720, 20, 160, 24)); fw=QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw); self.label_winstreak.setText(f"Winstreak: {get_user_stats(CURRENT_USER).get('winstreak',0)}")
        # target label shows the daily word internally (for testing/dev) - keep small and hidden in production; we keep it visible to follow original UI
        self.label_target = QtWidgets.QLabel(self.centralwidget); self.label_target.setGeometry(QtCore.QRect(360, 50, 200, 20)); small = QFont(); small.setPointSize(10); self.label_target.setFont(small); self.label_target.setText(daily_word_from_file("dailyword.txt"))
        # grid 5 rows x 6 columns
        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40, 80, 820, 360)); self.grid = QtWidgets.QGridLayout(self.widget)
        rows = [
            ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e","lineEdit_za"],
            ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i","lineEdit_zb"],
            ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o","lineEdit_zc"],
            ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t","lineEdit_zd"],
            ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y","lineEdit_z"]
        ]
        for r,row in enumerate(rows):
            for c,name in enumerate(row):
                le = QtWidgets.QLineEdit(self.widget)
                configure_letter_edit(le)
                if c == len(row)-1:
                    le.returnPressed.connect(self.enter)
                setattr(self, name, le)
                self.grid.addWidget(le, r, c, 1, 1)
        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(380, 460, 120, 32)); self.next_btn.setText("Complete"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.complete)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20, 20, 80, 30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)
        # disable daily if user already played today
        refresh_daily_button_state(ui)

    def enter(self):
        # similar to SixWordle.enter but sets last_daily_play on win/loss
        self.counter += 1
        g = dictionary4.get(self.counter, [])
        guess = []; widgets = []
        for n in g:
            w = getattr(self, n, None)
            widgets.append(w)
            guess.append(w.text().upper() if w else "")
        if "" in guess:
            QMessageBox.warning(None, "Not enough letters", "Not enough letters")
            self.counter = max(0, self.counter-1)
            return
        guess_word = "".join(guess)
        target = self.label_target.text().upper()
        if not self.check_word_valid(guess_word):
            QMessageBox.warning(None, "Invalid", "Not a valid word")
            self.counter = max(0, self.counter-1)
            return
        self.color_row_feedback(guess_word, target, widgets)
        if guess_word == target:
            self.next_btn.setEnabled(True)
        if self.counter >= self.max_attempts and guess_word != target:
            # mark loss and last_daily_play
            if CURRENT_USER:
                update_stats_db(CURRENT_USER, win=False, set_last_daily_play=True)
            QMessageBox.information(None, "Lose", f"You lose. The word was {target}")
            refresh_daily_button_state(ui)
            self.back_clicked()

    def complete(self):
        # user pressed Complete after winning
        if CURRENT_USER:
            update_stats_db(CURRENT_USER, win=True, set_last_daily_play=True)
        self.label_winstreak.setText(f"Winstreak: {get_user_stats(CURRENT_USER).get('winstreak',0)}")
        self.next_btn.setEnabled(False)
        refresh_daily_button_state(ui)
        try:
            MainwindowDaily.hide()
            MainWindow1.show()
        except Exception:
            pass

    def back_clicked(self):
        try:
            MainwindowDaily.hide()
            MainWindow1.show()
        except Exception:
            pass

# ------------------------------------------------------------------------
# Application entrypoint: create windows and UI instances
# ------------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # apply options
    apply_options(load_options())
    # instantiate UI classes
    ui = MainWindowUI()
    uiLogin = LoginUI()
    uiSignup = SignupUI()
    uiStat = StatisticUI()
    ui4 = FourWordle()
    ui5 = FiveWordle()
    ui6 = SixWordle()
    uiDaily = DailyWordUI()
    # create QMainWindow objects
    MainWindow1 = QtWidgets.QMainWindow()   # main
    DialogWindowLogin = QtWidgets.QMainWindow()  # login (using QMainWindow for simplicity)
    SignupWindow = QtWidgets.QMainWindow()
    MainWindowStat = QtWidgets.QMainWindow()
    MainWindow4 = QtWidgets.QMainWindow()
    MainWindow5 = QtWidgets.QMainWindow()
    MainWindow6 = QtWidgets.QMainWindow()
    MainwindowDaily = QtWidgets.QMainWindow()
    # setup UIs
    ui.setupUi(MainWindow1)
    uiLogin.setupUi(DialogWindowLogin)
    uiSignup.setupUi(SignupWindow)
    uiStat.setupUi(MainWindowStat)
    ui4.setupUi(MainWindow4)
    ui5.setupUi(MainWindow5)
    ui6.setupUi(MainWindow6)
    uiDaily.setupUi(MainwindowDaily)
    # start on login
    DialogWindowLogin.show()
    # ensure daily button correct
    refresh_daily_button_state(ui)
    sys.exit(app.exec_())
