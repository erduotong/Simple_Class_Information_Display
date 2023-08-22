# -*- coding: utf-8 -*-
import ctypes
import datetime
import json
import os
import re
import shutil
import threading
import time

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetricsF
from PyQt5.QtWidgets import QLabel, QTimeEdit, QListWidget


# 备份 分别为:路径,目标路径,备份槽位,
def backup(path: str, destination_path: str, backup_slot: int) -> None:
    # 备份文件名中的时间戳
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    # 获取备份文件的原文件名和扩展名
    file_name, file_ext = os.path.splitext(os.path.basename(path))
    # 生成备份文件名
    backup_name = f"{timestamp}_{file_name}{file_ext}"
    # 移动文件到目标目录
    backup_path = os.path.join(destination_path, backup_name)
    shutil.move(path, backup_path)
    # 列出目标文件夹中的所有备份文件，并按修改时间进行排序
    backups = os.listdir(destination_path)
    backups = [os.path.join(destination_path, f) for f in backups]
    backups.sort(key=lambda f: os.path.getmtime(f))
    # 如果备份文件数量超过 backup_slot，删除最早的备份文件
    if len(backups) > backup_slot:
        for i in backups[:-backup_slot]:
            os.remove(i)


# 读取文件函数
def read_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# 写入文件函数
def write_file(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# 输入:星期几,全小写 周六日会返回一个空的列表
def populate_the_timesheet(weekday: str):
    if weekday == "saturday" or weekday == "sunday":  # 可以自定义
        # 返回空~
        return [{'name': 'None', 'start': '00:01', 'end': '23:59'}]
    time_dict = json.loads(read_file("../data/Curriculum/time.json"))
    lessons_list_a = json.loads(read_file("../data/Curriculum/lessons.json"))
    lessons_list = lessons_list_a[weekday]

    # 创建一个空列表 start_end_times，用于存储各节课程的开始和结束时间
    start_end_times = []
    # 读取每个课程的时间信息并将其添加到 start_end_times 中
    for i in range(len(lessons_list)):
        lesson_name = lessons_list[i]  # 获取当前课程名称
        time_info = time_dict["l" + str(i + 1)]  # 提取当前课程的时间信息
        start_time = time_info["start"]  # 提取当前课程的开始时间
        end_time = time_info["end"]  # 提取当前课程的结束时间
        start_end_times.append(
            dict(name=lesson_name, start=start_time, end=end_time))  # 将当前课程的时间信息存储到 start_end_times 中
    # 将特殊课程的时间信息添加到 start_end_times 中
    for lesson_name in lessons_list_a['special']:
        if lesson_name in time_dict:
            start_time = time_dict[lesson_name]["start"]
            end_time = time_dict[lesson_name]["end"]
            start_end_times.append(dict(name=lesson_name, start=start_time, end=end_time))
    # 对 start_end_times 中的课程按照开始时间进行排序
    sorted_times = sorted(start_end_times, key=lambda x: x["start"])
    # 用列表 lst 来记录排序后的课程及其对应的时间信息
    lst = []
    last_end_time = None
    # 处理每节课程的开始和结束时间，并在每节课程之间添加课间时间
    for time_info in sorted_times:
        lesson_name = time_info["name"]
        start_time = time_info["start"]  # 当前课程的开始时间
        end_time = time_info["end"]  # 当前课程的结束时间
        if last_end_time is not None and start_time > last_end_time:
            # 如果上一节课结束时间和当前课程的开始时间之间有空闲时间，就添加上课间时间
            interval_name = "课间"
            interval_time = dict(name=interval_name, start=last_end_time, end=start_time)
            lst.append(interval_time)
        lst.append(dict(name=lesson_name, start=start_time, end=end_time))
        last_end_time = end_time  # 更新上一节课的结束时间
    return lst


# 比较两个时间是不是一样的
def compareTime():
    try:
        data = json.loads(read_file("../data/daily_config.json"))

        if data["date_time"] == datetime.datetime.now().strftime("%Y_%m_%d"):
            return True  # 文件中的日期等于当前日期，返回
        else:
            return False
    except:
        return False  # 文件损坏或者不相等


# schedule计时任务的运行模块 传入等待时间
def run_schedule(sec: int, window) -> None:
    # 对齐整数秒
    time_to_next_second = 1 - time.time() % 1
    time.sleep(time_to_next_second)
    while 1:
        time.sleep(sec)
        window.refresh_time_signal.emit()


# 获得实际的行数 包括自动换行 传入控件
def get_visible_line_count(text_edit):
    a_line_count = text_edit.document().lineCount()
    line_count = 0
    block = text_edit.document().begin()
    while block.isValid():
        line_count += block.layout().lineCount()
        block = block.next()
    return max(line_count, a_line_count)


# 传入:调整的的text_edits的列表 最小值 最大值
def adjust_the_text_edit_font_size(text_edits, min_size: int, max_size: int) -> None:
    font = QFont("黑体")  # 默认为黑体

    def set_font_size(size):
        nonlocal font
        font.setPointSize(size)
        for text_edit in text_edits:
            text_edit.setFont(font)

    def is_scrollbar_visible():
        return any(text_edit.verticalScrollBar().isVisible() for text_edit in text_edits)

    left = min_size
    right = max_size
    while left <= right:
        mid = (left + right) // 2
        set_font_size(mid)
        if is_scrollbar_visible():
            right = mid - 1
        else:
            left = mid + 1

    optimal_font_size = right

    if optimal_font_size <= 0:  # 否则就出bug了
        optimal_font_size = 1

    set_font_size(optimal_font_size)
    return


# 设置字体大小 传入对象以及要设置的字体大小
def adjust_font_size(obj, font_size: int) -> None:
    font = QtGui.QFont("黑体")
    font.setPointSize(font_size)
    obj.setFont(font)


def time_to_datetime(time_str, now):
    """
    :param time_str: 类似‘11:45’这样的字符串输入
    :param now: 现在的时间，datetime.now()获得的
    :return:一个和datetime.now()一样的格式
    """
    # 获取当前时间
    # 解析输入的时间字符串，获取小时和分钟
    hour, minute = map(int, time_str.split(":"))
    # 构造一个日期时间对象，将时分秒设置为输入的时间
    dt = datetime.datetime(now.year, now.month, now.day, hour, minute)
    return dt


# 格式化倒计时字符串
def format_timedelta(delta):
    """
    格式化倒计时字符串
    :param delta:timedelta对象
    :return:小于60s: xx秒 小于1h:xx:xx 否则xx:xx:xx
    """
    total_seconds = delta.total_seconds()
    if total_seconds < 60:
        return f"{int(total_seconds)}秒"
    elif total_seconds < 3600:
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    else:
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds - hours * 3600) // 60)
        seconds = int(total_seconds - hours * 3600 - minutes * 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# 生成作业
def generate_homework(lessons) -> str:
    """
    生成作业 按照with_homework的顺序
    :param lessons:传入daily_config中的lessons这个列表
    :return: 作业 包括换行
    """
    lessons_with_homework = json.loads(read_file("../data/Curriculum/lessons.json"))["with_homework"]
    return_lessons = []
    return_str = ''
    for i in lessons:
        if i['name'] in lessons_with_homework:
            return_lessons.append(i['name'])
    for i in lessons_with_homework:
        if i in return_lessons:
            return_str += f'*{i}:\n'
    return return_str


# 传入daily_config和now_lesson，获得now_lesson在daily_config中的第几个同名
def search_now_lessons(daily_config: dict, next_lesson: dict):
    """
    传入daily_config和now_lesson，获得now_lesson在daily_config中的第几个同名
    :param daily_config: self.daily_config
    :param next_lesson: 要找的下一节课
    :return: 位于第几个
    """
    tot: int = 0
    for i in daily_config["lessons_list"]:
        if i['name'] == next_lesson['name']:
            tot += 1
        if i == next_lesson:
            break
    return tot


# 用于给指示现在课程和下一个课程的QLabel简化代码
def initialize_label_indicator(name: str, text: str):
    """
    用于给指示现在课程和下一个课程的QLabel简化代码
    :param name:要设置的对象名
    :param text:要设置的文本
    :return:初始化好的QLabel
    """
    label = QLabel()
    label.setObjectName(name)
    font = QFont("黑体", 16)
    font.setWeight(QFont.Bold)
    label.setFont(font)
    label.setAlignment(Qt.AlignCenter)
    label.setText(text)
    label.hide()
    return label


# 检查文件是否存在并在不存在时初始化
def initialize_the_file(version: str) -> None:
    """
    检查文件是否存在并在不存在时初始化 路径写在内部
    :return: None
    """
    path = {
        "../data/Curriculum/lessons.json": {
            "monday": ["None"],
            "tuesday": ["None"],
            "wednesday": ["None"],
            "thursday": ["None"],
            "friday": ["None"],
            "saturday": ["None"],
            "sunday": ["None"],
            "special": ["None"],
            "with_homework": ["None"]
        },
        "../data/Curriculum/time.json": {
            "l1": {
                "start": "00:01",
                "end": "23:55"
            },
            "None": {
                "start": "23:55",
                "end": "23:59"
            }
        },
        "../data/program_config.json": {
            "version": version,
            "backup_slots": {
                "program_config": 5,
                "daily_config": 5,
                "time": 5,
                "lessons": 5
            },
            "refresh_time": 1,
            "layout_adjustment_accuracy": 100,
            "minimum_font_size": 20,
            "maximum_font_size": 200,
            "time_font_size": 51,
            "text_edit_refresh_time": 5,
            "the_window_changes_the_refresh_time": 0.7,
            "now_indicator_text": "<Now",
            "next_indicator_text": "<Next"

        },
        "../data/DownloadHelper/update_config.json": {
            "state": 0,
            "update_from": 1,
            "check_update_when_start": True,
            "last_download_url": None
        }
    }
    for filepath, content in path.items():
        if not os.path.exists(filepath):  # 判断文件是否存在，如果不存在则创建
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=4, ensure_ascii=False)  # 把content写入文件中
    config = json.loads(read_file('../data/program_config.json'))
    if 'version' in config and config['version'] == version:
        return

    # 包含一下~
    def update_dict(dict1, dict2):
        for key in dict1:
            if key in dict2:
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    update_dict(dict1[key], dict2[key])
                else:
                    # 检查类型是否一致
                    if isinstance(dict2[key], type(dict1[key])):
                        dict1[key] = dict2[key]
                    else:
                        try:
                            # 尝试转换类型
                            converted_value = type(dict1[key])(dict2[key])
                            dict1[key] = converted_value
                        except (ValueError, TypeError):
                            # 转换失败，从 dict1 中复制
                            dict1[key] = dict1[key]
        return dict1

    config = update_dict(path['../data/program_config.json'], config)
    config['version'] = version
    write_file('../data/program_config.json', json.dumps(config, ensure_ascii=False, indent=4))


