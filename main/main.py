# -*- coding: utf-8 -*-
import copy
import sys
import threading
from datetime import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from daily_initialization import *
import time
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QRegExpValidator
from rcs import Ui_Dialog
from main_window import Ui_MainWindow
from settings_page import Ui_settings


# 使用了qdarkstyle
class ReselectTheClassScheduleWindow(QDialog, Ui_Dialog):
    returnPressed = pyqtSignal(str)

    def __init__(self, week):
        super().__init__()
        self.week = week
        self.result = None
        self.setupUi(self)
        self.show()
        self.init_ui()
        self.singal1 = None

    def init_ui(self):
        self.monday.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "monday"))
        self.tuesday.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "tuesday"))
        self.wednesday.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "wednesday"))
        self.thursday.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "thursday"))
        self.friday.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "friday"))
        self.saturday.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "saturday"))
        self.sunday.toggled.connect(lambda checked: self.on_radio_button_toggled(checked, "sunday"))
        self.pushButton.clicked.connect(self.on_push_button_clicked)
        self.pushButton_2.clicked.connect(self.on_push_button_2_clicked)

    def on_push_button_clicked(self):
        try:
            self.result = \
                [i for i, v in self.week.items() if
                 tuple(v) == tuple(self.textBrowser.toPlainText().strip().split())][0]
        except:
            self.result = "monday"
        self.singal1 = 'clicked'
        self.close()
        self.returnPressed.emit(self.result)

    def on_push_button_2_clicked(self):
        self.result = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][
            datetime.now().weekday()]
        self.singal1 = 'clicked'
        self.close()
        self.returnPressed.emit(self.result)

    def on_radio_button_toggled(self, checked, text):
        if checked:
            a = ' '
            for i in self.week[text]:
                a += f"{i} "
            self.textBrowser.setText(a)
            self.textBrowser.setAlignment(Qt.AlignCenter)
            self.textBrowser.repaint()

    def closeEvent(self, event):
        if self.singal1 == 'clicked':
            event.accept()
        else:
            event.ignore()


