import random
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox
import config
from config import WORDLE_DICTIONARIES
from database import update_stats_db
from utils import configure_letter_edit, clear_row_widgets, daily_word_from_file, is_valid_word, refresh_daily_button_state

class BaseWordle:
    def __init__(self, letters_count=5):
        self.letters_count = letters_count
        self.counter = 0
        self.max_attempts = 5
        self.target_word = None
        self.MainWindow = None 
        self.grid_map = WORDLE_DICTIONARIES.get(letters_count)

    def check_word_valid(self, word):
        return is_valid_word(word, self.letters_count)

    def color_row_feedback(self, guess, target, widgets):
        t = list(target)
        res = [""] * len(guess)
        
        for i, ch in enumerate(guess):
            w = widgets[i]
            if ch == t[i]:
                w.setStyleSheet("background-color: rgb(0,170,0);") 
                t[i] = None 
                res[i] = "green"
        
        for i, ch in enumerate(guess):
            w = widgets[i]
            if res[i] == "":
                try:
                    idx = t.index(ch)
                    w.setStyleSheet("background-color: rgb(255,255,0);") 
                    t[idx] = None 
                except ValueError:
                    w.setStyleSheet("background-color: rgb(255,0,0);") 

    def enter(self):
        attempt = self.counter + 1
        g = self.grid_map.get(attempt, [])
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
        
        for w in widgets:
            if w:
                w.setEnabled(False)
        
        if guess == self.target_word:
            self.on_win()
        
        self.counter += 1
        
        if self.counter >= self.max_attempts and guess != self.target_word:
            self.on_lose()
            
    def on_win(self):
        QMessageBox.information(None, "Win", "You won!")

    def on_lose(self):
        if self.letters_count == 4:
            config.WINSTREAK_4 = 0
        elif self.letters_count == 5:
            config.WINSTREAK_5 = 0
        elif self.letters_count == 6:
            config.WINSTREAK_6 = 0
            
        QMessageBox.information(None, "Lose", "You lose. The word was " + self.target_word)
        self.back_clicked()

    def get_target_word(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [ln.strip().upper() for ln in f if ln.strip() and len(ln.strip()) == self.letters_count]
        except Exception:
            lines = []
            
        default_word = "WORD"[:self.letters_count] 
        return random.choice(lines) if lines else default_word
        
    def back_clicked(self):
        pass

class FourWordle(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=4)

    def setupUi(self, MainWindow, MainWindowMain_ref):
        if hasattr(self, 'MainWindow') and self.MainWindow and self.MainWindow.centralWidget():
            self.MainWindow.centralWidget().deleteLater()

        self.MainWindowMain_ref = MainWindowMain_ref
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(320, 10, 260, 40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("4-Word Wordle")
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget); self.label_winstreak.setGeometry(QtCore.QRect(620,20,160,24)); fw=QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw); self.label_winstreak.setText(f"Winstreak: {config.WINSTREAK_4}")
        
        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40,80,720,360))
        self.grid = QtWidgets.QGridLayout(self.widget)
        
        rows = WORDLE_DICTIONARIES.get(4)
        for r_idx, (r, row) in enumerate(rows.items()):
            for c, name in enumerate(row):
                def make_next_getter(row_names=row, c=c):
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
                self.grid.addWidget(le, r_idx, c, 1, 1)

        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(340,460,120,32)); self.next_btn.setText("Next"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.next_clicked)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20,20,80,30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Only set target word if it hasn't been set (i.e., this is the first time setupUi runs)
        if not self.target_word:
            self.target_word = self.get_target_word("4-wordsource.txt")

    def on_win(self):
        if config.CURRENT_USER:
            update_stats_db(config.CURRENT_USER, win=True, set_last_daily_play=False)
        self.next_btn.setEnabled(True)

    def on_lose(self):
        if config.CURRENT_USER:
            update_stats_db(config.CURRENT_USER, win=False, set_last_daily_play=False)
        super().on_lose() 

    def next_clicked(self):
        config.WINSTREAK_4 += 1
        self.label_winstreak.setText(f"Winstreak: {config.WINSTREAK_4}")
        self.next_btn.setEnabled(False)
        
     
        self.counter = 0 
        self.target_word = self.get_target_word("4-wordsource.txt")
        
        self.MainWindow.setWindowTitle("4-Word Wordle") 
        self.setupUi(self.MainWindow, self.MainWindowMain_ref)
        self.MainWindow.show()

    def back_clicked(self):
        try:
            self.MainWindow.hide()
            self.MainWindowMain_ref.show()
        except Exception:
            pass

