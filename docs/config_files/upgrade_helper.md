# upgrade_config.json

[回到README](../../README.md)

## 基本信息:

**警告:为需求文件 请勿修改 并且此设置无任何需求进行更改**

* 配置文件位置:data/DownloadHelper/update_config.json

## 可配置项说明

* state: 当前处于的状态 0等待操作 1为正在检测更新 2为等待下载更新 3为正在下载 4为等待安装
* update_from: 从哪里下载更新 0为gitee 1为github
* check_update_when_start: 是否在启动的时候自动检测更新
* last_download_url: 存储上一次搜索到的下载链接 用于继续下载