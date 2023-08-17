# -*- coding: utf-8 -*-
from functions import *


def daily_initialization(week_name):  # 每日的配置文件生成函数
    with open("../data/program_config.json", "r") as f:
        config = json.loads(f.read())
    if not os.path.exists("../data/daily_config.json"):
        with open("../data/daily_config.json", "w"):
            pass
    now_datetime = datetime.datetime.now()
    try:
        data = json.loads(read_file("../data/daily_config.json"))
        if data["date_time"] == now_datetime.strftime("%Y_%m_%d") and data["lessons_list"]:
            return  # 文件中的日期等于当前日期且lessons_list不为空，返回
    except:
        pass
    backup("../data/daily_config.json", "../data/backup/daily_config", config["backup_slots"]["daily_config"])
    daily_config = {
        "date_time": datetime.datetime.now().strftime("%Y_%m_%d"),
        "lessons_list": populate_the_timesheet(week_name),
        "backup": {
            "msg": "",
            "homework": ""
        }
    }
    daily_config["backup"]["homework"] = generate_homework(daily_config["lessons_list"])
    write_file('../data/daily_config.json', json.dumps(daily_config, ensure_ascii=False, indent=4))