# 自适应一些控件的字体大小(例如QPushButton/QLabel)
def adaptive_label_font_size(label, max_size: int, min_size: int) -> None:
    """
    自适应QLabel的字体大小
    :param label:要设置的label
    :param max_size: 最大大小
    :param min_size: 最小大小
    :return: None
    """
    if min_size > max_size:
        max_size, min_size = min_size, max_size
    contents_rect = label.contentsRect()
    label_width = contents_rect.width()
    label_height = contents_rect.height()
    text = label.text()
    text = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', text)
    # 设置初始字体大小，根据初始标签大小和文本大小评估
    initial_font_size = (max_size + min_size) // 2
    font = label.font()
    font.setFamily("黑体")
    font.setPointSize(initial_font_size)

    # 使用二分法进行快速搜索
    while max_size >= min_size:
        current_font_size = (max_size + min_size) // 2
        font.setPointSize(current_font_size)

        # 测量文本的尺寸
        fm = QFontMetricsF(font)
        text_width = fm.boundingRect(text).width()
        text_height = fm.lineSpacing()
        # 根据文本尺寸调整搜索范围
        if text_width > label_width or text_height > label_height:
            max_size = current_font_size - 1
        else:
            min_size = current_font_size + 1
    # 使用最终确定的字体大小
    font.setPointSize(max_size)
    label.setFont(font)
    return


