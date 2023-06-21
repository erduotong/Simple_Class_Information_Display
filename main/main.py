import sys
import threading

import qdarkstyle
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from daily_initialization import *


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
    refresh_time_singal = pyqtSignal()  # 更新时间
    run_adaptive_text_edit_manually = pyqtSignal()  # 自适应homework和message的字体大小和比例 手动触发

    # todo 这个信号↑要绑定一个按钮的

    def __init__(self, program_config):
        super().__init__()
        self.refresh_edit_size = QtCore.QTimer()  # 设置一个计时器
        self.refresh_edit_size.setInterval(program_config["text_edit_refresh_time"] * 1000)  # 设置停止编辑刷新的时间
        # 绑定信号&槽
        self.refresh_edit_size.timeout.connect(self.manually_refresh_the_text_edit_font)  # 超时后连接到更新字体
        self.refresh_time_singal.connect(self.refresh_time)
        self.run_adaptive_text_edit_manually.connect(self.manually_refresh_the_text_edit_font)
        # 变量初始化
        self.screen_height = None
        self.screen_width = None
        self.ui = None
        self.daily_config = None
        self.lessons_with_slots = []
        # config需要用的内容初始化
        self.laa = int(program_config["layout_adjustment_accuracy"])
        self.min_font_size = int(program_config["minimum_font_size"])
        self.max_font_size = int(program_config["maximum_font_size"])
        self.run_window()  # 运行!

    def run_window(self):
        self.ui = uic.loadUi("./main_window.ui")
        self.ui.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口
        rect = QDesktopWidget().availableGeometry()  # 初始化大小
        self.ui.resize(rect.width(), rect.height())
        self.refresh_time()  # 先进行初始化
        self.adjust_msg_hw_size()
        adjust_font_size(self.ui.nowtime, config["time_font_size"])  # 设置时间显示的字体大小
        # 绑定要用到ui的信号和槽
        self.ui.message.textChanged.connect(self.on_text_changed)  # 两个文本框的超时信号
        self.ui.homework.textChanged.connect(self.on_text_changed)
        # print(self.ui.__dict__)  # 调试用
        self.initialize_the_class_schedule()  # 测试课表初始化函数

    # todo 粘贴自动转换成纯文本
    # todo 实现类似wallpaper engine的方式放置在桌面上(现在能基本实现 但是效果并不好)
    # todo 根据目前所看的虚拟桌面自动切换
    # todo 课表自动大小切换+自适应数量
    # todo 课表的下节课指示牌
    # todo 可编辑颜色的message

    # 刷新时间
    def refresh_time(self):
        self.ui.nowtime.setText(time.strftime("%Y/%m/%d %H:%M:%S ", time.localtime()) +
                                ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][
                                    time.localtime().tm_wday])
        self.ui.nowtime.repaint()

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
        # 恢复滚动条的位置
        self.ui.homework.verticalScrollBar().setValue(homework_scroll_value)
        self.ui.message.verticalScrollBar().setValue(message_scroll_value)

    # 计时器的函数 如果被改变了那就开始计时
    def on_text_changed(self):
        # 如果定时器正在运行，则停止定时器
        if self.refresh_edit_size.isActive():
            self.refresh_edit_size.stop()
        # 重新启动定时器
        self.refresh_edit_size.start()

    # 手动触发字体更新
    def manually_refresh_the_text_edit_font(self):
        self.ui.message.textChanged.disconnect(self.on_text_changed)  # 先断开防止重复触发
        self.ui.homework.textChanged.disconnect(self.on_text_changed)
        self.refresh_edit_size.stop()  # 先把计时器关了
        self.adjust_msg_hw_size()  # 然后再更新一下
        # 重新连接textChanged信号与槽函数
        self.ui.message.textChanged.connect(self.on_text_changed)
        self.ui.homework.textChanged.connect(self.on_text_changed)

    # 为课表添加内容 排除”课间“以及special内的内容 并且添加browser
    # 随后为这些browser添加对应的内容 并且开始计时器
    # 然后就丢到移动函数去了
    # 生成→自适应→显示(可重复)
    # 计算并且开始计时
    def initialize_the_class_schedule(self):
        # 先把要加入的数量判断出来
        self.lessons_with_slots = []  # 初始化一下
        lessons = json.loads(read_file("../data/Curriculum/lessons.json"))  # 读一下lessons后面判断
        self.daily_config = json.loads(read_file("../data/daily_config.json"))  # 读入daily_config
        for i in self.daily_config["lessons_list"]:
            if i["name"] in lessons["special"] or i["name"] == '课间':  # 特殊课程和课间不能入内
                continue
            self.lessons_with_slots.append(i["name"])  # 加!
        # 初始化lessons_list
        # 操作的是lessons_list这个widget 先清空其中所有的QTextBrowser
        for i in self.ui.lessons_list.findChildren(QtWidgets.QTextBrowser):
            i.deleteLater()
        # 添加第一个用于显示课间等的widget(一定有的) 名称为common_course_slots
        text_browser = QtWidgets.QTextBrowser(self.ui.lessons_list)
        text_browser.setObjectName("common_course_slots")
        text_browser.setText("s")  # todo test!!!!!!
        self.ui.lessons_list.layout().addWidget(text_browser)
        # 添加剩余len lessons_with_slots个
        for i in range(1, len(self.lessons_with_slots) + 1):
            text_browser = QtWidgets.QTextBrowser(self.ui.lessons_list)
            text_browser.setObjectName(f"lesson{i}")
            text_browser.setText(str(i))  # todo test!!!!!
            self.ui.lessons_list.layout().addWidget(text_browser)
        # 最后刷新一下
        self.ui.lessons_list.repaint()


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
    # 进入主窗口
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # 设置qss 使用qdarkstyle qss
    main_window.ui.show()
    app.exec()
