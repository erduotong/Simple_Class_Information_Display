import json
import time
import shutil
import datetime
import os
from PyQt5 import QtWidgets
import win32gui


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
    lessons_list = json.loads(read_file("../data/Curriculum/lessons.json"))
    lessons_list = lessons_list[weekday]
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
    for lesson_name in ["早读", "延时服务", "晨读", "中午休息"]:
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


# 清理不需要的WorkerW窗口
def pretreatmentHandle():
    hwnd = win32gui.FindWindow("Progman", "Program Manager")
    win32gui.SendMessageTimeout(hwnd, 0x052C, 0, None, 0, 0x03E8)
    hwnd_WorkW = None
    while 1:
        hwnd_WorkW = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
        if not hwnd_WorkW:
            continue
        hView = win32gui.FindWindowEx(hwnd_WorkW, None, "SHELLDLL_DefView", None)
        if not hView:
            continue
        h = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
        while h:
            win32gui.SendMessage(h, 0x0010, 0, 0)  # WM_CLOSE
            h = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
        break
    return hwnd
