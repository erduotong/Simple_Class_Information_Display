import sys
import threading
from datetime import *
import qdarkstyle
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from daily_initialization import *
import time


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
    run_adaptive_text_edit_manually = pyqtSignal()  # 自适应homework和message的字体大小和比例 手动触发 todo 绑定一个刷新按钮
    update_the_course_indicator_singal = pyqtSignal()  # 刷新课程指示器用的信号

    def __init__(self, program_config):
        super().__init__()
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
        self.ui = None
        self.lessons_status = None
        self.daily_config = self.daily_config = json.loads(read_file("../data/daily_config.json"))
        self.lessons_with_slots = []
        self.next_lesson = None  # 存储的是lessons_list的下标
        self.time_to_next_len = None
        self.lessons_slots = []
        # config需要用的内容初始化
        self.laa = int(program_config["layout_adjustment_accuracy"])
        self.min_font_size = int(program_config["minimum_font_size"])
        self.max_font_size = int(program_config["maximum_font_size"])
        self.run_window()  # 运行!
        self.time_to_next_refresh()  # 强制刷新一下到下一节课的时间
        QtCore.QTimer.singleShot(0, self.after_init)

    # 需要渲染窗口完毕后执行的函数
    def after_init(self):
        self.initialize_the_class_schedule()
        set_font_list = []
        QtCore.QTimer.singleShot(0, self.after_after_init)

    # 真的是醉了......
    def after_after_init(self):
        for i in self.lessons_slots:
            adjust_the_text_edit_font_size([self.ui.findChild(QTextBrowser, i)], self.min_font_size, self.max_font_size)

    def run_window(self):
        self.ui = uic.loadUi("./main_window.ui")
        self.ui.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口
        rect = QDesktopWidget().availableGeometry()  # 初始化大小
        self.ui.resize(rect.width(), rect.height())
        adjust_font_size(self.ui.nowtime, config["time_font_size"])  # 设置时间显示的字体大小
        # 绑定要用到ui的信号和槽
        self.ui.homework.setPlainText(self.daily_config['backup']['homework'])  # 加载之前的文本
        self.ui.message.setPlainText(self.daily_config['backup']['msg'])
        self.ui.message.textChanged.connect(self.on_text_changed)  # 两个文本框的超时信号
        self.ui.homework.textChanged.connect(self.on_text_changed)
        self.run_adaptive_text_edit_manually.emit()
        self.ui.refresh_font.clicked.connect(self.run_adaptive_text_edit_manually)
        # 设置快捷键
        self.ui.refresh_font.setShortcut('F5')
        self.refresh_time()  # 先进行初始化一次时间防止卡着
        # print(self.ui.__dict__)  # 调试用
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
        self.time_to_next_refresh()
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
        # 备份一下其中的内容
        self.daily_config["backup"]["msg"] = self.ui.message.toPlainText()
        self.daily_config["backup"]["homework"] = self.ui.homework.toPlainText()
        write_file("../data/daily_config.json", json.dumps(self.daily_config, ensure_ascii=False, indent=4))
        # 重新连接textChanged信号与槽函数
        self.ui.message.textChanged.connect(self.on_text_changed)
        self.ui.homework.textChanged.connect(self.on_text_changed)

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
        for i in self.ui.lessons_list.findChildren(QtWidgets.QTextBrowser):
            i.deleteLater()
        self.ui.lessons_list.setMaximumHeight(self.ui.lessons_list.height())  # 防止超出距离
        # 添加第一个用于显示课间等的widget(一定有的) 名称为common_course_slots
        self.lessons_slots = []
        text_browser = QtWidgets.QTextBrowser(self.ui.lessons_list)
        text_browser.setObjectName("common_course_slots")
        self.lessons_slots.append("common_course_slots")
        text_browser.setText("延时服务")  # test
        text_browser.setAlignment(Qt.AlignHCenter)
        self.ui.lessons_list.layout().addWidget(text_browser)
        # 添加剩余len lessons_with_slots个
        for i in range(1, len(self.lessons_with_slots) + 1):
            text_browser = QtWidgets.QTextBrowser(self.ui.lessons_list)
            text_browser.setObjectName(f"lesson{i}")
            text_browser.setText(self.lessons_with_slots[i - 1])
            text_browser.setAlignment(Qt.AlignHCenter)
            self.lessons_slots.append(f"lesson{i}")
            self.ui.lessons_list.layout().addWidget(text_browser)

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
                self.update_the_course_indicator_singal.emit()
            # 更新一下课程表的指示器
            self.ui.time_to_next.setPlainText(
                f"距离第一节课还有{format_timedelta(time_to_datetime(self.daily_config['lessons_list'][0]['start'], now_time) - now_time)}"
            )
        # 上完最后一节课的情况 为1
        elif now_time > time_to_datetime(self.daily_config["lessons_list"][-1]["end"], now_time):
            if self.lessons_status != 1:
                self.lessons_status = 1
                self.update_the_course_indicator_singal.emit()
            self.ui.time_to_next.setPlainText(
                f"已放学{format_timedelta(now_time - time_to_datetime(self.daily_config['lessons_list'][-1]['end'], now_time))}"
            )
        # 正常 正在上课的情况
        else:
            for index, lesson in enumerate(self.daily_config["lessons_list"]):
                if time_to_datetime(lesson["start"], now_time) <= now_time < time_to_datetime(lesson["end"], now):
                    if self.next_lesson != index + 1:
                        self.next_lesson = index + 1
                        self.update_the_course_indicator_singal.emit()
                    break
            if self.next_lesson == len(self.daily_config["lessons_list"]):  # 超过列表最大长度了
                self.ui.time_to_next.setPlainText(
                    f"距离放学还有{format_timedelta(time_to_datetime(self.daily_config['lessons_list'][self.next_lesson - 1]['end'], now_time) - now_time)}")
            else:
                self.ui.time_to_next.setPlainText(
                    f"距离{self.daily_config['lessons_list'][self.next_lesson]['name']}还有{format_timedelta(time_to_datetime(self.daily_config['lessons_list'][self.next_lesson]['start'], now_time) - now_time)}"
                )

        # 设置对齐方式
        self.ui.time_to_next.setAlignment(Qt.AlignCenter)
        # 自适应大小
        if len(self.ui.time_to_next.toPlainText()) != self.time_to_next_len or self.ui.time_to_next.verticalScrollBar().isVisible():
            self.time_to_next_len = len(self.ui.time_to_next.toPlainText())
            # 自适应字体大小
            adjust_the_text_edit_font_size([self.ui.time_to_next], self.min_font_size, self.max_font_size)

    # 刷新这个课程以及下一个课程的指示器
    def refresh_the_course_indicator(self) -> None:
        print("refresh_the_course_indicator")


if __name__ == '__main__':
    now = datetime.now()
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
