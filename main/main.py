import datetime
import json
import sys
import time
from daily_initialization import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import qdarkstyle


# 使用了qdarkstyle
class ReselectTheClassScheduleWindow(QWidget):
    returnPressed = pyqtSignal(str)

    def __init__(self, week):
        super().__init__()
        self.week = week
        self.ui = None
        self.result = None

        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./ui_rcs.ui")
        self.ui.mon.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "monday"))
        self.ui.tue.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "tuesday"))
        self.ui.wed.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "wednesday"))
        self.ui.thur.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "thursday"))
        self.ui.fri.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "friday"))
        self.ui.pushButton.clicked.connect(self.on_push_button_clicked)
        self.ui.pushButton_2.clicked.connect(self.on_push_button_2_clicked)

    def on_push_button_clicked(self):
        try:
            self.result = \
                [i for i, v in self.week.items() if
                 tuple(v) == tuple(self.ui.textBrowser.toPlainText().strip().split())][0]
        except:
            self.result = "monday"

        self.ui.close()
        self.returnPressed.emit(self.result)

    def on_push_button_2_clicked(self):
        self.result = datetime.datetime.now().strftime("%A").lower()
        self.ui.close()
        self.returnPressed.emit(self.result)

    def on_radio_button_toggled(self, checked, text):
        if checked:
            a = ' '
            for i in self.week[text]:
                a += f"{i} "
            self.ui.textBrowser.setText(a)
            self.ui.textBrowser.setAlignment(Qt.AlignCenter)
            self.ui.textBrowser.repaint()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.screen_height = None
        self.screen_width = None
        self.ui = None
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./main_window.ui")


if __name__ == '__main__':
    now = datetime.datetime.now()
    week_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][now.weekday()]
    compare_time = compareTime()
    # 如果是周六日并且文件没有在今天被创建过的话就问一下
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 高DPI自适应
    if (week_name == 'saturday' or week_name == 'sunday') and compare_time is False:
        app = QApplication(sys.argv)
        ReselectTheClassSchduleWindow = ReselectTheClassScheduleWindow(
            json.loads(read_file('../data/Curriculum/lessons.json')))
        ReselectTheClassSchduleWindow.returnPressed.connect(lambda: None)  # 禁用自定义信号
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # 使用深色的qss
        ReselectTheClassSchduleWindow.ui.show()
        app.exec()
        week_name = ReselectTheClassSchduleWindow.result
    daily_initialization(week_name)  # 初始化daily_config文件
    # 进入主窗口
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # 使用qdarkstyle qss
    MainWindow.ui.show()
    app.exec()
