# Simple Class Information Display

[![Generic badge](https://img.shields.io/badge/编写于_Python_版本-3.11.3-blue.svg?style=for-the-badge)](https://Python.org)
[![Generic badge](https://img.shields.io/badge/PYTHON_版本支持-3.8_+-blue.svg?style=for-the-badge)](https://Python.org)
![](https://img.shields.io/github/last-commit/erduotong/Simple_Class_Information_Display?style=for-the-badge)

> 如果无法正常访问仓库的[Github](https://gitee.com/erduotong/Simple_Class_Information_Display)
> 进行下载, 可以从仓库的[Gitee](https://gitee.com/erduotong/Simple_Class_Information_Display)进行下载

## 快捷跳转目录

<details>
  <summary>点击展开</summary>

* [Simple Class Information Display](#simple-class-information-display)
    * [快捷跳转目录](#快捷跳转目录)
    * [概述](#概述)
    * [下载](#下载)
        * [选择qdarkstyle](#选择qdarkstyle)
        * [安装形式](#安装形式)
            * [从安装包安装](#从安装包安装)
            * [从程序压缩包安装](#从程序压缩包安装)
            * [从源码安装](#从源码安装)
    * [首次使用](#首次使用)
        * [从安装包启动](#从安装包启动)
        * [从程序压缩包启动](#从程序压缩包启动)
        * [从源码启动](#从源码启动)
    * [文档](#文档)
    * [更新计划](#更新计划)
    * [分享协议](#分享协议)
        * [署名-非商业性使用-相同方式共享 4.0 国际 (CC BY-NC-SA 4.0)](#署名-非商业性使用-相同方式共享-40-国际-cc-by-nc-sa-40)

</details>

## 概述

这是一个信息展示的软件 针对在学校中的使用场景进行设计(如灵活调整, 自动生成) 减少一些枯燥的, 重复的工作

---

## 下载

### 选择qdarkstyle

程序有两种形式:有qdarkstyle和无qdarkstyle 请参见下图  
如果选择需要qdarkstyle(右图), 请在下载时选择带有 with_qdarkstyle 的(例如exe_with_qdarkstyle)  
如果选不需要qdarkstyle(左图), 请在下载时选择带有 without_qdarkstyle 的(例如source_without_qdarkstyle)

<p align="left">↓左侧: 无qdarkstyle</p>
<p align="right">右侧: 有qdarkstyle↓</p>

![](./images/with_and_without_qdarkstyle.png)

### 安装形式

* [从安装包安装](#从安装包安装) **(推荐)** 请优先选择
* [从程序压缩包安装](#从程序压缩包安装)
* [从源代码安装]()

##### 从安装包安装

该方式会下载一个安装程序, 安装程序将会根据要求帮助安装 不需要解释器等运行环境 程序安装包内已经包含所需    
不推荐**非Windows**系统的用户使用 使用了Windows API(ShellExecute)于更新程序中 除非您确定它可以正常运作  
如果你需要[qdarkstyle](#选择qdarkstyle), 请选择"Simple_Class_Information_Display_Setup.with_qdarkstyle.exe" 下载  
如果你不需要[qdarkstyle](#选择qdarkstyle), 请选择"Simple_Class_Information_Display_Setup.without_qdarkstyle.exe" 下载  
Github用户请在Github的 ->[Releases](https://github.com/erduotong/Simple_Class_Information_Display/releases/latest)<-
进行下载  
Gitee用户请在Gitee的 ->[Releases](https://github.com/erduotong/Simple_Class_Information_Display/releases/latest)<- 进行下载

##### 从程序压缩包安装

该方式会下载程序的打包后的文件 不需要解释器等运行环境 程序打包后以已经包含所需
不推荐**非Windows**系统的用户使用 使用了Windows API(ShellExecute)于更新程序中 除非您确定它可以正常运作
下载完成后, 请解压后阅读其中的readme.txt
如果你需要[qdarkstyle](#选择qdarkstyle), 请选择"exe_with_qdarkstyle.zip" 下载  
如果你不需要[qdarkstyle](#选择qdarkstyle), 请选择"exe_without_qdarkstyle.zip" 下载  
Github用户请在Github的 ->[Releases](https://github.com/erduotong/Simple_Class_Information_Display/releases/latest)<-
进行下载  
Gitee用户请在Gitee的 ->[Releases](https://github.com/erduotong/Simple_Class_Information_Display/releases/latest)<- 进行下载

##### 从源码安装

该方式会下载程序的源代码 需要Python解释器和一些库 下列是详细要求

* Python解释器 3.8+
* PyQt5
* qdarkstyle (如果你选择了使用qdarkstyle的版本)
* requests
* urllib3

下载完成后, 请解压后阅读其中的readme.txt 并且运行setup_lib.py使用pip安装所需运行库  
如果你需要[qdarkstyle](#选择qdarkstyle), 请选择"source_with_qdarkstyle.zip" 下载  
如果你不需要[qdarkstyle](#选择qdarkstyle), 请选择"source_without_qdarkstyle.zip“ 下载  
Github用户请在Github的 ->[Releases](https://github.com/erduotong/Simple_Class_Information_Display/releases/latest)<-
进行下载  
Gitee用户请在Gitee的 ->[Releases](https://github.com/erduotong/Simple_Class_Information_Display/releases/latest)<- 进行下载

---

## 首次使用

> 后续的使用方法请查看[使用/功能教程](./docs/how_to_use.md)

##### 从安装包启动

如果勾选了安装包创建快捷方式, 直接启动即可  
如果没有快捷方式, 请打开安装目录的文件夹中的app文件夹, 并运行其中的Simple Class Information Display.exe

##### 从程序压缩包启动

打开解压后的文件夹中的app文件夹 并运行其中的Simple Class Information Display.exe

##### 从源码启动

先运行setup_lib.py使用pip安装所需运行库(或者自行安装)  
随后运行安装文件夹中的app文件夹中的Simple Class Information Display.pyw

---

## 文档

* [Simple Class Information Display 使用方法](./docs/how_to_use.md)

<details>
  <summary>配置文件</summary>

* [程序配置文件(program_config.json)](./docs/config_files/program_config.md)
* [每日配置文件(daily_config.json)](./docs/config_files/daily_config.md)
* [时间生成配置文件(time.json)](./docs/config_files/time.md)
* [课程生成配置文件(lessons.json)](./docs/config_files/lessons.md)

</details>

---

## 更新计划

- [ ] 使用方法README

---

## 支持Simple Class Information Display
如果你认为Simple Class Information Display很好用, 可以帮助您的话  
可以考虑一下支持我更好的开发?  
[去爱发电看看!](https://afdian.net/a/erduotong)

## 分享协议

<https://creativecommons.org/licenses/by-nc-sa/4.0/>

#### 署名-非商业性使用-相同方式共享 4.0 国际 (CC BY-NC-SA 4.0)

这是一份普通人可以理解的许可协议概要 (但不是替代) 。 免责声明.

您可以自由地：

共享 — 在任何媒介以任何形式复制、发行本作品

演绎 — 修改、转换或以本作品为基础进行创作

只要你遵守许可协议条款，许可人就无法收回你的这些权利。

惟须遵守下列条件：

署名 — 您必须给出地当的署名，提供指向本许可协议的链接，同时标明是否（对原始作品）作了修改。您可以用任何合理的方式来署名，但是不得以任何方式暗示许可人为您或您的使用背书。

非商业性使用 — 您不得将本作品用于商业目的。

相同方式共享 — 如果您再混合、转换或者基于本作品进行创作，您必须基于与原先许可协议地同的许可协议 分发您贡献的作品。

没有附加限制 — 您不得适用法律术语或者 技术措施 从而限制其他人做许可协议允许的事情。

声明：

您不必因为公共领域的作品要素而遵守许可协议，或者您的使用被可适用的 例外或限制所允许。

不提供担保。许可协议可能不会给与您意图使用的所必须的所有许可。例如，其他权利比如形象权、隐私权或人格权可能限制您如何使用作品。
