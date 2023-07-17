# Simple_Class_Information_Display

[![Generic badge](https://img.shields.io/badge/编写于_Python_版本-3.11.3-blue.svg)](https://Python.org)

### 强烈建议**阅读完成readme**后再开始操作/下载

> 如果你无法正常访问github进行下载，可以尝试从仓库的[gitee](https://gitee.com/erduotong/Simple_Class_Information_Display)
> 下载  
> [gitee](https://gitee.com/erduotong/Simple_Class_Information_Display)
> 的仓库更新可能不及时，推荐从仓库的[github](https://github.com/erduotong/Simple_Class_Information_Display)查看&下载

## 适用场景

开发是为了在学校进行使用 用于自动展示作业，课表等。减少一些日常的枯燥劳动。同时也方便进行使用

## 下载

### 选择qdarkstyle

你可以选择是否含有qdarkstyle进行美化
> 含有的话，就是这样:

![含有qdarkstyle的情况](./images/with_qdarkstyle.png '含有qdarkstyle的情况')
> 不含有的话，就是这样:

![不含有qdarkstyle的情况](./images/without_qdarkstyle.png '不含有qdarkstyle的情况')

### 从源码启动

> 不推荐，除非你知道你在做什么 推荐[从exe启动](#从exe启动)

如果你已经拥有**Python环境**并且可以使用**pip安装需要的依赖库** 你可以尝试从源码启动  
你可以在[这里](https://www.python.org/)安装python
如果你需要**qdarkstyle**美化,请选择**source_code_with_qdarkstyle**下载  
如果不需要**qdarkstyle**,请选择**source_code_without_qdarkstyle**  
请在[Releases](https://github.com/erduotong/Simple_Class_Information_Display/releases/latest)下载  
如果你正在使用gitee,请点击[这个链接](https://gitee.com/erduotong/Simple_Class_Information_Display/releases/latest)

### 从exe启动

**推荐的方式**  
相比从源码启动，会占用较多的空间(容纳了运行库) 但是不需要python解释器和PyQt等 已经打包  
如果你需要**qdarkstyle**美化,请选择**exe_with_qdarkstyle**下载  
如果不需要**qdarkstyle**,请选择**exe_without_qdarkstyle**下载  
请在[Releases](https://github.com/erduotong/Simple_Class_Information_Display/releases/latest)下载  
如果你正在使用gitee,请点击[这个链接](https://gitee.com/erduotong/Simple_Class_Information_Display/releases/latest)下载

## 使用

在下载压缩包后,解压到一个你喜欢的位置。随后打开解压出来的文件夹，再打开其中的app文件夹  
如果你**从源码启动**,打开其中的main.pyw  
如果你**从exe启动**,打开其中的Simple_Class_Information_Display.exe
如果觉得太麻烦，可以创建快捷方式  
启动后程序会在你解压出来的文件夹生成data文件夹，程序的配置等都位于其中。
在更改之前，请**阅读完下面的文档**。如果有某个配置文件损坏，删掉/点击重置，程序会重新生成

## 文档
#### 使用相关
* [设置页面](./docs/about_settings.md)
#### 配置文件

* [daily_config.json 今日配置文件](./docs/daily_config_meaning.md)
* [program_config.json 程序配置文件](./docs/program_config_meaning.md)
* [lessons.json 课表的存储文件](./docs/lessons.md)
* [time.json 课表对应的时间的存储文件](./docs/time.md)

#### 其他

* [快捷键](./docs/shortcut.md)

#### 可能有帮助的东西

使用的nuitka打包的指令:

```shell
nuitka --standalone --mingw64 --show-memory --show-progress  --enable-plugin=pyqt5 --follow-imports --remove-output --output-dir=../exe --windows-disable-console main.py
```

## 更新计划

* 用GUI更改当天的配置文件,课程时间等
* 自动生成值日表并展示
* 左侧的作业和信息编辑框可以更改颜色等

## 感谢

* PyQt5,Qt5:GUI
* qdarkstyle:好看的深色qss

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
