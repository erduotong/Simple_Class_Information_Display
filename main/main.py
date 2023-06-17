import datetime
import json
import sys
import time
from daily_initialization import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import qdarkstyle
import win32gui
import win32con
import schedule  # 用于计时
import threading


# 使用了qdarkstyle
class ReselectTheClassScheduleWindow(QDialog):
    # todo 不允许用户直接关闭窗口
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


# 参考用,字体自动大小切换
'''MainWindow(QMainWindow):
    # 定义两个信号：refresh_time_singal 和 adjust_textedit_size_singal
    refresh_time_singal = pyqtSignal()
    adjust_textedit_size_singal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.screen_height = None
        self.screen_width = None
        self.ui = None
        # 将 refresh_time_singal 信号连接到 refresh_time 槽函数
        self.refresh_time_singal.connect(self.refresh_time)
        # 将 adjust_textedit_size_singal 信号连接到 adjust_textedit_size 槽函数
        self.adjust_textedit_size_singal.connect(self.adjust_textedit_size)
        self.run_window()
        # 创建一个 QTimer 对象，并将它的 timeout 信号连接到 adjust_textedit_size 槽函数
        self.timer = QTimer()
        self.timer.timeout.connect(self.adjust_textedit_size)

    def run_window(self):
        self.ui = uic.loadUi("./main_window.ui")
        self.ui.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口
        rect = QDesktopWidget().availableGeometry()  # 初始化大小
        self.ui.resize(rect.width(), rect.height())
        # 设置位置
        h = win32gui.FindWindow("Progman", "Program Manager")  # 获取桌面窗口句柄
        win_hwnd = int(self.winId())  # 获取MainWindow窗口句柄
        win32gui.SetParent(win_hwnd, h)  # 将MainWindow窗口设置为桌面窗口的子窗口

    # 刷新时间的槽函数
    def refresh_time(self):
        self.ui.nowtime.setText(time.strftime("%Y/%m/%d %H:%M:%S ", time.localtime()) +
                                ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][
                                    time.localtime().tm_wday])
        self.ui.nowtime.repaint()

    # 调整字体大小和控件比例的槽函数
    def adjust_textedit_size(self):
        # 获取两个QTextEdit的文本内容
        message_text = self.ui.message.toPlainText()
        homework_text = self.ui.homework.toPlainText()
        # 计算两个QTextEdit的文本长度
        message_length = len(message_text)
        homework_length = len(homework_text)
        # 计算两个QTextEdit的文本长度比例
        if message_length + homework_length == 0:
            ratio = 0.5
        else:
            ratio = message_length / (message_length + homework_length)
        # 根据比例调整两个QTextEdit在msg_hw中的比例
        self.ui.msg_hw.layout().setStretch(0, ratio)
        self.ui.msg_hw.layout().setStretch(1, 1 - ratio)
        # 计算两个QTextEdit中最大的文本高度和宽度
        max_height = 0
        max_width = 0
        for textedit in [self.ui.message, self.ui.homework]:
            document_size = textedit.document().size().toSize()
            max_height = max(max_height, document_size.height())
            max_width = max(max_width, document_size.width())
        # 根据最大的文本高度和宽度调整字体大小
        if max_height > 0 and max_width > 0:
            new_font_size_width = min(max(self.ui.message.width() / max_width * self.ui.message.font().pointSize(), 10),
                                      20)
            new_font_size_height = min(
                max(self.ui.message.height() / max_height * self.ui.message.font().pointSize(), 10), 20)
            new_font_size = min(new_font_size_width, new_font_size_height)
            font = self.ui.message.font()
            font.setPointSize(new_font_size)
            self.ui.message.setFont(font)
            self.ui.homework.setFont(font)

    @pyqtSlot()
    def on_message_textChanged(self):
        if not self.timer.isActive():
            self.timer.start(60000)
        else:
            self.timer.stop()
            self.timer.start(60000)

    @pyqtSlot()
    def on_homework_textChanged(self):
        if not self.timer.isActive():
            self.timer.start(60000)
        else:
            self.timer.stop()
            self.timer.start(60000)

    @pyqtSlot()
    def on_message_textEditFinished(self):
        if self.timer.isActive():
            self.timer.stop()
            self.adjust_textedit_size()

    @pyqtSlot()
    def on_homework_textEditFinished(self):
        if self.timer.isActive():
            self.timer.stop()
            self.adjust_textedit_size()'''


class MainWindow(QMainWindow):
    refresh_time_singal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.screen_height = None
        self.screen_width = None
        self.ui = None
        self.refresh_time_singal.connect(self.refresh_time)
        self.run_window()

    def run_window(self):
        self.ui = uic.loadUi("./main_window.ui")
        self.ui.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口
        rect = QDesktopWidget().availableGeometry()  # 初始化大小
        self.ui.resize(rect.width(), rect.height())
        # 设置位置
        h = win32gui.FindWindow("Progman", "Program Manager")  # 获取桌面窗口句柄
        win_hwnd = int(self.winId())  # 获取MainWindow窗口句柄
        win32gui.SetParent(win_hwnd, h)  # 将MainWindow窗口设置为桌面窗口的子窗口
        # print(self.ui.__dict__)  # 调试用
        # todo 实现类似wallpaper engine的方式放置在桌面上(现在能基本实现 但是效果并不好)
        # todo 根据目前所看的虚拟桌面自动切换

    # 刷新时间
    def refresh_time(self):
        self.ui.nowtime.setText(time.strftime("%Y/%m/%d %H:%M:%S ", time.localtime()) +
                                ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][
                                    time.localtime().tm_wday])
        self.ui.nowtime.repaint()
    # todo 字体自动大小切换
    # todo 课表自动大小切换+自适应数量
    # todo 课表的下节课指示牌


if __name__ == '__main__':
    now = datetime.datetime.now()
    week_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][now.weekday()]
    compare_time = compareTime()
    # 如果是周六日并且文件没有在今天被创建过的话就问一下
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 高DPI自适应
    # 询问课表
    if (week_name == 'saturday' or week_name == 'sunday') and compare_time is False:
        app = QApplication(sys.argv)
        ReselectTheClassSchduleWindow = ReselectTheClassScheduleWindow(
            json.loads(read_file('../data/Curriculum/lessons.json')))
        ReselectTheClassSchduleWindow.returnPressed.connect(lambda: None)  # 禁用自定义信号
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # 使用深色的qss
        ReselectTheClassSchduleWindow.ui.show()
        app.exec()
        week_name = ReselectTheClassSchduleWindow.result
    else:  # 防止app忘记创建
        app = QApplication(sys.argv)
    config = json.loads(read_file("../data/program_config.json"))  # 把program_config读了
    daily_initialization(week_name)  # 初始化daily_config文件
    # 创建主窗口
    main_window = MainWindow()
    # 创建进程开始定时执行任务,传入刷新的秒数
    scheduled_task_thread = threading.Thread(target=run_schedule,
                                             args=(float(config["run_schedule_time"]), main_window,))
    scheduled_task_thread.start()
    pretreatmentHandle()  # 清理一下桌面
    # 进入主窗口
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # 设置qss 使用qdarkstyle qss
    main_window.ui.show()
    app.exec()
