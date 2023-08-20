# -*- coding: UTF-8 -*-
# ////////////////////////////////
# 这是更新模块!,相关的逻辑都写在这里啦
# ////////////////////////////////

import enum
import shutil
import zipfile
from pathlib import Path

import requests
from PyQt5.QtCore import QThread, pyqtSignal


class VersionStatus(enum.IntEnum):
    UpToDate = 0  # 无须更新
    Lower = 1  # 有新版本
    NoLink = 2  # 无下载链接
    Error = 3  # error
    GithubToFast = 4  # github api访问过快


class DownloadStatus(enum.IntEnum):
    Success = 0  # 下载成功
    ErrorDownload = 1  # 下载时出错
    ErrorWriteChunk = 2  # 写入文件块时出错


# 思路            (这里要判断网络是否连接 没连接就不试了
# 获得更新检查权限->检查更新 如果有新版本就发射信号并且保存好可能会用的download url ->
# 启动下载 -> 等待下载完成(准备好就更改状态) -> 询问安装 -> os._exit(0)并且启动!
# TODO 应用名是Simple Class Information Display 打包成zip的时候应该把整个文件夹打包 其中包含一个app文件夹
# TODO 类要记得deletelater并且disconnect

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
    if Path(file_path).exists():
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


class GetLatestVersion(QThread):
    get_latest_version_return = pyqtSignal(VersionStatus)

    def __init__(self, update_source: str, update_parameters):
        """
        获取最新的版本号，如果有就写入update_parameters 信号return
        :param update_source: 更新源
        :param update_parameters: 外部dict的引用
        """
        super().__init__()
        self.update_parameters = update_parameters
        self.mode = update_source

    def run(self):
        api_link_dict = {
            "github": 'https://api.github.com/repos/erduotong/Simple_Class_Information_Display/releases/latest',
            "gitee": 'https://gitee.com/api/v5/repos/erduotong/Simple_Class_Information_Display/releases/latest'}
        api_link: str = api_link_dict[self.mode]  # 这里是判断api_link要在哪里的地方
        response = requests.get(api_link, verify=False)  # 获得api数据
        if response.status_code != 200:
            self.get_latest_version_return.emit(VersionStatus.Error)
            return
        response = response.json()  # 得到相应的数据
        if "documentation_url" in response:  # github的访问过快
            self.get_latest_version_return.emit(VersionStatus.GithubToFast)
            return
        if self.mode in ("github", "gitee"):
            if response.get("name") == self.update_parameters["now_version"]:
                self.get_latest_version_return.emit(VersionStatus.UpToDate)
                return
            self.update_parameters["new_version"] = response.get("name")
            self.update_parameters["change_log"] = response.get("body")
            # 遍历assets以获得匹配版本类型的download_url
            assets = response.get("assets")
            if any(i.get("name") == self.update_parameters["version_type"] for i in assets):
                self.update_parameters["download_url"] = response.get("browser_download_url")
                self.get_latest_version_return.emit(VersionStatus.Lower)
                return
            self.get_latest_version_return.emit(VersionStatus.NoLink)
            return
        self.get_latest_version_return.emit(VersionStatus.Error)
        return


class DownloadUpdate(QThread):
    download_update_return = pyqtSignal(DownloadStatus)

    def __init__(self, update_source: str, update_parameters):
        """
        下载更新
        :param update_source: 更新源
        :param update_parameters: 外部dict的引用
        """
        super().__init__()
        self.update_parameters = update_parameters
        self.from_where = update_source

    def run(self):
        # 检查更新辅助程序
        status = check_helper(self.from_where, self.update_parameters["program_form"])
        if status != DownloadStatus.Success:
            self.download_update_return.emit(status)  # 出现错误
            return
        # 下载文件
        temp_path = Path('../data/DownloadHelper/temp.zip')
        temp_path.unlink(missing_ok=True)
        if Path("../data/DownloadHelper/app").exists():
            shutil.rmtree("../data/DownloadHelper/app")

        status = download_file('../data/DownloadHelper/temp.zip', self.update_parameters["download_url"])
        if status != DownloadStatus.Success:
            self.download_update_return.emit(status)  # 出现错误
            return
        # 解压
        with zipfile.ZipFile('../data/DownloadHelper/temp.zip', 'r') as zip_ref:
            zip_ref.extractall('../data/DownloadHelper/')
        Path("../data/DownloadHelper/temp.zip").unlink(missing_ok=True)
        # 转移app文件夹
        if Path('../will_use').exists():  # 检查是否存在will_use并删除
            shutil.rmtree('../will_use')
        shutil.move('../data/DownloadHelper/app', '../will_use')
        self.download_update_return.emit(DownloadStatus.Success)
        return


