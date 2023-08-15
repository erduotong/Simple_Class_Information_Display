# -*- coding: utf-8 -*-
import sys
import copy
import random
import datetime
import threading

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import *

from daily_initialization import *
from main_window import Ui_MainWindow
from rcs import Ui_Dialog
from settings_page import Ui_settings


class ReselectTheClassScheduleWindow(QDialog, Ui_Dialog):
    returnPressed = pyqtSignal(str)

    def __init__(self, week):
        super().__init__()
        self.week = week
        self.result = None
        self.setupUi(self)
        self.show()
        self.init_ui()
        self.signal1 = None

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
        self.signal1 = 'clicked'
        self.close()
        self.returnPressed.emit(self.result)

    def on_push_button_2_clicked(self):
        self.result = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][
            datetime.now().weekday()]
        self.signal1 = 'clicked'
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
        if self.signal1 == 'clicked':
            event.accept()
        else:
            event.ignore()


class SettingsPage(QWidget, Ui_settings):
    signal_go_to_the_settings_page = pyqtSignal()
    signal_exit_SettingsPage = pyqtSignal()
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
        # ==========daily config
        self.today_lessons_edit_opened: bool = False
        self.add_dailyconfig_lessons.clicked.connect(self.add_daily_config_lessons)
        self.sort_by_time.clicked.connect(self.reorder_by_time)
        # 绑定信号和槽
        self.signal_switch_to_the_interface.connect(self.open_about)
        self.signal_go_to_the_settings_page.connect(self.initialize_after_entering)
        self.not_save_exit.clicked.connect(self.do_not_save_and_exit)
        self.save_exit.clicked.connect(self.save_and_exit)
        self.to_program_config.clicked.connect(self.open_program_config)
        self.to_daily_config.clicked.connect(self.open_daily_config)
        self.to_lessons.clicked.connect(self.open_lessons)
        self.to_about.clicked.connect(self.open_about)
        self.to_time.clicked.connect(self.open_time)
        self.to_resetting.clicked.connect(self.open_resetting)
        self.set_lessons_tabWidget.currentChanged.connect(self.on_lessons_edit_current_changed)
        self.set_time_tabWidget.currentChanged.connect(self.time_edit_adaptive_fonts)
        self.time_edit_reorder_button.clicked.connect(self.time_edit_reorder)
        self.time_edit_reorder_special_button.clicked.connect(self.time_edit_reorder_special)
        self.start_reset.clicked.connect(self.start_the_reset)
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
        self.today_lessons_edit_opened: bool = False

    # //////////////////
    # program_config编辑

    def open_program_config(self):
        self.tabWidget.setCurrentIndex(0)
        if not self.program_config_opened:
            self.program_config_opened = True
            self.init_program_config_widget()

    def init_program_config_widget(self):
        # 首先清空 然后计算出最大和最小高度 框死
        # 清空其中的所有widget保险
        for i in self.program_config_show_area.findChildren(QWidget):
            i.deleteLater()
            pass
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
            "text_edit_refresh_time": "文本编辑后自动自适应时间间隔",
            "the_window_changes_the_refresh_time": "窗口改变后自动自适应时间间隔",
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
            QTimer.singleShot(0, lambda: self.daily_config_tab_changed(0))

            self.daily_config_opened = True

    def init_daily_config_table(self):
        self.daily_config_tableWidget.setRowCount(0)  # 清空其中的内容
        table_row_height = self.daily_config_tableWidget.height() // 20  # 设置单格的高度
        self.daily_config_tableWidget.horizontalHeader().setFixedHeight(table_row_height)
        # 生成表格
        for i in self.daily_config_dict.get("lessons_list"):
            row_position = self.daily_config_tableWidget.rowCount()  # 获得行数
            self.daily_config_tableWidget.insertRow(row_position)  # 添加一行
            self.daily_config_tableWidget.setRowHeight(row_position, table_row_height)
            font = QFont("黑体")
            # 添加课程名称更改
            line_edit = QLineEdit(str(i.get("name")))
            line_edit.setFont(font)
            line_edit.textChanged.connect(
                lambda content, row=row_position: self.update_daily_config_lessons(content, 1, row))
            self.daily_config_tableWidget.setCellWidget(row_position, 0, line_edit)
            # start时间更改
            time_edit_start = StrictQTimeEdit()
            time_edit_start.setFont(font)
            time_edit_start.setDisplayFormat("hh:mm")
            time_edit_start.setTime(QTime.fromString(i.get("start"), "hh:mm"))
            time_edit_start.timeChanged.connect(
                lambda content, row=row_position: self.update_daily_config_lessons(content.toString("hh:mm"), 2,
                                                                                   row))
            self.daily_config_tableWidget.setCellWidget(row_position, 1, time_edit_start)
            # end时间更改
            time_edit_end = StrictQTimeEdit()
            time_edit_end.setFont(font)
            time_edit_end.setDisplayFormat("hh:mm")
            time_edit_end.setTime(QTime.fromString(i.get("end", "hh:mm")))
            time_edit_end.timeChanged.connect(
                lambda content, row=row_position: self.update_daily_config_lessons(content.toString("hh:mm"), 3,
                                                                                   row))
            self.daily_config_tableWidget.setCellWidget(row_position, 2, time_edit_end)
            # 删除按钮更改
            button = QPushButton("删除")
            button.setFont(font)
            button.clicked.connect(lambda _, row=row_position: self.update_daily_config_lessons(None, 4, row))
            button.setStyleSheet("""
                                QPushButton:hover, QPushButton:focus {
                                    border: 3px solid #346792;
                                }
                            """)
            self.daily_config_tableWidget.setCellWidget(row_position, 3, button)

    def daily_config_tab_changed(self, index):
        # 根据index判断要进行什么操作
        # 如果index还没有进行过初始化，那么就进行一下初始化
        # 否则就该干嘛干嘛(比如重排序?
        self.today_lessons_edit_opened: bool = False
        # 课程编辑
        if index == 0:
            if not self.today_lessons_edit_opened:  # 本次进入没有启用过，需要进行一次初始化~
                self.today_lessons_edit_opened = True
                # 初始化列的大小
                self.daily_config_dict["lessons_list"] = sorted(self.daily_config_dict["lessons_list"],
                                                                key=lambda x: x["start"])  # 对其中的数据按开始时间进行一次排序
                self.daily_config_tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
                self.daily_config_tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
                self.daily_config_tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
                self.daily_config_tableWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
                self.init_daily_config_table()  # 生成表格
                for i in self.widget_6.findChildren(QPushButton):
                    adaptive_label_font_size(i, 25, 1)

            # 字体自适应
            def adjust_table_widget_font_size():
                for i in self.daily_config_tableWidget.findChildren((QLineEdit, QPushButton, StrictQTimeEdit)):
                    adaptive_label_font_size(i, 50, 1)

            QTimer.singleShot(0, adjust_table_widget_font_size)

    def update_daily_config_lessons(self, content_1, mode, row_) -> None:
        if mode == 1:  # 刷新课程名称
            if content_1 and not content_1.isspace():  # 只有在内容不为空的情况下才进行变更
                content_11 = content_1.rstrip()  # 删除末尾空格
                if content_11 != content_1:
                    self.daily_config_tableWidget.cellWidget(row_, 0).setText(content_11)
                self.daily_config_dict["lessons_list"][row_]["name"] = content_11  # 设置该项为content_11
            return
        elif mode == 2:  # 刷新开始时间
            self.daily_config_dict["lessons_list"][row_]["start"] = content_1
            return
        elif mode == 3:  # 刷新结束时间
            self.daily_config_dict["lessons_list"][row_]["end"] = content_1
            return
        else:  # 删除该项
            del self.daily_config_dict["lessons_list"][row_]  # 删除该项
            self.daily_config_dict["lessons_list"] = sorted(self.daily_config_dict["lessons_list"],
                                                            key=lambda x: x["start"])  # 对其中的数据按开始时间进行一次排序
            self.init_daily_config_table()  # 生成表格

            # 字体自适应
            def adjust_table_widget_font_size():
                for i in self.daily_config_tableWidget.findChildren((QLineEdit, QPushButton, StrictQTimeEdit)):
                    adaptive_label_font_size(i, 50, 1)

            QTimer.singleShot(0, adjust_table_widget_font_size)
            return

    # 添加新的一项在末尾
    def add_daily_config_lessons(self):
        self.daily_config_dict["lessons_list"].append({
            "name": "新建项",
            "start": "11:45",
            "end": "19:19"
        })
        table_row_height = self.daily_config_tableWidget.height() // 18  # 设置单格的高度
        i = self.daily_config_dict["lessons_list"][-1]
        row_position = self.daily_config_tableWidget.rowCount()  # 获得行数
        self.daily_config_tableWidget.insertRow(row_position)  # 添加一行
        self.daily_config_tableWidget.setRowHeight(row_position, table_row_height)
        font = QFont("黑体")
        # 添加课程名称更改
        line_edit = QLineEdit(str(i.get("name")))
        line_edit.setFont(font)
        line_edit.textChanged.connect(
            lambda content, row=row_position: self.update_daily_config_lessons(content, 1, row))
        self.daily_config_tableWidget.setCellWidget(row_position, 0, line_edit)
        # start时间更改
        time_edit_start = StrictQTimeEdit()
        time_edit_start.setFont(font)
        time_edit_start.setDisplayFormat("hh:mm")
        time_edit_start.setTime(QTime.fromString(i.get("start"), "hh:mm"))
        time_edit_start.timeChanged.connect(
            lambda content, row=row_position: self.update_daily_config_lessons(content.toString("hh:mm"), 2,
                                                                               row))
        self.daily_config_tableWidget.setCellWidget(row_position, 1, time_edit_start)
        # end时间更改
        time_edit_end = StrictQTimeEdit()
        time_edit_end.setFont(font)
        time_edit_end.setDisplayFormat("hh:mm")
        time_edit_end.setTime(QTime.fromString(i.get("end", "hh:mm")))
        time_edit_end.timeChanged.connect(
            lambda content, row=row_position: self.update_daily_config_lessons(content.toString("hh:mm"), 3,
                                                                               row))
        self.daily_config_tableWidget.setCellWidget(row_position, 2, time_edit_end)
        # 删除按钮更改
        button = QPushButton("删除")
        button.setFont(font)
        button.clicked.connect(lambda _, row=row_position: self.update_daily_config_lessons(None, 4, row))
        button.setStyleSheet("""
                                        QPushButton:hover, QPushButton:focus {
                                            border: 3px solid #346792;
                                        }
                                    """)
        self.daily_config_tableWidget.setCellWidget(row_position, 3, button)

        def adjust_table_widget_font_size():
            for i in self.daily_config_tableWidget.findChildren((QLineEdit, QPushButton, StrictQTimeEdit)):
                adaptive_label_font_size(i, 50, 1)

        QTimer.singleShot(0, adjust_table_widget_font_size)

    # 按时间重排序
    def reorder_by_time(self):
        self.daily_config_dict["lessons_list"] = sorted(self.daily_config_dict["lessons_list"],
                                                        key=lambda x: x["start"])  # 对其中的数据按开始时间进行一次排序
        self.init_daily_config_table()  # 生成表格

        # 字体自适应
        def adjust_table_widget_font_size():
            for i in self.daily_config_tableWidget.findChildren((QLineEdit, QPushButton, StrictQTimeEdit)):
                adaptive_label_font_size(i, 50, 1)

        QTimer.singleShot(0, adjust_table_widget_font_size)

    # //////////////////
    # 课程编辑

    def open_lessons(self):
        self.tabWidget.setCurrentIndex(2)
        if not self.lessons_opened:
            # 初始化lessons页
            # 清空tabWidget中的控件
            for i in range(self.set_lessons_tabWidget.count()):  # 遍历self.set_lessons_tabWidget中的所有tab
                tab = self.set_lessons_tabWidget.widget(i)  # 获取当前tab
                layout = tab.layout()  # 获取当前tab的布局
                if layout is not None:  # 如果布局不为空
                    while layout.count():  # 遍历布局中的所有控件
                        item = layout.takeAt(0)  # 获取当前控件
                        widget = item.widget()
                        if widget is not None:
                            widget.deleteLater()  # 删除控件
                    QWidget().setLayout(layout)  # 清空布局

            for index, (key, value) in enumerate(self.lessons_dict.items()):
                layout_father = QHBoxLayout()
                list_widget = ListWidgetWithRowChanged()
                for i in value:  # 添加每个元素到list-widget里面
                    item = QtWidgets.QListWidgetItem(i)
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                    list_widget.addItem(item)
                # 设置list-widget
                list_widget.setSpacing(2)  # 设置间隔

                # 创建编辑按钮
                button_layout = QGridLayout()
                button_add = QPushButton("+")  # 设置增加按钮
                button_del = QPushButton("-")  # 删除按钮
                button_move_up = QPushButton("↑")  # 上移按钮
                button_move_down = QPushButton("↓")  # 下移按钮
                # 设置字体颜色
                button_add.setStyleSheet("color:lightgreen;font-weight:bold;")
                button_del.setStyleSheet("color:red;font-weight:bold;")
                button_move_up.setStyleSheet("font-weight:bold")
                button_move_down.setStyleSheet("font-weight:bold")
                # 丢到布局里面
                button_layout.addWidget(button_add, 0, 0)
                button_layout.addWidget(button_del, 0, 1)
                button_layout.addWidget(button_move_down, 1, 1)
                button_layout.addWidget(button_move_up, 1, 0)
                button_add.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置缩放策略
                button_del.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button_move_up.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button_move_down.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button_layout.setSpacing(50)
                button_widget = QWidget()  # 丢到widget里面
                button_widget.setLayout(button_layout)
                layout_father.addWidget(list_widget, 10)
                layout_father.addWidget(button_widget, 6)
                self.set_lessons_tabWidget.widget(index).setLayout(layout_father)  # 设置第i页的布局
                button_add.clicked.connect(lambda f, list_widget1=list_widget: self.lessons_edit_add(list_widget1))
                button_del.clicked.connect(lambda f, list_widget1=list_widget: self.lessons_edit_del(list_widget1))
                button_move_up.clicked.connect(
                    lambda f, list_widget1=list_widget: self.lessons_edit_move_up(list_widget1))
                button_move_down.clicked.connect(
                    lambda f, list_widget1=list_widget: self.lessons_edit_move_down(list_widget1))
                list_widget.itemChanged.connect(
                    lambda item1, lessons_key=key, list_widget1=list_widget: self.lessons_edit_content_changed(item1,
                                                                                                               lessons_key,
                                                                                                               list_widget1))
                list_widget.itemsChanged.connect(lambda lw=list_widget, k=key: self.lessons_edit_row_changed(lw, k))
            self.lessons_opened = True
        QTimer.singleShot(0, lambda: self.on_lessons_edit_current_changed(self.set_lessons_tabWidget.currentIndex()))

    # 当切换到新的tab的时候自适应其中的字体
    def on_lessons_edit_current_changed(self, index):
        tab = self.set_lessons_tabWidget.widget(index)  # 得到tab!
        fixed_size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        expanding_size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        for i in tab.findChildren(QPushButton):
            i.setSizePolicy(fixed_size_policy)  # 先锁定
            adaptive_label_font_size(i, 100, 1)
            i.setSizePolicy(expanding_size_policy)  # 后自由防止出现一些奇奇怪怪的bug
        list_widget = tab.findChild(ListWidgetWithRowChanged)  # 找一下listWidget
        height = tab.height() // 20
        list_widget.setStyleSheet(f'''
            QListWidget::item {{height: {height}px;}}
            QListWidget::item:selected {{
                border: 3px solid #346792;
            }}
        ''')

        for i in range(list_widget.count()):  # 遍历其中的item
            item = list_widget.item(i)
            adaptive_item_font_size(item, 50, 1, list_widget)  # 自适应大小

    # 添加一节课在当前的list_widget中
    def lessons_edit_add(self, list_widget):
        item = QtWidgets.QListWidgetItem("None")  # 添加一个
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        list_widget.addItem(item)
        adaptive_item_font_size(item, 50, 1, list_widget)  # 自适应大小

    # 删除
    def lessons_edit_del(self, list_widget):
        will_del = list_widget.currentItem()
        if will_del is None:
            QMessageBox.warning(self, "警告",
                                "请选中一项后再删除",
                                QMessageBox.Yes)  # 添加提示窗口提醒用户
            return
        list_widget.takeItem(list_widget.row(will_del))

    # 和上一个元素交换以达成上移的目的
    def lessons_edit_move_up(self, list_widget):
        item = list_widget.currentItem()  # 获得当前的item
        if item is None:
            QMessageBox.warning(self, "警告", "请选中一项后再进行移动操作", QMessageBox.Yes)  # 添加提示窗口提醒用户
            return
        item_row = list_widget.row(item)
        if item_row > 0:
            item1 = list_widget.takeItem(item_row)  # 获取两个项目
            item2 = list_widget.takeItem(item_row - 1)
            list_widget.insertItem(item_row - 1, item2)  # 交换两个项目
            list_widget.insertItem(item_row - 1, item1)
            list_widget.setCurrentRow(item_row - 1)  # 将选定的行更改为item_row-1

    # 和下一个元素交换以达成下移的目的
    def lessons_edit_move_down(self, list_widget):
        item = list_widget.currentItem()  # 获得当前的item
        if item is None:
            QMessageBox.warning(self, "警告", "请选中一项后再进行移动操作", QMessageBox.Yes)  # 添加提示窗口提醒用户
            return
        item_row = list_widget.row(item)
        if item_row < list_widget.count() - 1:
            item1 = list_widget.takeItem(item_row)  # 获取两个项目
            item2 = list_widget.takeItem(item_row + 1)
            list_widget.insertItem(item_row + 1, item2)  # 交换两个项目
            list_widget.insertItem(item_row + 1, item1)
            list_widget.setCurrentRow(item_row + 1)  # 将选定的行更改为item_row+1

    # 行数发生变化
    def lessons_edit_row_changed(self, list_widget, key):
        # 遍历其中的item并且重新添加到key里面
        self.lessons_dict[key].clear()  # 先清空
        self.time_opened = False
        for i in range(list_widget.count()):
            self.lessons_dict[key].append(list_widget.item(i).text())  # 获得并添加到末尾!

    # 内容发生变化
    def lessons_edit_content_changed(self, item, lessons_key, list_widget):
        self.time_opened = False
        text = item.text().rstrip()  # 获得文本并丢掉末尾的空格
        item.setText(text)  # 覆盖，正则判断不是好文明!
        if text:  # 当里面非空的时候才处理
            self.lessons_dict[lessons_key][list_widget.row(item)] = text  # 将lessons_dict里面的key中的第item的row个元素设置成当前的更改!

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
        # TODO 完成两个重排序
        if not self.time_opened:
            # 思路:判断time.json里面和实际lessons里面的max值是否相等，以及special里面是否都已经添加进去了。如果已经有那么就继承时间
            # 如果没有的话，那么就新建一项
            # 用tab widget来区分special和常规的
            # 重排序操作:依次取出其中的时间然后添加到一个列表内 再装填回去 接着重新生成一次
            self.init_time_edit()  # 加载内容
            self.time_edit_table_to_dict()  # 根据表中的内容重新更改time_dict
            self.time_opened = True
        QTimer.singleShot(0, lambda: self.time_edit_adaptive_fonts(self.set_time_tabWidget.currentIndex()))

    # 按时间重新排序
    def time_edit_reorder(self):
        need_sort = []
        for key in self.time_dict.keys():
            if re.match(r'^l\d+$', key):
                need_sort.append(self.time_dict[key])
        need_sort.sort(key=lambda x: (x['start'], x['end']))
        for i in range(1, len(need_sort) + 1):
            self.time_dict[f'l{i}'] = need_sort[i - 1]
        self.init_time_edit()  # 重载内容
        self.time_edit_table_to_dict()
        QTimer.singleShot(0, lambda: self.time_edit_adaptive_fonts(self.set_time_tabWidget.currentIndex()))

    def time_edit_reorder_special(self):
        # 重复上述逻辑但是可能需要映射？
        need_sort = []
        for key in list(self.time_dict.keys()):
            if not re.match(r'^l\d+$', key):
                need_sort.append({key: self.time_dict[key]})
                del self.time_dict[key]
        need_sort.sort(key=lambda x: (list(x.values())[0]['start'], list(x.values())[0]['end']))
        for i in need_sort:
            self.time_dict.update(i)
        self.init_time_edit()  # 重载内容
        self.time_edit_table_to_dict()
        QTimer.singleShot(0, lambda: self.time_edit_adaptive_fonts(self.set_time_tabWidget.currentIndex()))

    # 初始化/生成
    def init_time_edit(self):
        row_height = self.tabWidget.height() // 13
        max_lessons_len = 0
        self.time_edit_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.time_edit_tableWidget_special.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.time_edit_tableWidget.setRowCount(0)  # 清空
        self.time_edit_tableWidget_special.setRowCount(0)
        # ----------------
        # 常规的tab_widget
        for i in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            max_lessons_len = max(len(self.lessons_dict.get(i)), max_lessons_len)  # 获得最多的lessons数量
        for i in range(1, max_lessons_len + 1):
            row_position = self.time_edit_tableWidget.rowCount()
            self.time_edit_tableWidget.insertRow(row_position)
            self.time_edit_tableWidget.setRowHeight(row_position, row_height)
            label = QLabel()
            time_edit_start = StrictQTimeEdit()
            time_edit_start.setDisplayFormat("hh:mm")
            time_edit_end = StrictQTimeEdit()
            time_edit_end.setDisplayFormat("hh:mm")
            label.setText(f'l{i}')
            lesson_n = self.time_dict.get(f'l{i}')
            if lesson_n is not None:  # 判断是否有这个时间 没有的话就新建
                time_edit_start.setTime(QTime.fromString(lesson_n['start'], 'hh:mm'))
                time_edit_end.setTime(QTime.fromString(lesson_n['end'], 'hh:mm'))
            else:
                time_edit_start.setTime(QTime.fromString("00:00", 'hh:mm'))
                time_edit_end.setTime(QTime.fromString("00:00", 'hh:mm'))
            time_edit_start.timeChanged.connect(
                lambda time_, ln=f'l{i}': self.time_edit_changed(time_, ln, False))  # false为start,true为end
            time_edit_end.timeChanged.connect(
                lambda time_, ln=f'l{i}': self.time_edit_changed(time_, ln, True))
            self.time_edit_tableWidget.setCellWidget(row_position, 0, label)
            self.time_edit_tableWidget.setCellWidget(row_position, 1, time_edit_start)
            self.time_edit_tableWidget.setCellWidget(row_position, 2, time_edit_end)
        # 特殊课程的生成
        to_add = []  # 要按照字典中的顺序做出来所以特别丑。。。
        for i in self.lessons_dict.get("special"):
            if self.time_dict.get(i) is None:
                self.time_dict.update({
                    i: {
                        "start": "00:00",
                        "end": "00:00"
                    }
                })
            to_add.append({i: self.time_dict.get(i)})

        def cmp(d):
            for key in d:
                return list(self.time_dict.keys()).index(key)

        to_add.sort(key=cmp)

        for i in to_add:
            key: str = ''
            value: dict = {}
            for i1, j1 in i.items():
                key = i1
                value = j1
            row_position = self.time_edit_tableWidget_special.rowCount()
            self.time_edit_tableWidget_special.insertRow(row_position)
            self.time_edit_tableWidget_special.setRowHeight(row_position, row_height)
            label = QLabel()
            time_edit_start = StrictQTimeEdit()
            time_edit_end = StrictQTimeEdit()
            time_edit_start.setDisplayFormat("hh:mm")
            time_edit_end.setDisplayFormat("hh:mm")
            label.setText(key)
            time_edit_start.setTime(QTime.fromString(value['start'], 'hh:mm'))
            time_edit_end.setTime(QTime.fromString(value['end'], 'hh:mm'))
            time_edit_start.timeChanged.connect(
                lambda time_, ln=key: self.time_edit_changed_special(time_, ln, False))  # false为start,true为end
            time_edit_end.timeChanged.connect(
                lambda time_, ln=key: self.time_edit_changed_special(time_, ln, True))
            self.time_edit_tableWidget_special.setCellWidget(row_position, 0, label)
            self.time_edit_tableWidget_special.setCellWidget(row_position, 1, time_edit_start)
            self.time_edit_tableWidget_special.setCellWidget(row_position, 2, time_edit_end)

    # 根据time_edit_tableWidget中的内容反向生成time_dict
    def time_edit_table_to_dict(self):
        self.time_dict.clear()  # 清空先
        # 遍历通用的并添加
        for table in [self.time_edit_tableWidget, self.time_edit_tableWidget_special]:  # 简化代码
            for i in range(table.rowCount()):
                label_text = table.cellWidget(i, 0).text()
                time_edit_start = table.cellWidget(i, 1).text()
                time_edit_end = table.cellWidget(i, 2).text()
                self.time_dict.update({label_text: {
                    "start": time_edit_start,
                    "end": time_edit_end
                }})

    def time_edit_changed(self, now_time: QTime, time_number: str, mode: bool):
        time_str = now_time.toString('hh:mm')
        if not mode:  # 如果为start
            self.time_dict[time_number]["start"] = time_str
        else:  # 为end
            self.time_dict[time_number]["end"] = time_str
        return

    def time_edit_changed_special(self, now_time: QTime, to_change: str, mode: bool):
        time_str = now_time.toString('hh:mm')
        if not mode:  # 如果为start
            self.time_dict[to_change]["start"] = time_str
        else:  # 为end
            self.time_dict[to_change]["end"] = time_str
        return

    def time_edit_adaptive_fonts(self, current):
        tab = self.set_time_tabWidget.widget(current)
        for i in tab.findChildren(QLabel):
            adaptive_label_font_size(i, 50, 1)
        for i in tab.findChildren(QPushButton):
            i.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            adaptive_label_font_size(i, 50, 1)
            i.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        for e in tab.findChildren(QLineEdit):
            adaptive_label_font_size(e, 50, 1)

    # //////////////////
    # 重置

    def open_resetting(self):
        self.tabWidget.setCurrentIndex(5)
        tab = self.tabWidget.widget(5)
        # 自适应字体
        for i in tab.findChildren((QPushButton, QCheckBox)):
            adaptive_label_font_size(i, 30, 1)
        # 设置一下选择框的大小不然瞎眼
        for i in tab.findChildren(QCheckBox):
            siz = i.font().pointSize()
            i.setStyleSheet(f"""
                QCheckBox {{
                    spacing: 5px;
                }}
                QCheckBox::indicator {{
                    width: {siz}px;
                    height: {siz}px;
                }}
                """)
            adaptive_label_font_size(i, 30, 1)
        # 选择要重置的项->用户点击触发->

    def start_the_reset(self):
        selected_files: list = []
        # 判断哪些被选中了然后添加一下
        if self.reset_program_config.isChecked():
            selected_files.append("program_config")
            self.reset_program_config.setChecked(False)
        if self.reset_daily_config.isChecked():
            selected_files.append("daily_config")
            self.reset_daily_config.setChecked(False)
        if self.reset_lessons.isChecked():
            selected_files.append("lessons")
            self.reset_lessons.setChecked(False)
        if self.reset_time.isChecked():
            selected_files.append("time")
            self.reset_time.setChecked(False)
        if len(selected_files) == 0:  # 啥也没选也想重置?
            QtWidgets.QMessageBox.warning(self, "警告", "请至少选择一个配置文件进行重置!")
            return
        compare_dict: dict = {
            "program_config": "程序基本设置",
            "daily_config": "今日配置",
            "lessons": "课表",
            "time": "课程时间"
        }
        confirm_message = "确定要重置以下配置文件吗?\n" + "\n".join(
            [f"{file}({compare_dict[file]})" for file in selected_files])
        # 和用户确认确实要重置
        reply = QMessageBox.question(self, "请进行确认", confirm_message,
                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.No:
            QMessageBox.information(self, "提示", "重置操作已中止")
            return
        reply = QMessageBox.question(self, "请再次进行确认重置操作", confirm_message,
                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.No:
            QMessageBox.information(self, "提示", "重置操作已中止")
            return
        # 进行一个简单的加法来保证安全
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        text, ok = QInputDialog.getText(self, "最后验证",
                                        f"{confirm_message}\n这是最后一次取消的机会\n如果确定重置,请输入{num1}+{num2}的结果:")
        if not ok or not text.isdigit() or int(text) != num1 + num2:  # 答案不对？那就爬
            QMessageBox.information(self, "提示", "重置操作已中止")
            return
        # 重置 先备份(移动，也就算做删除了->生成->读进来->设置开启状态为非
        if "program_config" in selected_files:
            backup('../data/program_config.json', '../data/backup/program_config',
                   self.program_config_dict["backup_slots"]["program_config"])
            initialize_the_file(version)
            self.program_config_dict = json.loads(read_file('../data/program_config.json'))
            self.program_config_opened: bool = False
        if "daily_config" in selected_files:
            backup('../data/daily_config.json', '../data/backup/daily_config',
                   self.program_config_dict["backup_slots"]["daily_config"])
            initialize_the_file(version)
            self.daily_config_dict = json.loads(read_file('../data/daily_config.json'))
            self.daily_config_opened: bool = False
            self.today_lessons_edit_opened: bool = False
        if "lessons" in selected_files:
            backup('../data/Curriculum/lessons.json', '../data/backup/lessons',
                   self.program_config_dict["backup_slots"]["lessons"])
            initialize_the_file(version)
            self.lessons_opened: bool = False
            self.lessons_dict = json.loads(read_file('../data/Curriculum/lessons.json'))
        if "time" in selected_files:
            backup('../data/Curriculum/time.json', '../data/backup/time',
                   self.program_config_dict["backup_slots"]["time"])
            initialize_the_file(version)
            self.time_opened: bool = False
            self.time_dict = json.loads(read_file('../data/Curriculum/time.json'))
        confirm_message = "\n".join(
            [f"{file}({compare_dict[file]})" for file in selected_files])
        QMessageBox.information(self, "提示", f"重置操作已完成\n重置了以下文件:\n{confirm_message}")

    # //////////////////
    # 保存并退出
    def save_and_exit(self):
        self.daily_config_dict["lessons_list"] = sorted(self.daily_config_dict["lessons_list"],
                                                        key=lambda x: x["start"])  # 对其中的数据按开始时间进行一次排序
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
        if list(self.time_dict.items()) != list(self.time_dict_mirror.items()):
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
        self.signal_exit_SettingsPage.emit()  # 退出!

    # 不保存并退出
    def do_not_save_and_exit(self):
        # 减少内存占用
        self.remove_unwanted()
        # 啥也不用干
        self.signal_exit_SettingsPage.emit()  # 退出!

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
    refresh_time_signal = pyqtSignal()  # 更新时间
    run_adaptive_text_edit_manually = pyqtSignal()  # 自适应homework和message的字体大小和比例 手动触发
    update_the_course_indicator_signal = pyqtSignal(int)  # 刷新课程指示器用的信号

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
        self.settings_page.signal_exit_SettingsPage.connect(self.exit_settings_page)  # 绑定设置退出的信号
        self.settings_.clicked.connect(self.show_settings_page)
        self.refresh_edit_size.timeout.connect(self.manually_refresh_the_text_edit_font)  # 超时后连接到更新字体
        self.refresh_time_signal.connect(self.refresh_time)
        self.run_adaptive_text_edit_manually.connect(self.manually_refresh_the_text_edit_font)
        self.update_the_course_indicator_signal.connect(self.refresh_the_course_indicator)
        # 变量初始化
        self.window_resized: bool = False  # 窗口大小曾经改变过
        self.settings_is_open: bool = False  # 设置页面开启状态
        self.screen_height = None
        self.screen_width = None
        self.lessons_status = None
        self.daily_config = json.loads(read_file("../data/daily_config.json"))
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
                self.update_the_course_indicator_signal.emit(0)
            # 更新一下课程表的指示器
            self.time_to_next.setPlainText(
                f"距离{self.daily_config['lessons_list'][0]['name']}还有{format_timedelta(time_to_datetime(self.daily_config['lessons_list'][0]['start'], now_time) - now_time)}"
            )
        # 上完最后一节课的情况 为1
        elif now_time > time_to_datetime(self.daily_config["lessons_list"][-1]["end"], now_time):
            if self.lessons_status != 1:
                self.lessons_status = 1
                self.update_the_course_indicator_signal.emit(1)
            self.time_to_next.setPlainText(
                f"已放学{format_timedelta(now_time - time_to_datetime(self.daily_config['lessons_list'][-1]['end'], now_time))}"
            )
        # 正常 正在上课的情况 为2
        else:
            for index, lesson in enumerate(self.daily_config["lessons_list"]):
                if time_to_datetime(lesson["start"], now_time) <= now_time < time_to_datetime(lesson["end"], now):
                    if self.next_lesson != index + 1:
                        self.next_lesson = index + 1
                        self.update_the_course_indicator_signal.emit(2)
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
            # 添加提示窗口提醒用户要从左上角进行关闭
            QMessageBox.information(self, "提醒",
                                    "请从左上角选择保存并退出/直接退出回到主窗口后再关闭应用",
                                    QMessageBox.Yes)  # 添加提示窗口提醒用户要从左上角进行关闭
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
        self.settings_page.signal_go_to_the_settings_page.emit()
        self.stackedWidget.setCurrentIndex(1)  # 切换到设置的堆叠布局
        self.settings_page.signal_switch_to_the_interface.emit()

    # 从设置界面退出
    def exit_settings_page(self):
        self.settings_is_open = False
        self.stackedWidget.setCurrentIndex(0)  # 切换到设置的堆叠布局
        # 刷新其他的数据 (暂完成？有bug以后再修
        self.daily_config = json.loads(read_file('../data/daily_config.json'))
        # 刷新program_config
        self.program_config = json.loads(read_file('../data/program_config.json'))
        program_config = self.program_config
        self.laa = int(program_config["layout_adjustment_accuracy"])
        self.min_font_size = int(program_config["minimum_font_size"])
        self.max_font_size = int(program_config["maximum_font_size"])
        self.resize_timer.setInterval(int(program_config['the_window_changes_the_refresh_time'] * 1000))
        self.findChild(QLabel, "next_lesson_indicator").setText(program_config['next_indicator_text'])
        self.findChild(QLabel, "now_lesson_indicator").setText(program_config['now_indicator_text'])

        # 刷新课表指示器
        self.window_resized: bool = False
        self.lessons_status = None  # 防止拒绝刷新
        self.next_lesson = None
        self.after_init()


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
        ReselectTheClassScheduleWindow = ReselectTheClassScheduleWindow(lessons_dict)
        app.exec()
        week_name = ReselectTheClassScheduleWindow.result
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
