# program_config.json

[回到README](../../README.md)

## 基本信息:

**警告 不建议直接对文件进行修改 如果要修改参数请前往设置页面修改**  
在从文件直接修改前 请关闭Simple Class Information Display防止出错

* 配置文件位置:data/program_config.json

## 可配置项说明

* version: 程序的版本号
* backup_slots: 程序的备份槽位设置
    * program_config: 程序配置文件的备份数量
    * daily_config: 每日生成的配置文件的备份数量
    * time: 时间配置文件的备份数量
    * lessons: 课程配置文件的备份数量
* refresh_time: 主窗口刷新时间的间隔
* layout_adjustment_accuracy：比值精度 用于自适应调节两个东西时候的int比值精度 越大精度越高 推荐使用100就足够了
  输入时强制转换int
* minimum_font_size：自动调节字体大小时的最小值
* maximum_font_size：自动调节字体大小时的最大值
* time_font_size：显示时间的Label的字体大小
* text_edit_refresh_time: 编辑完文本后 自动刷新字体大小的时间
* the_window_changes_the_refresh_time：窗口大小改变后刷新字体的时间
* now_indicator_text: 现在的课程指示器的显示的文本 如<Now
* next_indicator_text: 下一节课的课程指示器的显示的文本 如<Next
