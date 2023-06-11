import datetime
from function import *


def daily_initialization():  # 每日的配置文件生成函数
    with open("../data/program_config.json", "r") as f:
        config = json.loads(f.read())
    if not os.path.exists("../data/daily_config.json"):
        with open("../data/daily_config.json", "w"):
            pass
    try:
        with open("../data/daily_config.json", "r") as f:
            if json.loads(f.read())["date_time"] == datetime.datetime.now().strftime("%Y_%m_%d"):
                return
    except:
        pass
    backup("../data/daily_config.json", "../data/backup/daily_config", config["backup_slots"]["daily_config"])
    # todo 将lessons里面的和时间一一对应并且补全课间&延时服务等
    daily_config = {
        "date_time": datetime.datetime.now().strftime("%Y_%m_%d")
    }
    with open("../data/daily_config.json", "w") as f:
        f.write(json.dumps(daily_config))