class SettingsPage(QWidget, Ui_settings):
    singal_go_to_the_settings_page = pyqtSignal()
    singal_exit_SettingsPage = pyqtSignal()
    signal_switch_to_the_interface = pyqtSignal()  # 在切换到设置页的时候要干啥的信号 现在是打开关于页

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 加载UI
        self.tabWidget.findChild(QTabBar).hide()
        # 初始化变量
        self.program_config_dict = None
        self.daily_config_dict = None
        self.lessons_dict = None
        self.time_dict = None
        self.program_config_dict_mirror = None
        self.daily_config_dict_mirror = None
        self.lessons_dict_mirror = None
        self.time_dict_mirror = None
        self.program_config_opened: bool = False
        self.daily_config_opened: bool = False
        self.lessons_opened: bool = False
        self.about_opened: bool = False
        self.time_opened: bool = False
        # 绑定信号和槽
        self.signal_switch_to_the_interface.connect(self.open_about)
        self.singal_go_to_the_settings_page.connect(self.initialize_after_entering)
        self.not_save_exit.clicked.connect(self.do_not_save_and_exit)
        self.save_exit.clicked.connect(self.save_and_exit)
        self.to_program_config.clicked.connect(self.open_program_config)
        self.to_daily_config.clicked.connect(self.open_daily_config)
        self.to_lessons.clicked.connect(self.open_lessons)
        self.to_about.clicked.connect(self.open_about)
        self.to_time.clicked.connect(self.open_time)
        self.to_resetting.clicked.connect(self.open_resetting)
        # ================
        self.daily_config_tab_widget.currentChanged.connect(self.daily_config_tab_changed)

    # 进入后载入一些设置啥的初始化
    def initialize_after_entering(self):
        # 根据上一次保存的内容来决定切换到什么地方并且准备初始化
        self.program_config_dict = json.loads(read_file('../data/program_config.json'))
        self.daily_config_dict = json.loads(read_file('../data/daily_config.json'))
        self.lessons_dict = json.loads(read_file('../data/Curriculum/lessons.json'))
        self.time_dict = json.loads(read_file('../data/Curriculum/time.json'))
        # 设置镜像,后续要进行操作
        self.program_config_dict_mirror = copy.deepcopy(self.program_config_dict)
        self.daily_config_dict_mirror = copy.deepcopy(self.daily_config_dict)
        self.lessons_dict_mirror = copy.deepcopy(self.lessons_dict)
        self.time_dict_mirror = copy.deepcopy(self.time_dict)
        self.now_version.setText(f"版本号: {self.program_config_dict['version']}")  # 替换 关于 内的版本号
        self.program_config_opened: bool = False
        self.daily_config_opened: bool = False
        self.lessons_opened: bool = False
        self.time_opened: bool = False

    # //////////////////
    # program_config编辑

    def open_program_config(self):
        self.tabWidget.setCurrentIndex(0)
        if not self.program_config_opened:
            self.program_config_opened = True
            self.initialize_program_config_widget()

    def initialize_program_config_widget(self):
        # 首先清空 然后计算出最大和最小高度 框死
        # 清空其中的所有widget保险
        for i in self.program_config_show_area.findChildren(QWidget):
            i.deleteLater()
        # 用于翻译对照
        compare_dict = {
            "backup_slots<--daily_config": "今日配置文件备份槽位数",
            "backup_slots<--program_config": "程序配置文件备份槽位数",
            "backup_slots<--time": "课程默认时间文件备份槽位数",
            "backup_slots<--lessons": "课表存储文件备份槽位数",
            "refresh_time": "逻辑刷新时间(秒)",
            "layout_adjustment_accuracy": "自适应比例精度",
            "minimum_font_size": "最小自适应字体大小",
            "maximum_font_size": "最大自适应字体大小",
            "time_font_size": "时间显示器字体大小",
            "text_edit_refresh_time": "文本编辑后自动自适应间隔",
            "the_window_changes_the_refresh_time": "窗口改变后自动自适应间隔",
            "now_indicator_text": "现在课程指示器显示文本",
            "next_indicator_text": "下节课程指示器显示文本"
        }

        # 递归的函数
        def add_widget(a: dict, top_key):

            for key, value in a.items():
                # 递归,保证嵌套正常
                if isinstance(value, dict):
                    if top_key is not None:
                        add_widget(value, f"{top_key}-{key}")
                    else:
                        add_widget(value, key)
                    continue
                # version不显示
                if key == "version":
                    continue
                # 替换成单一字符串
                if top_key is not None:
                    key = f"{top_key}<--{key}"
                # 根据value和key生成widget
                widget = QWidget()
                widget.setFixedHeight(self.program_config_scrollarea.height() // 11)
                # 为widget内添加label
                layout = QHBoxLayout()  # 设置水平布局
                label = QLabel(compare_dict.get(key))
                font = QFont("黑体")
                label.setFont(font)
                label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                layout.addWidget(label)
                # 添加编辑框 判断类型并设置能输入什么东西
                line_edit = QLineEdit()
                line_edit.setText(str(value))  # 添加文本
                # 判断类型
                if isinstance(value, float):
                    validator = QDoubleValidator()
                elif isinstance(value, int):
                    validator = QIntValidator()
                else:
                    validator = QRegExpValidator()
                line_edit.setValidator(validator)  # 添加类型限制,加强鲁棒性
                line_edit.textChanged.connect(lambda text, key1=key, value_type=type(value):
                                              self.update_program_config_dict(text, key1, value_type))
                layout.addWidget(line_edit)
                widget.setLayout(layout)  # 添加布局
                self.program_config_show_area.layout().addWidget(widget)  # 加入widget

        add_widget(self.program_config_dict, None)  # 传入None 现在就是在遍历top key
        # 自适应字体大小
        for i in self.program_config_show_area.findChildren(QLabel):
            adaptive_label_font_size(i, 50, 1)
        for i in self.program_config_show_area.findChildren(QLineEdit):
            adaptive_label_font_size(i, 50, 1)

            # 字体变化的时候更新program_config这个dict

    def update_program_config_dict(self, text, key, value_type):
        if text == '':
            return
        if value_type == int:
            text = int(text)
        elif value_type == float:
            text = float(text)
        else:
            text = str(text)
        # 更改字典的值
        key = key.split("<--")
        dict1 = self.program_config_dict
        for i in key[:-1]:
            dict1 = dict1[i]
        dict1[key[-1]] = text

    # //////////////////
    # daily_config编辑

    def open_daily_config(self):
        self.tabWidget.setCurrentIndex(1)
        if not self.daily_config_opened:
            self.daily_config_tab_changed(0)
            # TODO 初始化daily_config页 用QTableWidget
            self.daily_config_opened = True

    def daily_config_tab_changed(self, index):
        # 根据index判断要进行什么操作
        # 如果index还没有进行过初始化，那么就进行一下初始化
        # 否则就该干嘛干嘛(比如重排序?
        print(index)

    # //////////////////
    # 课程编辑

    def open_lessons(self):
        self.tabWidget.setCurrentIndex(2)
        if not self.lessons_opened:
            # TODO 初始化lessons页
            self.lessons_opened = True

    # //////////////////
    # 关于显示

    def open_about(self):
        self.tabWidget.setCurrentIndex(3)
        if not self.about_opened:
            self.about_opened = True
            self.initialize_about_widget()

    def initialize_about_widget(self):
        # 自适应一下字体大小
        for i in self.show_about.findChildren(QLabel):
            adaptive_label_font_size(i, 50, 1)

    # //////////////////
    # 时间编辑

    def open_time(self):
        self.tabWidget.setCurrentIndex(4)
        if not self.time_opened:
            # TODO 初始化time页
            self.time_opened = True

    # //////////////////
    # 重置

    def open_resetting(self):
        self.tabWidget.setCurrentIndex(5)
        # TODO 为resetting页面加UI

    # //////////////////
    # 保存并退出
    def save_and_exit(self):
        # 保存文件 如果发生了更改就要备份 然后再覆写
        if self.program_config_dict != self.program_config_dict_mirror:
            backup('../data/program_config.json', '../data/backup/program_config',
                   self.program_config_dict["backup_slots"]["program_config"])
            write_file('../data/program_config.json',
                       json.dumps(self.program_config_dict, ensure_ascii=False, indent=4))
        if self.daily_config_dict != self.daily_config_dict_mirror:
            backup('../data/daily_config.json', '../data/backup/daily_config',
                   self.program_config_dict["backup_slots"]["daily_config"])
            write_file('../data/daily_config.json',
                       json.dumps(self.daily_config_dict, ensure_ascii=False, indent=4))
        if self.time_dict != self.time_dict_mirror:
            backup('../data/Curriculum/time.json', '../data/backup/time',
                   self.program_config_dict["backup_slots"]["time"])
            write_file('../data/Curriculum/time.json',
                       json.dumps(self.time_dict, ensure_ascii=False, indent=4))
        if self.lessons_dict != self.lessons_dict_mirror:
            backup('../data/Curriculum/lessons.json', '../data/backup/lessons',
                   self.program_config_dict["backup_slots"]["lessons"])
            write_file('../data/Curriculum/lessons.json',
                       json.dumps(self.lessons_dict, ensure_ascii=False, indent=4))
        # 减少内存占用
        self.remove_unwanted()
        self.singal_exit_SettingsPage.emit()  # 退出!

    # 不保存并退出
    def do_not_save_and_exit(self):
        # 减少内存占用
        self.remove_unwanted()
        # 啥也不用干
        self.singal_exit_SettingsPage.emit()  # 退出!

    # 删除一些之后要重新生成的东西以减少内存占用(是否需要多线程存疑
    def remove_unwanted(self):
        self.program_config_dict = None
        self.daily_config_dict = None
        self.lessons_dict = None
        self.time_dict = None
        self.program_config_dict_mirror = None
        self.daily_config_dict_mirror = None
        self.lessons_dict_mirror = None
        self.time_dict_mirror = None
        # 控件大小相关
        maxsize = 16777215
        self.program_config_show_area.setMaximumSize(maxsize, maxsize)


class MainWindow(QMainWindow, Ui_MainWindow):
    refresh_time_singal = pyqtSignal()  # 更新时间
    run_adaptive_text_edit_manually = pyqtSignal()  # 自适应homework和message的字体大小和比例 手动触发
    update_the_course_indicator_singal = pyqtSignal(int)  # 刷新课程指示器用的信号

    def __init__(self, program_config):
        super().__init__()
        self.setupUi(self)
        # 其他页
        self.settings_page = SettingsPage()  # 设置页面
        self.stackedWidget.addWidget(self.settings_page)
        # 设置计时器
        self.refresh_edit_size = QtCore.QTimer()  # 设置一个计时器
        self.refresh_edit_size.setInterval(program_config["text_edit_refresh_time"] * 1000)  # 设置停止编辑刷新的时间
        # 绑定信号&槽
        self.settings_page.singal_exit_SettingsPage.connect(self.exit_settings_page)  # 绑定设置退出的信号
        self.settings_.clicked.connect(self.show_settings_page)
        self.refresh_edit_size.timeout.connect(self.manually_refresh_the_text_edit_font)  # 超时后连接到更新字体
        self.refresh_time_singal.connect(self.refresh_time)
        self.run_adaptive_text_edit_manually.connect(self.manually_refresh_the_text_edit_font)
        self.update_the_course_indicator_singal.connect(self.refresh_the_course_indicator)
        # 变量初始化
        self.window_resized: bool = False  # 窗口大小曾经改变过
        self.settings_is_open: bool = False  # 设置页面开启状态
        self.screen_height = None
        self.screen_width = None
        self.lessons_status = None
        self.daily_config = self.daily_config = json.loads(read_file("../data/daily_config.json"))
        self.lessons_with_slots = []
        self.next_lesson = None  # 存储的是lessons_list的下标
        self.time_to_next_len = None
        self.lessons_slots = []
        self.now_lesson_indicator = 'hide'  # 防止后面出现找不到就识别错误
        self.next_lesson_indicator = 'hide'
        # config需要用的内容初始化
        self.laa = int(program_config["layout_adjustment_accuracy"])
        self.min_font_size = int(program_config["minimum_font_size"])
        self.max_font_size = int(program_config["maximum_font_size"])
        self.program_config = program_config
        self.setWindowTitle("Simple Class Information Display")
        rect = QDesktopWidget().availableGeometry()  # 初始化大小
        self.resize(rect.width(), rect.height())
        adjust_font_size(self.nowtime, config["time_font_size"])  # 设置时间显示的字体大小
        # 绑定要用到信号和槽
        self.homework.setPlainText(self.daily_config['backup']['homework'])  # 加载之前的文本
        self.message.setPlainText(self.daily_config['backup']['msg'])
        self.message.textChanged.connect(self.on_text_changed)  # 两个文本框的超时信号
        self.homework.textChanged.connect(self.on_text_changed)
        self.refresh_font_.clicked.connect(self.run_adaptive_text_edit_manually)
        # QTimer区
        self.resize_timer = QTimer(self)  # 刷新窗口的QTimer
        self.resize_timer.setInterval(int(program_config['the_window_changes_the_refresh_time'] * 1000))
        self.resize_timer.timeout.connect(self.on_resize_timeout)
        # 设置快捷键
        self.refresh_font_.setShortcut('F5')
        # 加入两个显示的QLabel
        self.layout().addWidget(
            initialize_label_indicator("next_lesson_indicator", program_config['next_indicator_text']))
        self.layout().addWidget(
            initialize_label_indicator("now_lesson_indicator", program_config['now_indicator_text']))
        # print(self.__dict__)  # 调试用
        self.stackedWidget.setCurrentIndex(0)  # 切换到page0
        self.show()  # 显示
        # 开始套娃 执行要渲染窗口完毕后的操作
        QtCore.QTimer.singleShot(0, self.after_init)

    # 需要渲染窗口完毕后执行的函数
    def after_init(self):
        self.initialize_the_class_schedule()
        QtCore.QTimer.singleShot(0, self.after_after_init)

    # 真的是醉了......
    def after_after_init(self):
        self.run_adaptive_text_edit_manually.emit()
        for i in self.lessons_slots:
            adjust_the_text_edit_font_size([self.findChild(QTextBrowser, i)], self.min_font_size, self.max_font_size)
        QtCore.QTimer.singleShot(0, self.adjust_msg_hw_size)
        QtCore.QTimer.singleShot(0, self.refresh_time)  # 强制刷新时间

    # 刷新时间
    def refresh_time(self):
        self.nowtime.setText(time.strftime("%Y/%m/%d %H:%M:%S ", time.localtime()) +
                             ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][
                                 time.localtime().tm_wday])
        self.time_to_next_refresh()
        self.nowtime.repaint()

    # 更新msg和hw两个的拉伸和字体大小
    def adjust_msg_hw_size(self):
        # 删除 message 和 homework 末尾的空行和空格
        message_text = self.message.toPlainText().rstrip()
        homework_text = self.homework.toPlainText().rstrip()
        message_cursor_pos = self.message.textCursor().position()  # 保存当前光标位置 后面要用
        homework_cursor_pos = self.homework.textCursor().position()
        homework_scroll_value = self.homework.verticalScrollBar().value()  # 保留滚动条的位置
        message_scroll_value = self.message.verticalScrollBar().value()
        self.message.setPlainText(message_text)  # 设置删除空格后的文本
        self.homework.setPlainText(homework_text)
        # 根据文本行数计算比值
        message_lines = get_visible_line_count(self.message)
        homework_lines = get_visible_line_count(self.homework)
        if message_lines + homework_lines == 0:
            ratio = 0.5
        else:
            ratio = message_lines / (message_lines + homework_lines)
        # 根据计算出的比值设置拉伸系数
        self.msg_hw.layout().setStretchFactor(self.message, int(ratio * self.laa))
        self.msg_hw.layout().setStretchFactor(self.homework, int((1 - ratio) * self.laa))
        # 字体大小设置
        adjust_the_text_edit_font_size([self.message, self.homework], self.min_font_size, self.max_font_size)
        # 恢复光标位置
        message_cursor = self.message.textCursor()  # message的位置
        if message_cursor_pos > len(message_text):
            message_cursor.movePosition(QtGui.QTextCursor.End)
        else:
            message_cursor.setPosition(message_cursor_pos)
        self.message.setTextCursor(message_cursor)
        homework_cursor = self.homework.textCursor()  # homework的位置
        # 如果光标位置超出文本长度，则将光标移动到文本末尾
        if homework_cursor_pos > len(homework_text):
            homework_cursor.movePosition(QtGui.QTextCursor.End)
        else:
            homework_cursor.setPosition(homework_cursor_pos)
        self.homework.setTextCursor(homework_cursor)
        # 恢复滚动条的位置
        self.homework.verticalScrollBar().setValue(homework_scroll_value)
        self.message.verticalScrollBar().setValue(message_scroll_value)

    # 计时器的函数 如果被改变了那就开始计时
    def on_text_changed(self):
        # 重启计时器
        self.refresh_edit_size.start()

    # 手动触发字体更新
    def manually_refresh_the_text_edit_font(self):
        self.message.textChanged.disconnect()  # 先断开防止重复触发
        self.homework.textChanged.disconnect()
        self.refresh_edit_size.stop()  # 先把计时器关了
        self.adjust_msg_hw_size()  # 然后再更新一下
        # 备份一下其中的内容
        self.daily_config["backup"]["msg"] = self.message.toPlainText()
        self.daily_config["backup"]["homework"] = self.homework.toPlainText()
        write_file("../data/daily_config.json", json.dumps(self.daily_config, ensure_ascii=False, indent=4))
        # 重新连接textChanged信号与槽函数
        self.message.textChanged.connect(self.on_text_changed)
        self.homework.textChanged.connect(self.on_text_changed)

    # 添加课表
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
        for i in self.lessons_list.findChildren(QtWidgets.QTextBrowser):
            i.deleteLater()
        self.lessons_list.setMaximumHeight(self.lessons_list.height())  # 防止超出距离
        # 添加第一个用于显示课间等的widget(一定有的) 名称为common_course_slots
        self.lessons_slots = []
        text_browser = QtWidgets.QTextBrowser(self.lessons_list)
        text_browser.setObjectName("common_course_slots")
        self.lessons_slots.append("common_course_slots")
        text_browser.setText(" ")
        text_browser.setAlignment(Qt.AlignHCenter)
        self.lessons_list.layout().addWidget(text_browser)
        # 添加剩余len lessons_with_slots个
        for i in range(1, len(self.lessons_with_slots) + 1):
            text_browser = QtWidgets.QTextBrowser(self.lessons_list)
            text_browser.setObjectName(f"lesson{i}")
            text_browser.setText(self.lessons_with_slots[i - 1])
            text_browser.setAlignment(Qt.AlignHCenter)
            self.lessons_slots.append(f"lesson{i}")
            self.lessons_list.layout().addWidget(text_browser)

    # 展示到下一个的事件
    def time_to_next_refresh(self) -> None:
        # 先判断时间 然后进行处理
        # 如果没有特殊变化那就不刷新 否则就进行一个刷新
        now_time = datetime.now()
        # 如果还没开始第一节课的情况 为0
        if now_time < time_to_datetime(self.daily_config["lessons_list"][0]["start"], now_time):
            if self.lessons_status != 0:
                self.lessons_status = 0
                self.update_the_course_indicator_singal.emit(0)
            # 更新一下课程表的指示器
            self.time_to_next.setPlainText(
                f"距离{self.daily_config['lessons_list'][0]['name']}还有{format_timedelta(time_to_datetime(self.daily_config['lessons_list'][0]['start'], now_time) - now_time)}"
            )
        # 上完最后一节课的情况 为1
        elif now_time > time_to_datetime(self.daily_config["lessons_list"][-1]["end"], now_time):
            if self.lessons_status != 1:
                self.lessons_status = 1
                self.update_the_course_indicator_singal.emit(1)
            self.time_to_next.setPlainText(
                f"已放学{format_timedelta(now_time - time_to_datetime(self.daily_config['lessons_list'][-1]['end'], now_time))}"
            )
        # 正常 正在上课的情况 为2
        else:
            for index, lesson in enumerate(self.daily_config["lessons_list"]):
                if time_to_datetime(lesson["start"], now_time) <= now_time < time_to_datetime(lesson["end"], now):
                    if self.next_lesson != index + 1:
                        self.next_lesson = index + 1
                        self.update_the_course_indicator_singal.emit(2)
                    break
            if self.next_lesson == len(self.daily_config["lessons_list"]):  # 超过列表最大长度了
                self.time_to_next.setPlainText(
                    f"距离放学还有{format_timedelta(time_to_datetime(self.daily_config['lessons_list'][self.next_lesson - 1]['end'], now_time) - now_time)}")
            else:
                self.time_to_next.setPlainText(
                    f"距离{self.daily_config['lessons_list'][self.next_lesson]['name']}还有{format_timedelta(time_to_datetime(self.daily_config['lessons_list'][self.next_lesson]['start'], now_time) - now_time)}"
                )

        # 设置对齐方式
        self.time_to_next.setAlignment(Qt.AlignCenter)
        # 自适应大小
        if len(self.time_to_next.toPlainText()) != self.time_to_next_len or self.time_to_next.verticalScrollBar().isVisible():
            self.time_to_next_len = len(self.time_to_next.toPlainText())
            # 自适应字体大小
            adjust_the_text_edit_font_size([self.time_to_next], self.min_font_size, self.max_font_size)

    # 刷新这个课程以及下一个课程的指示器
    # 这是一坨
    def refresh_the_course_indicator(self, mode) -> None:
        """
        :param mode:0:第一节课之前 1:放学后 2:正常 位于start和end之间
        :return: None
        """
        now_time = datetime.now()
        if mode == 0:
            if self.daily_config['lessons_list'][0]['name'] in self.lessons_with_slots:
                # 指向lesson1(next)
                self.now_lesson_indicator = 'hide'
                self.next_lesson_indicator = self.findChild(QTextBrowser, 'lesson1')
                self.refresh_the_course_indicator_position()
            else:
                text_browser = self.findChild(QTextBrowser, "common_course_slots")
                text_browser.setPlainText(self.daily_config['lessons_list'][0]['name'])
                text_browser.setAlignment(Qt.AlignHCenter)
                adjust_the_text_edit_font_size([text_browser], self.min_font_size, self.max_font_size)
                # 指向common_course_slots(next)
                self.now_lesson_indicator = 'hide'
                self.next_lesson_indicator = self.findChild(QTextBrowser, 'common_course_slots')
                self.refresh_the_course_indicator_position()
            return
        elif mode == 1:
            text_browser = self.findChild(QTextBrowser, "common_course_slots")
            text_browser.setPlainText("放学")
            text_browser.setAlignment(Qt.AlignHCenter)
            adjust_the_text_edit_font_size([text_browser], self.min_font_size, self.max_font_size)
            # 指向common_course_slots(now)
            self.now_lesson_indicator = self.findChild(QTextBrowser, 'common_course_slots')
            self.next_lesson_indicator = 'hide'
            self.refresh_the_course_indicator_position()
            return
        lesson_index = 0
        lesson_now: dict = {}
        for index, lesson in enumerate(self.daily_config["lessons_list"]):
            if time_to_datetime(lesson["start"], now_time) <= now_time < time_to_datetime(lesson["end"], now):
                lesson_now = lesson
                lesson_index = index
                break
        if lesson_now['name'] not in self.lessons_with_slots:  # 要用到common槽位的情况
            text_browser = self.findChild(QTextBrowser, "common_course_slots")
            text_browser.setPlainText(lesson_now['name'])
            text_browser.setAlignment(Qt.AlignHCenter)
            adjust_the_text_edit_font_size([text_browser], self.min_font_size, self.max_font_size)
            # 首先来判断lesson_index+1是否存在
            # 下一节课是放学或者要用槽 现在又要用到槽位 所以不显示下一节课
            if lesson_index + 1 >= len(self.daily_config['lessons_list']) or \
                    self.daily_config['lessons_list'][lesson_index + 1][
                        'name'] not in self.lessons_with_slots:
                # 指向common(now)
                self.now_lesson_indicator = self.findChild(QTextBrowser, 'common_course_slots')
                self.next_lesson_indicator = 'hide'
                self.refresh_the_course_indicator_position()
                return
            # 下一节课不用槽位的情况 搜索下一节课是哪个
            tot = search_now_lessons(self.daily_config, self.daily_config["lessons_list"][lesson_index + 1])
            index: int = 0
            for index, i in enumerate(self.lessons_with_slots):
                if i == self.daily_config["lessons_list"][lesson_index + 1]['name']:
                    tot -= 1
                if tot == 0:
                    break
            # 指向common(now) self.lessons_slots[index+1](next)
            self.now_lesson_indicator = self.findChild(QTextBrowser, 'common_course_slots')
            self.next_lesson_indicator = self.findChild(QTextBrowser, self.lessons_slots[index + 1])
            self.refresh_the_course_indicator_position()
            return
        # 现在不用槽位的情况
        else:
            # 先搜索现在的在什么地方
            tot = search_now_lessons(self.daily_config, self.daily_config["lessons_list"][lesson_index])
            index: int = 0
            for index, i in enumerate(self.lessons_with_slots):
                if i == self.daily_config["lessons_list"][lesson_index]['name']:
                    tot -= 1
                if tot == 0:
                    break
            # 下一节课是放学
            if lesson_index + 1 >= len(self.daily_config['lessons_list']):
                text_browser = self.findChild(QTextBrowser, "common_course_slots")
                text_browser.setPlainText('放学')
                text_browser.setAlignment(Qt.AlignHCenter)
                adjust_the_text_edit_font_size([text_browser], self.min_font_size, self.max_font_size)
                # 指向self.lessons_slots[index+1](now) 指向common(next)
                self.now_lesson_indicator = self.findChild(QTextBrowser, self.lessons_slots[index + 1])
                self.next_lesson_indicator = self.findChild(QTextBrowser, 'common_course_slots')
                self.refresh_the_course_indicator_position()
                return
            # 下一节课是课间/special等
            elif self.daily_config['lessons_list'][lesson_index + 1]['name'] not in self.lessons_with_slots:
                text_browser = self.findChild(QTextBrowser, "common_course_slots")
                text_browser.setPlainText(self.daily_config["lessons_list"][lesson_index + 1]['name'])
                text_browser.setAlignment(Qt.AlignHCenter)
                adjust_the_text_edit_font_size([text_browser], self.min_font_size, self.max_font_size)
                # self.lessons_slots[index+1](now) 指向common(next)
                self.now_lesson_indicator = self.findChild(QTextBrowser, self.lessons_slots[index + 1])
                self.next_lesson_indicator = self.findChild(QTextBrowser, 'common_course_slots')
                self.refresh_the_course_indicator_position()
                return
            # 下节课也在lessons_with_slots里面 所以那就正好+1和+2了
            # 指向self.lessons_slots[index+1](now) self.lessons_slots[index+2](next)
            self.now_lesson_indicator = self.findChild(QTextBrowser, self.lessons_slots[index + 1])
            self.next_lesson_indicator = self.findChild(QTextBrowser, self.lessons_slots[index + 2])
            self.refresh_the_course_indicator_position()
            return

    # 刷新课程指示器的位置
    def refresh_the_course_indicator_position(self):
        now_label = self.findChild(QLabel, "now_lesson_indicator")  # 先读取label方便操作
        next_label = self.findChild(QLabel, "next_lesson_indicator")
        if self.settings_is_open:
            now_label.hide()
            next_label.hide()
            return
        spacer_item_x = self.curriculum.width() - self.course_display.width()
        common = self.findChild(QTextBrowser, "common_course_slots")
        x = common.width() + common.mapToGlobal(QtCore.QPoint(0, 0)).x() + spacer_item_x // 50  # 获得x坐标
        spacer_item_x -= spacer_item_x // 25
        # 先设置now_lesson_indicator
        if self.now_lesson_indicator == 'hide':
            now_label.hide()
        else:
            # 先设置要指示的长度和高度
            now_label.setFixedSize(spacer_item_x, self.now_lesson_indicator.height())
            now_label.show()
            # 移动到该去的地方
            # 获得坐标
            y = self.now_lesson_indicator.mapToGlobal(
                QtCore.QPoint(0, 0)).y()  # now_lesson的左上角的y坐标
            parent_pos = now_label.parent().mapFromGlobal(QtCore.QPoint(x, y))
            now_label.move(parent_pos)
            # 自适应字体大小
            adaptive_label_font_size(now_label, self.max_font_size, self.min_font_size)
        # 然后设置next_lesson_indicator
        if self.next_lesson_indicator == 'hide':
            next_label.hide()
        else:
            # 先设置要指示的长度和高度
            next_label.setFixedSize(spacer_item_x, self.next_lesson_indicator.height())
            next_label.show()
            # 移动到该去的地方
            # 获得坐标
            y = self.next_lesson_indicator.mapToGlobal(
                QtCore.QPoint(0, 0)).y()  # now_lesson的左上角的y坐标
            parent_pos = next_label.parent().mapFromGlobal(QtCore.QPoint(x, y))
            next_label.move(parent_pos)
            # 自适应字体大小
            adaptive_label_font_size(next_label, self.max_font_size, self.min_font_size)

    # 重写resizeEvent 实现自动重新自适应字体大小
    def resizeEvent(self, event):
        self.resize_timer.start()  # 重置窗口大小时启动计时器
        super().resizeEvent(event)

    # 自适应字体大小 窗口调整超时后
    def on_resize_timeout(self):
        self.resize_timer.stop()  # 停止计时器
        # 开启设置页面的情况下
        if self.settings_is_open:
            self.window_resized = True  # 等下刷新
            return
        self.refresh_the_course_indicator_position()
        adjust_the_text_edit_font_size([self.time_to_next], self.min_font_size, self.max_font_size)
        for i in self.lessons_slots:
            adjust_the_text_edit_font_size([self.findChild(QTextBrowser, i)], self.min_font_size,
                                           self.max_font_size)

    # 重写closeEvent 要备份
    def closeEvent(self, event):
        # 设置页面只能通过按钮退出
        if self.settings_is_open:
            event.ignore()
            return
        # 先存一下
        self.daily_config["backup"]["msg"] = self.message.toPlainText()
        self.daily_config["backup"]["homework"] = self.homework.toPlainText()
        write_file("../data/daily_config.json", json.dumps(self.daily_config, ensure_ascii=False, indent=4))
        # 退出
        super().closeEvent(event)
        event.accept()
        os._exit(0)

    # 切换到设置界面
    def show_settings_page(self):
        self.settings_is_open = True
        self.run_adaptive_text_edit_manually.emit()  # 先备份一手
        self.refresh_the_course_indicator_position()  # 刷新一下课程指示器的位置
        self.settings_page.singal_go_to_the_settings_page.emit()
        self.stackedWidget.setCurrentIndex(1)  # 切换到设置的堆叠布局
        self.settings_page.signal_switch_to_the_interface.emit()

    # 从设置界面退出
    def exit_settings_page(self):
        # 删除对象
        self.settings_is_open = False
        self.stackedWidget.setCurrentIndex(0)  # 切换到设置的堆叠布局
        if self.window_resized:  # 如果设置页面开启的时候字体发生了改变的话就重新设置一下
            self.on_resize_timeout()
        self.window_resized = False
        # 刷新课表指示器
        self.lessons_status = None  # 防止拒绝刷新
        self.next_lesson = None
        self.time_to_next_refresh()

        # TODO 刷新其他的数据


