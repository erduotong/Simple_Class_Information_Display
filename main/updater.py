# -*- coding: UTF-8 -*-
# ////////////////////////////////
# 这是更新模块!,相关的逻辑都写在这里啦
# ////////////////////////////////

import enum
import json
import requests
import os
from concurrent.futures import ThreadPoolExecutor


class VersionStatus(enum.IntEnum):
    UpToDate = 0  # 无须更新
    Lower = 1  # 有新版本
    NoLink = 2  # 无下载链接
    Error = 3  # error


class DownloadStatus(enum.IntEnum):
    Success = 0  # 下载成功
    ErrorGetSize = 1  # 获取文件大小时出错
    ErrorDownload = 2  # 下载时出错
    ErrorWriteChunk = 3  # 写入文件块时出错


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

    def get_latest_version(self, mode: str, api_link: str) -> VersionStatus:
        """
        获得最新的版本号,如果有就写入self中
        :param mode: 从哪个网站获取? 目前支持解析 github gitee 处获得的
        :param api_link: 要获得的链接
        :return:0为无新版本 1为有新版本且一切正常 2为没有找到可用的新版下载链接 否则表明获得api的时候出错了
        """
        # 从api link获得后再去匹配mode
        response = requests.get(api_link)  # 获得api数据
        if response.status_code != 200:  # 获取了不正常的数据
            return VersionStatus.Error
        response = json.loads(response.json())  # 得到相应的数据
        if mode in ('github', 'gitee'):
            if response.get("name") == self.now_version:  # 版本相等的情况
                return VersionStatus.UpToDate
            self.new_version = response.get("name")
            self.change_log = response.get("body")
            # 遍历assets以获得匹配版本类型的download_url
            assets = response.get("assets")
            if any(i.get("name") == self.version_type for i in assets):
                self.download_url = response.get("browser_download_url")
                return VersionStatus.Lower
            return VersionStatus.NoLink
        return VersionStatus.Error

    def download_new_version(self, destination) -> DownloadStatus:
        """
        下载新版本并在完成时改名为complete
        :param destination:下载数据保存文件的路径(包括后缀名)
        :return:状态
        """
        # noinspection PyBroadException
        try:  # 获取文件大小
            response = requests.get(self.download_url, stream=True)
            file_size = int(response.headers.get('Content-Length', 0))  # 获得文件大小
        except:  # 获取的时候出现错误了
            return DownloadStatus.ErrorGetSize

        # noinspection PyBroadException
        try:  # 下载文件!
            pass #todo
        except:  # 没下成功
            return DownloadStatus.ErrorDownload