def adaptive_item_font_size(item, max_size: int, min_size: int, widget) -> None:
    """
    自适应各种item的字体大小
    :param item:要设置的item
    :param max_size: 最大大小
    :param min_size: 最小大小
    :param widget: 在哪个widget里面?
    :return: None
    """
    if min_size > max_size:
        max_size, min_size = min_size, max_size
    contents_rect = widget.visualItemRect(item)
    item_width = contents_rect.width()
    item_height = contents_rect.height()
    text = item.text()
    text = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', text)
    # 设置初始字体大小，根据初始标签大小和文本大小评估
    initial_font_size = (max_size + min_size) // 2
    font = item.font()
    font.setFamily("黑体")
    font.setPointSize(initial_font_size)

    # 使用二分法进行快速搜索
    while max_size >= min_size:
        current_font_size = (max_size + min_size) // 2
        font.setPointSize(current_font_size)

        # 测量文本的尺寸
        fm = QFontMetricsF(font)
        text_width = fm.boundingRect(text).width()
        text_height = fm.lineSpacing()
        # 根据文本尺寸调整搜索范围
        if text_width > item_width or text_height > item_height:
            max_size = current_font_size - 1
        else:
            min_size = current_font_size + 1
    # 使用最终确定的字体大小
    font.setPointSize(max_size)
    item.setFont(font)
    return


class ShowUserLoading(threading.Thread):
    def __init__(self, to_set_label, text: str):
        threading.Thread.__init__(self)
        self.to_set_label = to_set_label
        self.text = text

    def run(self):
        try:
            sleep_time = 0.2
            while True:
                self.to_set_label.setText(f"{self.text} |")
                time.sleep(sleep_time)
                self.to_set_label.setText(f"{self.text} /")
                time.sleep(sleep_time)
                self.to_set_label.setText(f"{self.text} -")
                time.sleep(sleep_time)
                self.to_set_label.setText(f"{self.text} \\")
                time.sleep(sleep_time)
        finally:
            return

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop_thread(self):
        thread_id = self.get_id()
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                   ctypes.py_object(SystemExit))


# 重写QTimeEdit 更严格的QTimeEdit 用户不可以用滚轮修改
class StrictQTimeEdit(QTimeEdit):
    def wheelEvent(self, event):
        event.ignore()


# 重写QListWidget 实现了其中任意行发生变化的时候发射items_changed信号
class ListWidgetWithRowChanged(QListWidget):
    itemsChanged = pyqtSignal()

    def insertItem(self, row, item):
        super().insertItem(row, item)
        self.itemsChanged.emit()

    def addItem(self, item):
        super().addItem(item)
        self.itemsChanged.emit()

    def takeItem(self, row):
        item = super().takeItem(row)
        self.itemsChanged.emit()
        return item

    def clear(self):
        super().clear()
        self.itemsChanged.emit()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.itemsChanged.emit()
