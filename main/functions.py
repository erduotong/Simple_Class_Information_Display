import json
import os
import shutil
from datetime import *
import time
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel


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
        os.remove(backups[0])


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
        if data["date_time"] == datetime.now().strftime("%Y_%m_%d"):
            return True  # 文件中的日期等于当前日期，返回
        else:
            return False
    except:
        return False  # 文件损坏或者不相等


# schedule计时任务的运行模块 传入等待时间
def run_schedule(sec: float, window) -> None:
    # 对齐整数秒
    time_to_next_second = 1 - time.time() % 1
    time.sleep(time_to_next_second)
    while 1:
        time.sleep(sec)
        window.refresh_time_singal.emit()


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
    # 计算合适的字体大小
    font_size = min_size
    font = QFont()
    while font_size < max_size:
        font.setPointSize(font_size)
        for text_edit in text_edits:
            text_edit.setFont(font)
        if any(text_edit.verticalScrollBar().isVisible() for text_edit in text_edits):
            font_size -= 1
            break
        font_size += 1
    while any(text_edit.verticalScrollBar().isVisible() for text_edit in text_edits):
        font_size -= 1
        font.setPointSize(font_size)
        for text_edit in text_edits:
            text_edit.setFont(font)
    if font_size <= 0:  # 否则就出bug了
        font_size = 1
    font.setPointSize(font_size)
    for text_edit in text_edits:
        text_edit.setFont(font)


# 设置字体大小 传入对象以及要设置的字体大小
def adjust_font_size(obj, font_size: int) -> None:
    font = QtGui.QFont()
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
    dt = datetime(now.year, now.month, now.day, hour, minute)
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
def initialize_the_file() -> None:
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
            "backup_slots": {
                "daily_config": 5
            },
            "refresh_time": "1",
            "layout_adjustment_accuracy": 100,
            "minimum_font_size": 20,
            "maximum_font_size": 80,
            "time_font_size": 51,
            "text_edit_refresh_time": 2,
            "now_indicator_text": "<Now",
            "next_indicator_text": "<Next",
            "desktop_wallpaper_mode": "false"
        }
    }
    for filepath, content in path.items():
        if not os.path.exists(filepath):  # 判断文件是否存在，如果不存在则创建
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=4, ensure_ascii=False)  # 把content写入文件中


# 自适应QLabel的字体大小
def adaptive_label_font_size(label, max_size: int, min_size: int) -> None:
    """
    自适应QLabel的字体大小
    :param label:要设置的label
    :param max_size: 最大大小
    :param min_size: 最小大小
    :return: None
    """
    # 获取当前label的宽度和高度
    label_width = label.width()
    label_height = label.height()
    # 创建字体对象，并设置初始字体大小
    font = QtGui.QFont()
    font.setPointSize(max_size)
    # 获取字体度量对象
    fm = QtGui.QFontMetrics(font, label)
    # 获取当前文本在初始字体下的行宽和行高
    text_width = fm.width(label.text())
    text_height = fm.lineSpacing()
    # 如果文本宽度超过了label宽度，或者文本高度超过了label高度，则逐步缩小字体大小
    while text_width > label_width or text_height > label_height:
        font.setPointSize(font.pointSize() - 1)
        fm = QtGui.QFontMetrics(font, label)
        text_width = fm.width(label.text())
        text_height = fm.lineSpacing()
        if font.pointSize() < min_size:
            break
    # 将动态调整后的字体应用到label上
    label.setFont(font)
