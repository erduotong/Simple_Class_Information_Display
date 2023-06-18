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
from PyQt5 import QtGui


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


class MainWindow(QMainWindow):
    refresh_time_singal = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.screen_height = None
        self.screen_width = None
        self.ui = None
        self.laa = int(config["layout_adjustment_accuracy"])
        self.min_font_size = int(config["minimum_font_size"])
        self.max_font_size = int(config["maximum_font_size"])
        self.refresh_time_singal.connect(self.refresh_time)
        self.run_window()

    def run_window(self):
        self.ui = uic.loadUi("./main_window.ui")
        self.ui.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口
        rect = QDesktopWidget().availableGeometry()  # 初始化大小
        self.ui.resize(rect.width(), rect.height())
        self.refresh_time()  # 先进行初始化
        self.adjust_msg_hw_size()
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
        self.adjust_msg_hw_size()

    # 更新msg和hw两个的拉伸和字体大小
    def adjust_msg_hw_size(self):
        # 删除 message 和 homework 末尾的空行和空格
        message_text = self.ui.message.toPlainText().rstrip()
        homework_text = self.ui.homework.toPlainText().rstrip()
        message_cursor_pos = self.ui.message.textCursor().position()  # 保存当前光标位置 后面要用
        homework_cursor_pos = self.ui.homework.textCursor().position()
        homework_scroll_value = self.ui.homework.verticalScrollBar().value()  # 保留滚动条的位置
        message_scroll_value = self.ui.message.verticalScrollBar().value()
        self.ui.message.setPlainText(message_text)  # 设置删除空格后的文本
        self.ui.homework.setPlainText(homework_text)

        # 根据文本行数计算比值
        message_lines = get_visible_line_count(self.ui.message)
        homework_lines = get_visible_line_count(self.ui.homework)
        if message_lines + homework_lines == 0:
            ratio = 0.5
        else:
            ratio = message_lines / (message_lines + homework_lines)
        # 根据计算出的比值设置拉伸系数
        self.ui.msg_hw.layout().setStretchFactor(self.ui.message, int(ratio * self.laa))
        self.ui.msg_hw.layout().setStretchFactor(self.ui.homework, int((1 - ratio) * self.laa))
        # 字体大小设置
        # 如果行没变动就先不刷新(因为绝对不会出现滚动条或者过少)

        adjust_the_text_edit_font_size([self.ui.message, self.ui.homework], self.min_font_size, self.max_font_size)
        # 恢复滚动条的位置
        self.ui.homework.verticalScrollBar().setValue(homework_scroll_value)
        self.ui.message.verticalScrollBar().setValue(message_scroll_value)

        # 恢复光标位置
        message_cursor = self.ui.message.textCursor()  # message的位置
        if message_cursor_pos > len(message_text):
            message_cursor.movePosition(QtGui.QTextCursor.End)
        else:
            message_cursor.setPosition(message_cursor_pos)
        self.ui.message.setTextCursor(message_cursor)
        homework_cursor = self.ui.homework.textCursor()  # homework的位置
        # 如果光标位置超出文本长度，则将光标移动到文本末尾
        if homework_cursor_pos > len(homework_text):
            homework_cursor.movePosition(QtGui.QTextCursor.End)
        else:
            homework_cursor.setPosition(homework_cursor_pos)
        self.ui.homework.setTextCursor(homework_cursor)

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
    main_window = MainWindow(config)
    # 创建进程开始定时执行任务,传入刷新的秒数
    scheduled_task_thread = threading.Thread(target=run_schedule,
                                             args=(float(config["run_schedule_time"]), main_window,))
    scheduled_task_thread.start()
    pretreatmentHandle()  # 清理一下桌面
    # 进入主窗口
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # 设置qss 使用qdarkstyle qss
    main_window.ui.show()
    app.exec()
