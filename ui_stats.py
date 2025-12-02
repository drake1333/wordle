from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import config  
from database import get_user_stats

class StatisticUI(object):
    def __init__(self, window_refs):
        self.MainWindowStat = window_refs["stat"]
        self.MainWindowMain = window_refs["main"]
        
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(480, 420)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.outer_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.outer_layout.setContentsMargins(20, 20, 20, 20)
        self.outer_layout.setSpacing(15)

        top_bar = QtWidgets.QHBoxLayout()

        self.back_btn = QtWidgets.QPushButton("Back")
        self.back_btn.setFixedSize(80, 32)
        self.back_btn.clicked.connect(self.back)
        top_bar.addWidget(self.back_btn)

        self.title = QtWidgets.QLabel("Statistics")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignCenter)

        top_bar.addStretch()
        top_bar.addWidget(self.title)
        top_bar.addStretch()

        self.outer_layout.addLayout(top_bar)

        stats_container = QtWidgets.QWidget(self.centralwidget)
        stats_layout = QtWidgets.QVBoxLayout(stats_container)
        stats_layout.setSpacing(10)

        label_font = QFont()
        label_font.setPointSize(13)

        self.label_name = QtWidgets.QLabel("Name: -")
        self.label_uid = QtWidgets.QLabel("UID: -")
        self.label_wins = QtWidgets.QLabel("Wins: 0")
        self.label_losses = QtWidgets.QLabel("Lose: 0")
        self.label_pct = QtWidgets.QLabel("Win/Lose Percentage: 0%")
        self.label_lastdaily = QtWidgets.QLabel("Last Daily: -")

        stat_labels = [
            self.label_name,
            self.label_uid,
            self.label_wins,
            self.label_losses,
            self.label_pct,
            self.label_lastdaily
        ]

        for lbl in stat_labels:
            lbl.setFont(label_font)
            lbl.setAlignment(Qt.AlignCenter)
            stats_layout.addWidget(lbl)

        self.outer_layout.addWidget(stats_container)

        MainWindow.setCentralWidget(self.centralwidget)

    def load_stats(self):

        if not config.CURRENT_USER:
            self.label_name.setText("Name: -")
            self.label_uid.setText("UID: -")
            self.label_wins.setText("Wins: 0")
            self.label_losses.setText("Lose: 0")
            self.label_pct.setText("Win/Lose Percentage: 0%")
            self.label_lastdaily.setText("Last Daily: -")
            return

        stats = get_user_stats(config.CURRENT_USER)
        wins = stats.get("wins", 0)
        losses = stats.get("losses", 0)
        total = wins + losses

        percentage = (wins / total * 100) if total > 0 else 0
        percentage = round(percentage, 2)

        self.label_name.setText(f"Name: {config.CURRENT_USER}")
        self.label_uid.setText(f"UID: {config.CURRENT_USER}")
        self.label_wins.setText(f"Wins: {wins}")
        self.label_losses.setText(f"Lose: {losses}")
        self.label_pct.setText(f"Win/Lose Percentage: {percentage}%")

        last = stats.get("last_daily_play")
        self.label_lastdaily.setText(f"Last Daily: {last}" if last else "Last Daily: -")

    def back(self):
        try:
            self.MainWindowStat.hide()
            self.MainWindowMain.show()
        except:
            pass