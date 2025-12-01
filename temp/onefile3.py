# newprogram.py - PART 1/4
# Wordle-like app (4/5/6 + Daily) with separate in-memory winstreaks per difficulty,
# daily-once-per-day-per-user, signup/login fixes, QLineEdits limited to 1 letter,
# auto-focus to next letter, and clearing row when invalid or incomplete.

import sys
import os
import sqlite3
import random
import json
from datetime import date
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QFont
from PyQt5.QtWidgets import QMessageBox, QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout

try:
    import enchant
except Exception:
    enchant = None

# Try to import user's get_db helper; fallback to sqlite
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
                          last_daily_play TEXT
                          )""")
        conn.commit()
        return conn, cursor

# ---------------- GLOBALS ----------------
CURRENT_USER = None
WINSTREAK_4 = 0
WINSTREAK_5 = 0
WINSTREAK_6 = 0

OPTIONS_FILE = "options.json"
DEFAULT_OPTIONS = {"theme": "Light", "font": "Default"}

# ---------------- Ensure statistics table ----------------
def ensure_statistics_table():
    conn, cursor = get_db()
    cursor.execute("""CREATE TABLE IF NOT EXISTS statistics (
                      username TEXT PRIMARY KEY,
                      wins INTEGER DEFAULT 0,
                      losses INTEGER DEFAULT 0,
                      last_daily_play TEXT
                      )""")
    conn.commit()
    cursor.execute("PRAGMA table_info(statistics)")
    cols = [r[1] for r in cursor.fetchall()]
    if "last_daily_play" not in cols:
        try:
            cursor.execute("ALTER TABLE statistics ADD COLUMN last_daily_play TEXT")
            conn.commit()
        except Exception:
            pass
    conn.close()

ensure_statistics_table()

# ---------------- LineEdit mapping ----------------
dictionary6 = {
    1: ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e","lineEdit_za"],
    2: ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i","lineEdit_zb"],
    3: ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o","lineEdit_zc"],
    4: ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t","lineEdit_zd"],
    5: ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y","lineEdit_z"]
}

dictionary5 = {
    1: ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e"],
    2: ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i"],
    3: ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o"],
    4: ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t"],
    5: ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y"]
}

dictionary4 = {
    1: ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d"],
    2: ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m"],
    3: ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n"],
    4: ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s"],
    5: ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x"]
}

# ---------------- DB helpers ----------------
def update_stats_db(username, win: bool, set_last_daily_play=False):
    if not username:
        return False
    conn, cursor = get_db()
    cursor.execute("SELECT wins, losses FROM statistics WHERE username=?", (username,))
    row = cursor.fetchone()
    if row:
        if win:
            cursor.execute("UPDATE statistics SET wins = wins + 1 WHERE username=?", (username,))
        else:
            cursor.execute("UPDATE statistics SET losses = losses + 1 WHERE username=?", (username,))
    else:
        wins = 1 if win else 0
        losses = 0 if win else 1
        cursor.execute("INSERT INTO statistics (username, wins, losses) VALUES (?, ?, ?)",
                       (username, wins, losses))
    if set_last_daily_play:
        today = date.today().isoformat()
        cursor.execute("UPDATE statistics SET last_daily_play = ? WHERE username = ?", (today, username))
    conn.commit()
    conn.close()
    return True

def get_user_stats(username):
    if not username:
        return {"wins":0,"losses":0,"last_daily_play":None}
    conn, cursor = get_db()
    cursor.execute("SELECT wins, losses, last_daily_play FROM statistics WHERE username=?", (username,))
    r = cursor.fetchone()
    conn.close()
    if r:
        return {"wins": r[0] or 0, "losses": r[1] or 0, "last_daily_play": r[2]}
    return {"wins":0,"losses":0,"last_daily_play":None}

def can_play_daily(username):
    if not username:
        return False
    stats = get_user_stats(username)
    last = stats.get("last_daily_play")
    return last != date.today().isoformat()

# ---------------- options ----------------
def load_options():
    if os.path.exists(OPTIONS_FILE):
        try:
            with open(OPTIONS_FILE,"r",encoding="utf-8") as fh:
                opts = json.load(fh)
                return {**DEFAULT_OPTIONS, **opts}
        except Exception:
            pass
    return DEFAULT_OPTIONS.copy()

def save_options(opts):
    try:
        with open(OPTIONS_FILE,"w",encoding="utf-8") as fh:
            json.dump(opts, fh)
            return True
    except Exception:
        return False

def apply_options(options):
    app = QtWidgets.QApplication.instance()
    if not app:
        return
    theme = options.get("theme","Light")
    font_choice = options.get("font","Default")
    if theme == "Dark":
        ss = "QWidget{background:#2b2b2b;color:#e6e6e6;}QLineEdit{background:#3a3a3a;color:#e6e6e6}"
    elif theme == "Blue":
        ss = "QWidget{background:#eaf6ff;color:#0a2540;}QLineEdit{background:#ffffff;color:#0a2540}"
    else:
        ss = ""
    app.setStyleSheet(ss)
    if font_choice == "Arial":
        app.setFont(QFont("Arial",10))
    elif font_choice == "Courier New":
        app.setFont(QFont("Courier New",10))
    else:
        app.setFont(QFont())

# ---------------- daily word ----------------
def daily_word_from_file(filepath="dailyword.txt"):
    try:
        with open(filepath,"r",encoding="utf-8") as fh:
            lines = [ln.strip() for ln in fh if ln.strip()]
    except Exception:
        lines = []
    if not lines:
        return "PYTHON"
    idx = date.today().toordinal() % len(lines)
    return lines[idx].upper()

# ---------------- QLineEdit configuration ----------------
def configure_letter_edit(le: QtWidgets.QLineEdit, next_widget_getter=None):
    """
    Configure a QLineEdit to accept exactly one uppercase letter.
    next_widget_getter: callable returning the next widget to focus (or None).
    """
    le.setMaxLength(1)
    le.setAlignment(Qt.AlignCenter)
    f = QFont(); f.setPointSize(14); le.setFont(f)
    regex = QRegExp("^[A-Za-z]?$")
    le.setValidator(QRegExpValidator(regex))
    def on_text_changed(txt):
        if txt is None:
            return
        txtu = txt.upper()
        if le.text() != txtu:
            try:
                le.blockSignals(True)
                le.setText(txtu)
            finally:
                le.blockSignals(False)
        # move focus to next widget if we have a single char
        if len(txtu) == 1 and next_widget_getter:
            nxt = next_widget_getter()
            if nxt:
                nxt.setFocus()
    le.textChanged.connect(on_text_changed)

# ---------------- helper to clear entire row ----------------
def clear_row_widgets(widgets):
    for w in widgets:
        if w:
            try:
                w.blockSignals(True)
                w.clear()
            finally:
                w.blockSignals(False)

# ---------------- refresh main daily button ----------------
def refresh_daily_button_state(main_ui=None):
    try:
        if CURRENT_USER:
            allowed = can_play_daily(CURRENT_USER)
            if main_ui and hasattr(main_ui, "pushButton_3"):
                main_ui.pushButton_3.setEnabled(bool(allowed))
            else:
                try:
                    ui.pushButton_3.setEnabled(bool(allowed))
                except Exception:
                    btn = MainWindowMain.findChild(QtWidgets.QPushButton, "pushButton_3")
                    if btn:
                        btn.setEnabled(bool(allowed))
        else:
            if main_ui and hasattr(main_ui, "pushButton_3"):
                main_ui.pushButton_3.setEnabled(False)
            else:
                try:
                    ui.pushButton_3.setEnabled(False)
                except Exception:
                    pass
    except Exception:
        pass

# ------------------------------------------------------------------------
# UI classes start here
# ------------------------------------------------------------------------
class MainWindowUI(object):
    def setupUi(self, MainWindow):
        self.window = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(620, 620)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # Title
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(220, 30, 280, 60))
        f = QFont(); f.setPointSize(28); f.setBold(True); self.title.setFont(f); self.title.setText("WORDLE")
        # Difficulty label
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(250, 110, 140, 20))
        f2 = QFont(); f2.setPointSize(12); self.label.setFont(f2); self.label.setText("DIFFICULTY")
        # Combo
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(180, 140, 260, 36))
        self.comboBox.addItems(["4 Word wordle","5 Word wordle","6 Word wordle"])
        # Buttons group
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(220, 200, 180, 340))
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        # Play
        self.pushButton_4 = QtWidgets.QPushButton(self.widget); self.pushButton_4.setText("PLAY"); self.pushButton_4.clicked.connect(self.play_clicked); self.gridLayout.addWidget(self.pushButton_4,0,0)
        # Daily
        self.pushButton_3 = QtWidgets.QPushButton(self.widget); self.pushButton_3.setText("DAILY WORD"); self.pushButton_3.clicked.connect(self.daily_clicked); self.gridLayout.addWidget(self.pushButton_3,1,0)
        # Statistic
        self.pushButton_stat = QtWidgets.QPushButton(self.widget); self.pushButton_stat.setText("STATISTIC"); self.pushButton_stat.clicked.connect(self.statistic_clicked); self.gridLayout.addWidget(self.pushButton_stat,2,0)
        # Options
        self.pushButton_opt = QtWidgets.QPushButton(self.widget); self.pushButton_opt.setText("OPTIONS"); self.pushButton_opt.clicked.connect(self.options_clicked); self.gridLayout.addWidget(self.pushButton_opt,3,0)
        # Exit
        self.pushButton_exit = QtWidgets.QPushButton(self.widget); self.pushButton_exit.setText("EXIT"); self.pushButton_exit.clicked.connect(QtWidgets.qApp.quit); self.gridLayout.addWidget(self.pushButton_exit,4,0)
        MainWindow.setCentralWidget(self.centralwidget)

    def play_clicked(self):
        sel = self.comboBox.currentText()
        try:
            MainWindowMain.hide()
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
            QMessageBox.warning(None, "Error", f"Could not open game: {e}")

    def daily_clicked(self):
        try:
            MainWindowMain.hide()
            uiDaily.setupUi(MainWindowDaily)
            MainWindowDaily.show()
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not open daily: {e}")

    def statistic_clicked(self):
        try:
            MainWindowMain.hide()
            uiStat.load_stats()
            MainWindowStat.show()
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
# newprogram.py - PART 2/4
# Login, Signup, Statistic, BaseWordle helpers and coloring logic

class LoginUI(object):
    def setupUi(self, Dialog):
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(420, 420)
        self.title = QtWidgets.QLabel(Dialog); self.title.setGeometry(QtCore.QRect(150, 30, 140, 60)); f=QFont(); f.setPointSize(20); f.setBold(True); self.title.setFont(f); self.title.setText("Log-In")
        self.groupBox = QtWidgets.QGroupBox(Dialog); self.groupBox.setGeometry(QtCore.QRect(80, 110, 260, 250))
        self.user_edit = QtWidgets.QLineEdit(self.groupBox); self.user_edit.setGeometry(QtCore.QRect(20, 30, 220, 34))
        self.pw_edit = QtWidgets.QLineEdit(self.groupBox); self.pw_edit.setGeometry(QtCore.QRect(20, 90, 220, 34)); self.pw_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lbl_user = QtWidgets.QLabel(self.groupBox); self.lbl_user.setGeometry(QtCore.QRect(20, 12, 100, 16)); self.lbl_user.setText("Username:")
        self.lbl_pw = QtWidgets.QLabel(self.groupBox); self.lbl_pw.setGeometry(QtCore.QRect(20, 72, 100, 16)); self.lbl_pw.setText("Password:")
        self.login_btn = QtWidgets.QPushButton(self.groupBox); self.login_btn.setGeometry(QtCore.QRect(80, 150, 100, 34)); self.login_btn.setText("LOGIN"); self.login_btn.clicked.connect(self.login_check)
        # sign-up link centered and clickable
        self.label_signup = QtWidgets.QLabel(self.groupBox); self.label_signup.setGeometry(QtCore.QRect(60, 190, 140, 20)); self.label_signup.setText("<a href='#'>Sign-up</a>"); self.label_signup.setAlignment(Qt.AlignCenter)
        self.label_signup.setOpenExternalLinks(False)
        self.label_signup.linkActivated.connect(self.open_signup)

    def login_check(self):
        global CURRENT_USER
        username = self.user_edit.text().strip()
        password = self.pw_edit.text()
        if username == "" or password == "":
            QMessageBox.warning(None, "Error", "Please enter username and password")
            return
        conn, cursor = get_db()
        cursor.execute("SELECT username FROM users WHERE username=? AND password=?", (username, password))
        r = cursor.fetchone()
        conn.close()
        if r:
            CURRENT_USER = username
            refresh_daily_button_state(ui)
            try:
                DialogWindowLogin.hide()
                MainWindowMain.show()
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
        Dialog.resize(420, 460)

        # FIXED TITLE — NO LONGER CUT OFF
        self.title = QtWidgets.QLabel(Dialog)
        self.title.setGeometry(QtCore.QRect(110, 20, 200, 40))  # wider
        f = QFont(); f.setPointSize(20); f.setBold(True)
        self.title.setFont(f)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setText("Sign-Up")

        # Main group box
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(60, 80, 300, 300))

        # Username Label - WIDER
        self.lbl_user = QtWidgets.QLabel(self.groupBox)
        self.lbl_user.setGeometry(QtCore.QRect(20, 20, 200, 20))
        self.lbl_user.setText("Username:")

        self.user_edit = QtWidgets.QLineEdit(self.groupBox)
        self.user_edit.setGeometry(QtCore.QRect(20, 40, 260, 34))

        # Password Label - WIDER
        self.lbl_pw = QtWidgets.QLabel(self.groupBox)
        self.lbl_pw.setGeometry(QtCore.QRect(20, 82, 200, 20))
        self.lbl_pw.setText("Password:")

        self.pw_edit = QtWidgets.QLineEdit(self.groupBox)
        self.pw_edit.setGeometry(QtCore.QRect(20, 102, 260, 34))
        self.pw_edit.setEchoMode(QtWidgets.QLineEdit.Password)

        # Confirm Password Label - WIDER
        self.lbl_confirm = QtWidgets.QLabel(self.groupBox)
        self.lbl_confirm.setGeometry(QtCore.QRect(20, 144, 200, 20))
        self.lbl_confirm.setText("Confirm Password:")

        self.pw_confirm = QtWidgets.QLineEdit(self.groupBox)
        self.pw_confirm.setGeometry(QtCore.QRect(20, 164, 260, 34))
        self.pw_confirm.setEchoMode(QtWidgets.QLineEdit.Password)

        # Buttons
        self.signup_btn = QtWidgets.QPushButton(self.groupBox)
        self.signup_btn.setGeometry(QtCore.QRect(60, 210, 80, 34))
        self.signup_btn.setText("Sign-up")
        self.signup_btn.clicked.connect(self.save_user)

        self.cancel_btn = QtWidgets.QPushButton(self.groupBox)
        self.cancel_btn.setGeometry(QtCore.QRect(160, 210, 80, 34))
        self.cancel_btn.setText("Cancel")
        self.cancel_btn.clicked.connect(self.back_to_login)

        # Back button (top-left)
        self.back_btn = QtWidgets.QPushButton(Dialog)
        self.back_btn.setGeometry(QtCore.QRect(10, 10, 80, 30))
        self.back_btn.setText("Back")
        self.back_btn.clicked.connect(self.back_to_login)


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

        conn, cursor = get_db()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            cursor.execute("INSERT OR IGNORE INTO statistics (username, wins, losses) VALUES (?, 0, 0)", (username,))
            conn.commit()
            QMessageBox.information(None, "Success", "Account created successfully!")
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




class StatisticUI(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(480, 420)

        # Center widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)

        # Main vertical layout with padding
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.layout.setContentsMargins(40, 20, 40, 20)
        self.layout.setSpacing(15)

        # --- Top row for back button ---
        self.top_row = QtWidgets.QHBoxLayout()
        self.back_btn = QtWidgets.QPushButton("Back", self.centralwidget)
        self.back_btn.setFixedSize(100, 35)
        self.back_btn.clicked.connect(self.back)
        self.top_row.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        self.top_row.addStretch()
        self.layout.addLayout(self.top_row)

        # Title
        self.title = QtWidgets.QLabel("Statistics", self.centralwidget)
        f = QFont()
        f.setPointSize(20)
        f.setBold(True)
        self.title.setFont(f)
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # --- nice horizontal line ---
        self.hl1 = QtWidgets.QFrame(self.centralwidget)
        self.hl1.setFrameShape(QtWidgets.QFrame.HLine)
        self.hl1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(self.hl1)

        # Stats layout
        self.info_layout = QtWidgets.QVBoxLayout()
        self.info_layout.setSpacing(10)

        stat_font = QFont()
        stat_font.setPointSize(13)
        stat_font.setBold(False)

        # Stats labels
        self.label_name = QtWidgets.QLabel("Name:", self.centralwidget)
        self.label_uid = QtWidgets.QLabel("UID:", self.centralwidget)
        self.label_wins = QtWidgets.QLabel("Wins:", self.centralwidget)
        self.label_losses = QtWidgets.QLabel("Losses:", self.centralwidget)
        self.label_pct = QtWidgets.QLabel("Win %:", self.centralwidget)
        self.label_lastdaily = QtWidgets.QLabel("Last Daily:", self.centralwidget)

        for lbl in [self.label_name, self.label_uid, self.label_wins, self.label_losses, self.label_pct, self.label_lastdaily]:
            lbl.setFont(stat_font)
            lbl.setAlignment(Qt.AlignCenter)
            self.info_layout.addWidget(lbl)

        self.layout.addLayout(self.info_layout)

        # --- bottom separator ---
        self.hl2 = QtWidgets.QFrame(self.centralwidget)
        self.hl2.setFrameShape(QtWidgets.QFrame.HLine)
        self.hl2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(self.hl2)

        MainWindow.setCentralWidget(self.centralwidget)

    def load_stats(self):
        if CURRENT_USER:
            stats = get_user_stats(CURRENT_USER)
            wins = stats.get("wins", 0)
            losses = stats.get("losses", 0)
            total = wins + losses
            pct = (wins / total) * 100 if total > 0 else 0

            self.label_name.setText(f"Name: {CURRENT_USER}")
            self.label_uid.setText(f"UID: {CURRENT_USER}")
            self.label_wins.setText(f"Wins: {wins}")
            self.label_losses.setText(f"Losses: {losses}")
            self.label_pct.setText(f"Win %: {pct:.2f}%")
            self.label_lastdaily.setText(f"Last Daily: {stats.get('last_daily_play','None')}")
        else:
            self.label_name.setText("Not logged in")

    def back(self):
        try:
            MainWindowStat.hide()
            MainWindowMain.show()
        except Exception:
            pass



class BaseWordle:
    def __init__(self, letters_count=5):
        self.letters_count = letters_count
        self.counter = 0
        self.max_attempts = 5
        self.target_word = None
        self.english_dict = enchant.Dict("en_US") if enchant else None

    def check_word_valid(self, word):
        if self.english_dict:
            return self.english_dict.check(word)
        return word.isalpha() and len(word) == self.letters_count

    def color_row_feedback(self, guess, target, widgets):
        t = list(target)
        res = [""] * len(guess)
        # exact matches
        for i,ch in enumerate(guess):
            w = widgets[i]
            if ch == t[i]:
                w.setStyleSheet("background-color: rgb(0,170,0);")
                t[i] = None
                res[i] = "green"
        # present elsewhere
        for i,ch in enumerate(guess):
            w = widgets[i]
            if res[i] == "":
                if ch in t:
                    w.setStyleSheet("background-color: rgb(255,255,0);")
                    t[t.index(ch)] = None
                else:
                    w.setStyleSheet("background-color: rgb(255,0,0);")
# newprogram.py - PART 3/4
# Implementations for 4- and 5-letter modes with single-letter edits and row-clearing behavior

class FourWordle(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=4)

    def setupUi(self, MainWindow):
        global WINSTREAK_4
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # Title (no answer label)
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(320, 10, 260, 40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("4-Word Wordle")
        # Winstreak label (top-right)
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget); self.label_winstreak.setGeometry(QtCore.QRect(620,20,160,24)); fw=QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw); self.label_winstreak.setText(f"Winstreak: {WINSTREAK_4}")
        # grid
        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40,80,720,360))
        self.grid = QtWidgets.QGridLayout(self.widget)
        rows = [
            ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d"],
            ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m"],
            ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n"],
            ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s"],
            ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x"]
        ]
        # create widgets and setup next focus behavior
        for r,row in enumerate(rows):
            for c,name in enumerate(row):
                # define getter for next widget in this row
                def make_next_getter(r=row, c=c, row_names=row):
                    def getter():
                        if c+1 < len(row_names):
                            return getattr(self, row_names[c+1], None)
                        return None
                    return getter
                le = QtWidgets.QLineEdit(self.widget)
                configure_letter_edit(le, next_widget_getter=make_next_getter())
                if c == len(row)-1:
                    # last in row -> Enter triggers row check
                    le.returnPressed.connect(self.enter)
                setattr(self, name, le)
                self.grid.addWidget(le, r, c, 1, 1)
        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(340,460,120,32)); self.next_btn.setText("Next"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.next_clicked)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20,20,80,30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)
        # pick a consistent target for this UI instance
        self.target_word = self.get_target_word()

    def get_target_word(self):
        try:
            with open("4-wordsource.txt","r",encoding="utf-8") as f:
                lines = [ln.strip().upper() for ln in f if ln.strip()]
        except Exception:
            lines = []
        if not lines:
            return "WORD"
        return random.choice(lines)

    def enter(self):
        # Determine the row we're on by counter (attempt index = counter+1)
        attempt = self.counter + 1
        g = dictionary4.get(attempt, [])
        widgets = [getattr(self, n, None) for n in g]
        # collect letters
        letters = [w.text().upper() if w else "" for w in widgets]
        # if any empty -> show Not a word and clear the row
        if "" in letters or any(len(ch) != 1 for ch in letters):
            QMessageBox.warning(None, "Not a word", "Not enough letters or incomplete row. Row will be cleared.")
            clear_row_widgets(widgets)
            return
        guess = "".join(letters)
        if not self.check_word_valid(guess):
            QMessageBox.warning(None, "Invalid", "Not a valid word. Row will be cleared.")
            clear_row_widgets(widgets)
            return
        # valid -> give feedback
        self.color_row_feedback(guess, self.target_word, widgets)
        if guess == self.target_word:
            self.next_btn.setEnabled(True)
        self.counter += 1
        if self.counter >= self.max_attempts and guess != self.target_word:
            if CURRENT_USER:
                update_stats_db(CURRENT_USER, win=False, set_last_daily_play=False)
            QMessageBox.information(None, "Lose", f"You lose. The word was {self.target_word}")
            self.back_clicked()

    def next_clicked(self):
        global WINSTREAK_4, ui4
        WINSTREAK_4 += 1
        if CURRENT_USER:
            update_stats_db(CURRENT_USER, win=True, set_last_daily_play=False)
        self.label_winstreak.setText(f"Winstreak: {WINSTREAK_4}")
        self.next_btn.setEnabled(False)
        # recreate and assign the global instance so event handlers reference the new instance
        ui4 = FourWordle()
        ui4.setupUi(MainWindow4)
        MainWindow4.show()

    def back_clicked(self):
        global WINSTREAK_4
        WINSTREAK_4 = 0
        try:
            MainWindow4.hide()
            MainWindowMain.show()
        except Exception:
            pass

class FiveWordle(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=5)

    def setupUi(self, MainWindow):
        global WINSTREAK_5
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(320, 10, 260, 40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("5-Word Wordle")
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget); self.label_winstreak.setGeometry(QtCore.QRect(620,20,160,24)); fw=QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw); self.label_winstreak.setText(f"Winstreak: {WINSTREAK_5}")
        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40,80,720,360)); self.grid = QtWidgets.QGridLayout(self.widget)
        rows = [
            ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e"],
            ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i"],
            ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o"],
            ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t"],
            ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y"]
        ]
        for r,row in enumerate(rows):
            for c,name in enumerate(row):
                def make_next_getter(r=row, c=c, row_names=row):
                    def getter():
                        if c+1 < len(row_names):
                            return getattr(self, row_names[c+1], None)
                        return None
                    return getter
                le = QtWidgets.QLineEdit(self.widget)
                configure_letter_edit(le, next_widget_getter=make_next_getter())
                if c == len(row)-1:
                    le.returnPressed.connect(self.enter)
                setattr(self, name, le)
                self.grid.addWidget(le, r, c, 1, 1)
        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(340,440,120,32)); self.next_btn.setText("Next"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.next_clicked)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20,20,80,30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)
        self.target_word = self.get_target_word()

    def get_target_word(self):
        try:
            with open("5-wordsource.txt","r",encoding="utf-8") as f:
                lines = [ln.strip().upper() for ln in f if ln.strip()]
        except Exception:
            lines = []
        if not lines:
            return "WORDS"
        return random.choice(lines)

    def enter(self):
        attempt = self.counter + 1
        g = dictionary5.get(attempt, [])
        widgets = [getattr(self, n, None) for n in g]
        letters = [w.text().upper() if w else "" for w in widgets]
        if "" in letters or any(len(ch) != 1 for ch in letters):
            QMessageBox.warning(None, "Not a word", "Not enough letters or incomplete row. Row will be cleared.")
            clear_row_widgets(widgets)
            return
        guess = "".join(letters)
        if not self.check_word_valid(guess):
            QMessageBox.warning(None, "Invalid", "Not a valid word. Row will be cleared.")
            clear_row_widgets(widgets)
            return
        self.color_row_feedback(guess, self.target_word, widgets)
        if guess == self.target_word:
            self.next_btn.setEnabled(True)
        self.counter += 1
        if self.counter >= self.max_attempts and guess != self.target_word:
            if CURRENT_USER:
                update_stats_db(CURRENT_USER, win=False, set_last_daily_play=False)
            QMessageBox.information(None, "Lose", f"You lose. The word was {self.target_word}")
            self.back_clicked()

    def next_clicked(self):
        global WINSTREAK_5, ui5
        WINSTREAK_5 += 1
        if CURRENT_USER:
            update_stats_db(CURRENT_USER, win=True, set_last_daily_play=False)
        self.label_winstreak.setText(f"Winstreak: {WINSTREAK_5}")
        self.next_btn.setEnabled(False)
        ui5 = FiveWordle()
        ui5.setupUi(MainWindow5)
        MainWindow5.show()

    def back_clicked(self):
        global WINSTREAK_5
        WINSTREAK_5 = 0
        try:
            MainWindow5.hide()
            MainWindowMain.show()
        except Exception:
            pass
# newprogram.py - PART 4/4
# 6-letter, Daily, and entrypoint

class SixWordle(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=6)

    def setupUi(self, MainWindow):
        global WINSTREAK_6
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(350, 10, 260, 40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("6-Word Wordle")
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget); self.label_winstreak.setGeometry(QtCore.QRect(720,20,160,24)); fw=QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw); self.label_winstreak.setText(f"Winstreak: {WINSTREAK_6}")
        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40,80,820,360)); self.grid = QtWidgets.QGridLayout(self.widget)
        rows = [
            ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e","lineEdit_za"],
            ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i","lineEdit_zb"],
            ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o","lineEdit_zc"],
            ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t","lineEdit_zd"],
            ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y","lineEdit_z"]
        ]
        for r,row in enumerate(rows):
            for c,name in enumerate(row):
                def make_next_getter(r=row, c=c, row_names=row):
                    def getter():
                        if c+1 < len(row_names):
                            return getattr(self, row_names[c+1], None)
                        return None
                    return getter
                le = QtWidgets.QLineEdit(self.widget)
                configure_letter_edit(le, next_widget_getter=make_next_getter())
                if c == len(row)-1:
                    le.returnPressed.connect(self.enter)
                setattr(self, name, le)
                self.grid.addWidget(le, r, c, 1, 1)
        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(380,460,120,32)); self.next_btn.setText("Next"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.next_clicked)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20,20,80,30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)
        self.target_word = self.get_target_word()

    def get_target_word(self):
        try:
            with open("6-wordsource.txt","r",encoding="utf-8") as f:
                lines = [ln.strip().upper() for ln in f if ln.strip()]
        except Exception:
            lines = []
        if not lines:
            return "PYTHON"
        return random.choice(lines)

    def enter(self):
        attempt = self.counter + 1
        g = dictionary6.get(attempt, [])
        widgets = [getattr(self, n, None) for n in g]
        letters = [w.text().upper() if w else "" for w in widgets]
        if "" in letters or any(len(ch) != 1 for ch in letters):
            QMessageBox.warning(None, "Not a word", "Not enough letters or incomplete row. Row will be cleared.")
            clear_row_widgets(widgets)
            return
        guess = "".join(letters)
        if not self.check_word_valid(guess):
            QMessageBox.warning(None, "Invalid", "Not a valid word. Row will be cleared.")
            clear_row_widgets(widgets)
            return
        self.color_row_feedback(guess, self.target_word, widgets)
        if guess == self.target_word:
            self.next_btn.setEnabled(True)
        self.counter += 1
        if self.counter >= self.max_attempts and guess != self.target_word:
            if CURRENT_USER:
                update_stats_db(CURRENT_USER, win=False, set_last_daily_play=False)
            QMessageBox.information(None, "Lose", f"You lose. The word was {self.target_word}")
            self.back_clicked()

    def next_clicked(self):
        global WINSTREAK_6, ui6
        WINSTREAK_6 += 1
        if CURRENT_USER:
            update_stats_db(CURRENT_USER, win=True, set_last_daily_play=False)
        self.label_winstreak.setText(f"Winstreak: {WINSTREAK_6}")
        self.next_btn.setEnabled(False)
        ui6 = SixWordle()
        ui6.setupUi(MainWindow6)
        MainWindow6.show()

    def back_clicked(self):
        global WINSTREAK_6
        WINSTREAK_6 = 0
        try:
            MainWindow6.hide()
            MainWindowMain.show()
        except Exception:
            pass

class DailyWordUI(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=6)

    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900,520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(360,10,260,40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("Daily Word")
        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40,80,820,360)); self.grid = QtWidgets.QGridLayout(self.widget)
        rows = [
            ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e","lineEdit_za"],
            ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i","lineEdit_zb"],
            ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o","lineEdit_zc"],
            ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t","lineEdit_zd"],
            ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y","lineEdit_z"]
        ]
        for r,row in enumerate(rows):
            for c,name in enumerate(row):
                def make_next_getter(r=row, c=c, row_names=row):
                    def getter():
                        if c+1 < len(row_names):
                            return getattr(self, row_names[c+1], None)
                        return None
                    return getter
                le = QtWidgets.QLineEdit(self.widget)
                configure_letter_edit(le, next_widget_getter=make_next_getter())
                if c == len(row)-1:
                    le.returnPressed.connect(self.enter)
                setattr(self, name, le)
                self.grid.addWidget(le, r, c, 1, 1)
        self.complete_btn = QtWidgets.QPushButton(self.centralwidget); self.complete_btn.setGeometry(QtCore.QRect(380,460,120,32)); self.complete_btn.setText("Complete"); self.complete_btn.setEnabled(False); self.complete_btn.clicked.connect(self.complete)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20,20,80,30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)
        self.target_word = daily_word_from_file("dailyword.txt")
        refresh_daily_button_state(ui)

    def enter(self):
        attempt = self.counter + 1
        g = dictionary6.get(attempt, [])
        widgets = [getattr(self, n, None) for n in g]
        letters = [w.text().upper() if w else "" for w in widgets]
        if "" in letters or any(len(ch) != 1 for ch in letters):
            QMessageBox.warning(None, "Not a word", "Not enough letters or incomplete row. Row will be cleared.")
            clear_row_widgets(widgets)
            return
        guess = "".join(letters)
        if not self.check_word_valid(guess):
            QMessageBox.warning(None, "Invalid", "Not a valid word. Row will be cleared.")
            clear_row_widgets(widgets)
            return
        self.color_row_feedback(guess, self.target_word, widgets)
        if guess == self.target_word:
            self.complete_btn.setEnabled(True)
        self.counter += 1
        if self.counter >= self.max_attempts and guess != self.target_word:
            if CURRENT_USER:
                update_stats_db(CURRENT_USER, win=False, set_last_daily_play=True)
            QMessageBox.information(None, "Lose", f"You lose. The word was {self.target_word}")
            refresh_daily_button_state(ui)
            self.back_clicked()

    def complete(self):
        if CURRENT_USER:
            update_stats_db(CURRENT_USER, win=True, set_last_daily_play=True)
        self.complete_btn.setEnabled(False)
        refresh_daily_button_state(ui)
        try:
            MainWindowDaily.hide()
            MainWindowMain.show()
        except Exception:
            pass

    def back_clicked(self):
        try:
            MainWindowDaily.hide()
            MainWindowMain.show()
        except Exception:
            pass

# ---------------- Entrypoint ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    apply_options(load_options())
    # UI instances (globals)
    ui = MainWindowUI()
    uiLogin = LoginUI()
    uiSignup = SignupUI()
    uiStat = StatisticUI()
    ui4 = FourWordle()
    ui5 = FiveWordle()
    ui6 = SixWordle()
    uiDaily = DailyWordUI()
    # Windows
    MainWindowMain = QtWidgets.QMainWindow()
    DialogWindowLogin = QtWidgets.QMainWindow()
    SignupWindow = QtWidgets.QMainWindow()
    MainWindowStat = QtWidgets.QMainWindow()
    MainWindow4 = QtWidgets.QMainWindow()
    MainWindow5 = QtWidgets.QMainWindow()
    MainWindow6 = QtWidgets.QMainWindow()
    MainWindowDaily = QtWidgets.QMainWindow()
    # Setup initial UIs
    ui.setupUi(MainWindowMain)
    uiLogin.setupUi(DialogWindowLogin)
    uiSignup.setupUi(SignupWindow)
    uiStat.setupUi(MainWindowStat)
    ui4.setupUi(MainWindow4)
    ui5.setupUi(MainWindow5)
    ui6.setupUi(MainWindow6)
    uiDaily.setupUi(MainWindowDaily)
    DialogWindowLogin.show()
    refresh_daily_button_state(ui)
    sys.exit(app.exec_())
