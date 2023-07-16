# 程序配置文件

> 位置: data/program_config.json

* version: 程序的版本号
* backup_slots: 程序的备份槽位设置
    * daily_config: 每日生成的配置文件的备份数量
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