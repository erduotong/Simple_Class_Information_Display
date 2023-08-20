# -*- coding: UTF-8 -*-
# ////////////////////////////////
# 这是更新模块!,相关的逻辑都写在这里啦
# ////////////////////////////////

import enum
import os.path
import shutil
import zipfile

import requests
from PyQt5.QtCore import QThread, pyqtSignal


class VersionStatus(enum.IntEnum):
    UpToDate = 0  # 无须更新
    Lower = 1  # 有新版本
    NoLink = 2  # 无下载链接
    Error = 3  # error


class DownloadStatus(enum.IntEnum):
    Success = 0  # 下载成功
    ErrorDownload = 1  # 下载时出错
    ErrorWriteChunk = 2  # 写入文件块时出错


# 思路            (这里要判断网络是否连接 没连接就不试了
# 获得更新检查权限->检查更新 如果有新版本就发射信号并且保存好可能会用的download url ->
# 启动下载 -> 等待下载完成(准备好就更改状态) -> 询问安装 -> os._exit(0)并且启动!
# TODO 应用名是Simple Class Information Display 打包成zip的时候应该把整个文件夹打包 其中包含一个app文件夹

def download_file(destination, download_url) -> DownloadStatus:
    """
    下载文件(单线程) 多线程不会写啊啊啊啊啊啊啊
    :param destination: 存储到哪里（包括后缀
    :param download_url: 下载链接
    :return: 下载状态
    """
    try:
        response = requests.get(download_url, stream=True, verify=False)

    except Exception:
        return DownloadStatus.ErrorDownload

    try:
        with open(destination, 'wb') as f:
            f.write(response.content)
    except Exception:
        return DownloadStatus.ErrorWriteChunk
    return DownloadStatus.Success


# 源代码会特殊处理
def check_helper(mode: str, where: str) -> DownloadStatus:
    """
    检查是否有辅助程序
    :param where: 从哪儿下?(github / gitee)
    :param mode: 模式 分为source(从源代码安装的)和exe(正常安装打包的exe)
    :return:下载的状态 也就相当于检索的状态了
    """
    file_type = 'pyw' if mode == 'source' else 'exe'
    file_path = f"../data/DownloadHelper/upgrade_helper.{file_type}"
    if os.path.exists(file_path):
        return DownloadStatus.Success

    if where == 'gitee':
        download_link = ('https://gitee.com/erduotong/Simple_Class_Information_Display/releases/download/v1.1'
                         '-upgrade_helper/upgrade_helper.pyw') if mode == 'source' else \
            ('https://gitee.com/erduotong/Simple_Class_Information_Display/releases/download/v1.1-upgrade_helper'
             '/upgrade_helper.exe')  # gitee 源代码/exe
    else:
        download_link = ('https://github.com/erduotong/Simple_Class_Information_Display/releases/download/v1.1'
                         '-upgrade_helper/upgrade_helper.pyw') if mode == 'source' else \
            ('https://github.com/erduotong/Simple_Class_Information_Display/releases/download/v1.1-upgrade_helper'
             '/upgrade_helper.exe')  # github 源代码/exe
    state = download_file(file_path, download_link)
    return state


class ProgramUpdater(QThread):
    get_latest_version_return = pyqtSignal(VersionStatus)  # 给下面的用于处理返回值 todo 绑定这个信号到那边的返回值处理

    def __init__(self, now_version: str, version_type: str, program_form: str):
        super().__init__()
        """
        :param now_version: 当前版本
        :param version_type: 版本类型(下载安装包的名称 包括后缀)
        :param program_form: 程序形式(source / exe)
        """
        # 需求变量
        self.version_type = version_type  # 版本类型一定要完全匹配!包括后缀名!
        self.program_form = program_form
        self.now_version = now_version
        self.new_version = None
        self.change_log = None
        self.download_url = None

    def run(self) -> None:
        pass

    def get_latest_version(self, mode: str) -> None:
        """
        获得最新的版本号,如果有就写入self中
        :param mode: 从哪个网站获取? 目前支持解析 github gitee 处获得的
        :return:0为无新版本 1为有新版本且一切正常 2为没有找到可用的新版下载链接 否则表明获得api的时候出错了
        """
        # 这里是判断api_link要在哪里的地方
        api_link: str = ''
        if mode == 'github':
            api_link = 'https://api.github.com/repos/erduotong/Simple_Class_Information_Display/releases/latest'
        elif mode == 'gitee':
            api_link = 'https://gitee.com/api/v5/repos/erduotong/Simple_Class_Information_Display/releases/latest'
        # 从api link获得后再去匹配mode
        response = requests.get(api_link, verify=False)  # 获得api数据
        if response.status_code != 200:  # 获取了不正常的数据
            self.get_latest_version_return.emit(VersionStatus.Error)
            self.quit()  # return
        response = response.json()  # 得到相应的数据

        if mode in ('github', 'gitee'):
            if response.get("name") == self.now_version:  # 版本相等的情况
                self.get_latest_version_return.emit(VersionStatus.UpToDate)
                self.quit()  # return
            self.new_version = response.get("name")
            self.change_log = response.get("body")
            # 遍历assets以获得匹配版本类型的download_url
            assets = response.get("assets")
            if any(i.get("name") == self.version_type for i in assets):
                self.download_url = response.get("browser_download_url")
                self.get_latest_version_return.emit(VersionStatus.Lower)
                self.quit()  # return
            self.get_latest_version_return.emit(VersionStatus.NoLink)
            self.quit()  # return
        self.get_latest_version_return.emit(VersionStatus.Error)
        self.quit()  # return

    def download_update(self, from_where: str) -> DownloadStatus:
        # 检查更新辅助程序

        status = check_helper(from_where, self.program_form)

        if status != DownloadStatus.Success:
            return status  # 出现错误
        # 下载文件
        if os.path.exists("../data/DownloadHelper/temp.zip"):
            os.remove("../data/DownloadHelper/temp.zip")
        if os.path.exists("../data/DownloadHelper/app"):
            shutil.rmtree("../data/DownloadHelper/app")
        status = download_file('../data/DownloadHelper/temp.zip', self.download_url)
        if status != DownloadStatus.Success:
            return status
        # 解压
        with zipfile.ZipFile('../data/DownloadHelper/temp.zip', 'r') as zip_ref:
            zip_ref.extractall('../data/DownloadHelper/')
        os.remove("../data/DownloadHelper/temp.zip")
        # 转移app文件夹

        if os.path.exists('../will_use'):  # 检查是否存在will_use并删除
            shutil.rmtree('../will_use')
        shutil.move('../data/DownloadHelper/app', '../will_use')

        return DownloadStatus.Success  # 顺利完成!