class FiveWordle(FourWordle): 
    def __init__(self):
        super().__init__() 
        self.letters_count = 5
        self.grid_map = WORDLE_DICTIONARIES.get(5)

    def setupUi(self, MainWindow, MainWindowMain_ref):
        if hasattr(self, 'MainWindow') and self.MainWindow and self.MainWindow.centralWidget():
            self.MainWindow.centralWidget().deleteLater()

        self.MainWindowMain_ref = MainWindowMain_ref
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(320, 10, 260, 40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("5-Word Wordle")
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget); self.label_winstreak.setGeometry(QtCore.QRect(620,20,160,24)); fw=QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw); self.label_winstreak.setText(f"Winstreak: {config.WINSTREAK_5}")

        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40,80,720,360)); self.grid = QtWidgets.QGridLayout(self.widget)
        
        rows = WORDLE_DICTIONARIES.get(5)
        for r_idx, (r, row) in enumerate(rows.items()):
            for c, name in enumerate(row):
                def make_next_getter(row_names=row, c=c):
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
                self.grid.addWidget(le, r_idx, c, 1, 1)

        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(340,440,120,32)); self.next_btn.setText("Next"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.next_clicked)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20,20,80,30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)
        if not self.target_word:
            self.target_word = self.get_target_word("5-wordsource.txt")
        
    def next_clicked(self):
        config.WINSTREAK_5 += 1
        self.label_winstreak.setText(f"Winstreak: {config.WINSTREAK_5}")
        self.next_btn.setEnabled(False)
        
        self.counter = 0 
        self.target_word = self.get_target_word("5-wordsource.txt")
        
        self.MainWindow.setWindowTitle("5-Word Wordle")
        self.setupUi(self.MainWindow, self.MainWindowMain_ref) 
        self.MainWindow.show()

    def back_clicked(self):
        try:
            self.MainWindow.hide()
            self.MainWindowMain_ref.show()
        except Exception:
            pass

class SixWordle(FourWordle): 
    def __init__(self):
        super().__init__() 
        self.letters_count = 6
        self.grid_map = WORDLE_DICTIONARIES.get(6)

    def setupUi(self, MainWindow, MainWindowMain_ref):
        if hasattr(self, 'MainWindow') and self.MainWindow and self.MainWindow.centralWidget():
            self.MainWindow.centralWidget().deleteLater()

        self.MainWindowMain_ref = MainWindowMain_ref
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(350, 10, 260, 40)); f=QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("6-Word Wordle")
        self.label_winstreak = QtWidgets.QLabel(self.centralwidget); self.label_winstreak.setGeometry(QtCore.QRect(720,20,160,24)); fw=QFont(); fw.setPointSize(12); fw.setBold(True); self.label_winstreak.setFont(fw); self.label_winstreak.setText(f"Winstreak: {config.WINSTREAK_6}")
        
        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40,80,820,360)); self.grid = QtWidgets.QGridLayout(self.widget)
        
        rows = WORDLE_DICTIONARIES.get(6)
        for r_idx, (r, row) in enumerate(rows.items()):
            for c, name in enumerate(row):
                def make_next_getter(row_names=row, c=c):
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
                self.grid.addWidget(le, r_idx, c, 1, 1)

        self.next_btn = QtWidgets.QPushButton(self.centralwidget); self.next_btn.setGeometry(QtCore.QRect(380,460,120,32)); self.next_btn.setText("Next"); self.next_btn.setEnabled(False); self.next_btn.clicked.connect(self.next_clicked)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget); self.back_btn.setGeometry(QtCore.QRect(20,20,80,30)); self.back_btn.setText("Back"); self.back_btn.clicked.connect(self.back_clicked)
        MainWindow.setCentralWidget(self.centralwidget)
        if not self.target_word:
            self.target_word = self.get_target_word("6-wordsource.txt")
        
    def next_clicked(self):
        config.WINSTREAK_6 += 1
        self.label_winstreak.setText(f"Winstreak: {config.WINSTREAK_6}")
        self.next_btn.setEnabled(False)
        
        
        self.counter = 0 
        self.target_word = self.get_target_word("6-wordsource.txt")
        
        self.MainWindow.setWindowTitle("6-Word Wordle") 
        self.setupUi(self.MainWindow, self.MainWindowMain_ref)
        self.MainWindow.show()

    def back_clicked(self):
        try:
            self.MainWindow.hide()
            self.MainWindowMain_ref.show()
        except Exception:
            pass

