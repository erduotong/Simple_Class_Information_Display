# -*- coding: UTF-8 -*-
# ////////////////////////////////
# 这是更新模块!,相关的逻辑都写在这里啦
# ////////////////////////////////
import json

import requests


# 思路            (这里要判断网络是否连接 没连接就不试了
# 获得更新检查权限->检查更新 如果有新版本就发射信号并且保存好可能会用的download url ->


class ProgramUpdater(object):
    def __init__(self, now_version, version_type):
        # 需求变量
        self.version_type = version_type  # 版本类型一定要完全匹配!包括后缀名!
        self.now_version = now_version
        self.new_version = ""
        self.change_log = ""
        self.download_url = ""

    def get_latest_version(self, mode: str, api_link: str) -> int:
        """
        获得最新的版本号,如果有就写入self中
        :param mode: 从哪个网站获取? 目前支持解析 github gitee 处获得的
        :param api_link: 要获得的链接
        :return:0为无新版本 1为有新版本且一切正常 2为没有找到可用的新版下载链接 否则表明获得api的时候出错了
        """
        # 从api link获得后再去匹配mode
        response = requests.get(api_link)  # 获得api数据
        if response.status_code != 200:  # 获取了不正常的数据
            return response.status_code
        response = json.loads(response.json())  # 得到相应的数据
        if mode == 'github' or mode == 'gitee':
            if response.get("name") == self.now_version:  # 版本相等的情况
                return 0
            self.new_version = response.get("name")
            self.change_log = response.get("body")
            # 遍历assets以获得匹配版本类型的download_url
            if any(i.get("name") == self.version_type for i in response.get("assets")):
                self.download_url = response.get("download")
                return 1
            return 2
