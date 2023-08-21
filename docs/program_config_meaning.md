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
* update: 更新相关的选项
  * state: 当前处于的状态 0表示啥事没有 1表示正在检测更新 2表示等待用户下载 3表示正在下载 4表示等待安装 
  * update_from : 更新源位于列表中的索引(0:github 1:gitee)
  * check_update_when_star: 是否在启动程序的时候进行一次更新检测？