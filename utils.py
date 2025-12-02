import os
import json
import random
import config  
from datetime import date
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QFont
from config import OPTIONS_FILE, DEFAULT_OPTIONS, DAILY_WORD_FILE
from database import can_play_daily

try:
    import enchant
except Exception:
    enchant = None

ENGLISH_DICT = enchant.Dict("en_US") if enchant else None

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

def daily_word_from_file(filepath=DAILY_WORD_FILE):
    try:
        with open(filepath,"r",encoding="utf-8") as fh:
            lines = [ln.strip() for ln in fh if ln.strip()]
    except Exception:
        lines = []
    
    if not lines:
        return "PYTHON"
    
    idx = date.today().toordinal() % len(lines)
    return lines[idx].upper()

def is_valid_word(word, length):
    if len(word) != length:
        return False
    if ENGLISH_DICT:
        return ENGLISH_DICT.check(word)
    return word.isalpha()

def configure_letter_edit(le: QtWidgets.QLineEdit, next_widget_getter=None):
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
        
        if len(txtu) == 1 and next_widget_getter:
            nxt = next_widget_getter()
            if nxt:
                QtCore.QTimer.singleShot(0, nxt.setFocus)

    le.textChanged.connect(on_text_changed)

def clear_row_widgets(widgets):
    for w in widgets:
        if w:
            try:
                w.blockSignals(True)
                w.clear()
            finally:
                w.blockSignals(False)

def refresh_daily_button_state(main_ui_instance):
    try:
        if config.CURRENT_USER:
            allowed = can_play_daily(config.CURRENT_USER)
            if hasattr(main_ui_instance, "pushButton_3"):
                main_ui_instance.pushButton_3.setEnabled(bool(allowed))
        else:
            if hasattr(main_ui_instance, "pushButton_3"):
                main_ui_instance.pushButton_3.setEnabled(False)
    except Exception:
        pass