if __name__ == '__main__':
    version = '1.0.1'
    now = datetime.now()
    week_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][now.weekday()]
    compare_time = compareTime()
    # 初始化文件防止报错
    # 初始化文件夹
    os.makedirs('../data/backup/daily_config', exist_ok=True)
    os.makedirs('../data/backup/program_config', exist_ok=True)
    os.makedirs('../data/backup/time', exist_ok=True)
    os.makedirs('../data/backup/lessons', exist_ok=True)
    os.makedirs('../data/Curriculum', exist_ok=True)
    # 初始化文件并且兼容升级 具体更改在函数内
    initialize_the_file(version)
    # 如果是周六日并且文件没有在今天被创建过的话就问一下
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 高DPI自适应
    lessons_dict = json.loads(read_file('../data/Curriculum/lessons.json'))
    # 询问课表 如果是没东西的话那么就询问要替换哪个课表
    if (lessons_dict[week_name][0] == 'None') and compare_time is False:
        app = QApplication(sys.argv)
        ReselectTheClassSchduleWindow = ReselectTheClassScheduleWindow(lessons_dict)
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
                                             args=(int(config["refresh_time"]), main_window,))
    scheduled_task_thread.start()
    # 进入主窗口

    # 使用qdarkstyle
    import qdarkstyle

    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # 设置qss 使用qdarkstyle qss

    sys.exit(app.exec_())
# TODO 可以调整颜色的作业/消息
# TODO 值日模块
