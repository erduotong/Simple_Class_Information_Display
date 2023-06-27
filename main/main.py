# -*- coding: utf-8 -*-
import sys
import threading
from datetime import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from daily_initialization import *
import time
from rcs import Ui_Dialog
from main_window import Ui_MainWindow
import win32gui


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
        self.result = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][datetime.now().weekday()]
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


class MainWindow(QMainWindow, Ui_MainWindow):
    refresh_time_singal = pyqtSignal()  # 更新时间
    run_adaptive_text_edit_manually = pyqtSignal()  # 自适应homework和message的字体大小和比例 手动触发
    update_the_course_indicator_singal = pyqtSignal(int)  # 刷新课程指示器用的信号

    def __init__(self, program_config):
        super().__init__()
        self.setupUi(self)
        self.refresh_edit_size = QtCore.QTimer()  # 设置一个计时器
        self.refresh_edit_size.setInterval(program_config["text_edit_refresh_time"] * 1000)  # 设置停止编辑刷新的时间
        # 绑定信号&槽
        self.refresh_edit_size.timeout.connect(self.manually_refresh_the_text_edit_font)  # 超时后连接到更新字体
        self.refresh_time_singal.connect(self.refresh_time)
        self.run_adaptive_text_edit_manually.connect(self.manually_refresh_the_text_edit_font)
        self.update_the_course_indicator_singal.connect(self.refresh_the_course_indicator)
        # 变量初始化
        self.screen_height = None
        self.screen_width = None
        self.lessons_status = None
        self.daily_config = self.daily_config = json.loads(read_file("../data/daily_config.json"))
        self.lessons_with_slots = []
        self.next_lesson = None  # 存储的是lessons_list的下标
        self.time_to_next_len = None
        self.lessons_slots = []
        self.now_lesson_indicator = None
        self.next_lesson_indicator = None
        # config需要用的内容初始化
        self.laa = int(program_config["layout_adjustment_accuracy"])
        self.min_font_size = int(program_config["minimum_font_size"])
        self.max_font_size = int(program_config["maximum_font_size"])
        self.program_config = program_config
        # 设置是否开启桌面壁纸模式
        if self.program_config['desktop_wallpaper_mode'] == 'true':
            self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口
            pretreatmentHandle()  # 杀了其他桌面的程序
            # 下面的代码我也不知道具体是干嘛的 反正就是添加到桌面层 反正能跑
            # TODO 可以交互 暂时不知道如何实现
            # h = win32gui.FindWindow("Progman", "Program Manager")
            # win_hwnd = int(self.winId())
            # window_h = int(self.winId())
            # win32gui.SetParent(win_hwnd, h)
            # win32gui.SetParent(window_h, h)
        # 普通窗口模式
        else:
            self.setWindowTitle("Simple_Class_Information_Display")
        rect = QDesktopWidget().availableGeometry()  # 初始化大小
        self.resize(rect.width(), rect.height())
        adjust_font_size(self.nowtime, config["time_font_size"])  # 设置时间显示的字体大小
        # 绑定要用到信号和槽
        self.homework.setPlainText(self.daily_config['backup']['homework'])  # 加载之前的文本
        self.message.setPlainText(self.daily_config['backup']['msg'])
        self.message.textChanged.connect(self.on_text_changed)  # 两个文本框的超时信号
        self.homework.textChanged.connect(self.on_text_changed)
        self.refresh_font.clicked.connect(self.run_adaptive_text_edit_manually)
        # QTimer区
        self.resize_timer = QTimer(self)  # 刷新窗口的QTimer
        self.resize_timer.setInterval(int(program_config['the_window_changes_the_refresh_time'] * 1000))
        self.resize_timer.timeout.connect(self.on_resize_timeout)
        # 设置快捷键
        self.refresh_font.setShortcut('F5')
        # 加入两个显示的QLabel
        self.layout().addWidget(
            initialize_label_indicator("next_lesson_indicator", program_config['next_indicator_text']))
        self.layout().addWidget(
            initialize_label_indicator("now_lesson_indicator", program_config['now_indicator_text']))
        # print(self.__dict__)  # 调试用
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
        text_browser.setText("test")
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
        #
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
        self.refresh_the_course_indicator_position()
        adjust_the_text_edit_font_size([self.time_to_next], self.min_font_size, self.max_font_size)
        for i in self.lessons_slots:
            adjust_the_text_edit_font_size([self.findChild(QTextBrowser, i)], self.min_font_size,
                                           self.max_font_size)

    # 重写closeEvent 要备份
    def closeEvent(self, event):
        # 先存一下
        self.daily_config["backup"]["msg"] = self.message.toPlainText()
        self.daily_config["backup"]["homework"] = self.homework.toPlainText()
        write_file("../data/daily_config.json", json.dumps(self.daily_config, ensure_ascii=False, indent=4))
        # 退出
        super().closeEvent(event)
        event.accept()
        os._exit(0)


if __name__ == '__main__':
    now = datetime.now()
    week_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][now.weekday()]
    compare_time = compareTime()
    # 初始化文件防止报错
    # 初始化文件夹
    os.makedirs('../data/backup/daily_config', exist_ok=True)
    os.makedirs('../data/Curriculum', exist_ok=True)
    # 初始化文件 具体更改在函数内
    initialize_the_file()
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
                                             args=(float(config["refresh_time"]), main_window,))
    scheduled_task_thread.start()
    # 进入主窗口

    # 使用qdarkstyle
    import qdarkstyle

    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # 设置qss 使用qdarkstyle qss

    sys.exit(app.exec_())
