import json
import time
import shutil
import datetime
import os
from collections import OrderedDict


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


# todo 补全课表函数 先根据l1~l8填充然后填早读,最后把课间填上(从最早到最晚的空隙,如果到了end就跳转到下一个进行计时
# 输入:星期几,全小写
def populate_the_timesheet(weekday: str):
    if weekday == "saturday" or weekday == "sunday":  # 可以自定义
        # 解析为python对象,调用方法是[0][None][start]这样的,表示一整天都是空的
        return json.loads('[{"None": {"start": "00:01", "end": "23:59", }}]')
    time_dict = json.loads(read_file("../data/Curriculum/time.json"))
    lessons_dict = json.loads(read_file("../data/Curriculum/lessons.json"))
    lessons_dict = lessons_dict[weekday]



populate_the_timesheet("monday")
