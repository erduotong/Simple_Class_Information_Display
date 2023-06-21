import json
import time
import shutil
import datetime
import os
from PyQt5.QtGui import QFont
from PyQt5 import QtGui
import schedule
import win32gui
from PyQt5 import QtWidgets


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
        if data["date_time"] == datetime.datetime.now().strftime("%Y_%m_%d"):
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
        schedule.run_pending()
        time.sleep(sec)
        window.refresh_time_singal.emit()


# 获得实际的行数 包括自动换行 传入控件
def get_visible_line_count(text_edit):
    line_count = 0
    block = text_edit.document().begin()
    while block.isValid():
        line_count += block.layout().lineCount()
        block = block.next()
    return line_count


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
    # 如果出现了滚动条，则将字体大小减小1
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



