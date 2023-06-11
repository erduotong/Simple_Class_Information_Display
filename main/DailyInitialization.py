import datetime
from function import *


def daily_initialization():  # 每日的配置文件生成函数
    with open("../data/program_config.json", "r") as f:
        config = json.loads(f.read())
    if not os.path.exists("../data/daily_config.json"):
        with open("../data/daily_config.json", "w"):
            pass
    now_datetime = datetime.datetime.now()
    try:
        with open("../data/daily_config.json", "r") as f:
            if json.loads(f.read())["date_time"] == now_datetime.strftime("%Y_%m_%d"):
                return
    except:
        pass
    backup("../data/daily_config.json", "../data/backup/daily_config", config["backup_slots"]["daily_config"])
    week_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][now_datetime.weekday()]
    daily_config = {
        "date_time": datetime.datetime.now().strftime("%Y_%m_%d"),
        "lessons_list": populate_the_timesheet(week_name)
    }
    write_file('../data/daily_config.json', json.dumps(daily_config, ensure_ascii=False, indent=4))
