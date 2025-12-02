import sys
from PyQt5 import QtWidgets

from database import ensure_statistics_table
from utils import load_options, apply_options, refresh_daily_button_state
from ui_main import MainWindowUI
from ui_auth import LoginUI, SignupUI
from ui_stats import StatisticUI
from ui_wordle import FourWordle, FiveWordle, SixWordle, DailyWordUI

ensure_statistics_table()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    apply_options(load_options())

    MainWindowMain = QtWidgets.QMainWindow()
    DialogWindowLogin = QtWidgets.QMainWindow()
    SignupWindow = QtWidgets.QMainWindow()
    MainWindowStat = QtWidgets.QMainWindow()
    MainWindow4 = QtWidgets.QMainWindow()
    MainWindow5 = QtWidgets.QMainWindow()
    MainWindow6 = QtWidgets.QMainWindow()
    MainWindowDaily = QtWidgets.QMainWindow()
    
    window_refs = {
        "main": MainWindowMain,
        "login": DialogWindowLogin,
        "signup": SignupWindow,
        "stat": MainWindowStat,
        "4": MainWindow4,
        "5": MainWindow5,
        "6": MainWindow6,
        "daily": MainWindowDaily,
    }

    ui4 = FourWordle()
    ui5 = FiveWordle()
    ui6 = SixWordle()
    uiDaily = DailyWordUI()
    
    window_refs["ui4"] = ui4
    window_refs["ui5"] = ui5
    window_refs["ui6"] = ui6
    window_refs["uiDaily"] = uiDaily
    
    uiStat = StatisticUI(window_refs)
    window_refs["uiStat"] = uiStat
    
    ui = MainWindowUI(window_refs, main_ui_instance=None)
    
    uiLogin = LoginUI(window_refs, main_ui_instance=ui)
    uiSignup = SignupUI(window_refs)

    ui.main_ui_instance = ui

    ui.setupUi(MainWindowMain)
    uiLogin.setupUi(DialogWindowLogin)
    uiSignup.setupUi(SignupWindow)
    uiStat.setupUi(MainWindowStat)
    
    ui4.setupUi(MainWindow4, MainWindowMain)
    ui5.setupUi(MainWindow5, MainWindowMain)
    ui6.setupUi(MainWindow6, MainWindowMain)
    uiDaily.setupUi(MainWindowDaily, MainWindowMain, ui)

    DialogWindowLogin.show()
    refresh_daily_button_state(ui)
    
    sys.exit(app.exec_())