class DailyWordUI(BaseWordle):
    def __init__(self):
        super().__init__(letters_count=6)
        self.grid_map = WORDLE_DICTIONARIES.get(6)
        
    def setupUi(self, MainWindow, MainWindowMain_ref, main_ui_instance):
        if hasattr(self, 'MainWindow') and self.MainWindow and self.MainWindow.centralWidget():
            self.MainWindow.centralWidget().deleteLater()
            
        self.MainWindowMain_ref = MainWindowMain_ref
        self.main_ui_instance = main_ui_instance
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900,520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        
        self.title = QtWidgets.QLabel(self.centralwidget); self.title.setGeometry(QtCore.QRect(360,10,260,40)); f = QFont(); f.setPointSize(16); f.setBold(True); self.title.setFont(f); self.title.setText("Daily Word")

        self.widget = QtWidgets.QWidget(self.centralwidget); self.widget.setGeometry(QtCore.QRect(40,80,820,360)); self.grid = QtWidgets.QGridLayout(self.widget)

        rows = WORDLE_DICTIONARIES.get(6)
        for r_idx, (r, row) in enumerate(rows.items()):
            for c, name in enumerate(row):
                def make_next_getter(row_names=row, c=c):
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
                self.grid.addWidget(le, r_idx, c, 1, 1)

        self.complete_btn = QtWidgets.QPushButton(self.centralwidget)
        self.complete_btn.setGeometry(QtCore.QRect(380,460,120,32))
        self.complete_btn.setText("Complete")
        self.complete_btn.setEnabled(False)
        self.complete_btn.clicked.connect(self.complete)

        self.back_btn = QtWidgets.QPushButton(self.centralwidget)
        self.back_btn.setGeometry(QtCore.QRect(20,20,80,30))
        self.back_btn.setText("Back")
        self.back_btn.clicked.connect(self.back_clicked)

        MainWindow.setCentralWidget(self.centralwidget)
        self.target_word = daily_word_from_file()
        refresh_daily_button_state(main_ui_instance)

    def on_win(self):
        if config.CURRENT_USER:
            update_stats_db(config.CURRENT_USER, win=True, set_last_daily_play=True)
        self.complete_btn.setEnabled(True)

    def on_lose(self):
        if config.CURRENT_USER:
            update_stats_db(config.CURRENT_USER, win=False, set_last_daily_play=True)
        QMessageBox.information(None, "Lose", "You lose. The word was " + self.target_word)
        refresh_daily_button_state(self.main_ui_instance)
        self.back_clicked()

    def complete(self):
        self.complete_btn.setEnabled(False)
        refresh_daily_button_state(self.main_ui_instance)
        try:
            self.MainWindow.hide()
            self.MainWindowMain_ref.show()
        except Exception:
            pass

    def back_clicked(self):
        try:
            self.MainWindow.hide()
            self.MainWindowMain_ref.show()
        except Exception:
            pass