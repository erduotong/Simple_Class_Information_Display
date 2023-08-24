# daily_config.json

[回到README](../../README.md)

## 基本信息:

**警告 不建议直接对文件进行修改 如果要修改参数请前往设置页面修改**  
在从文件直接修改前 请关闭Simple Class Information Display防止出错

* 配置文件位置:data/daily_config.json

## 可配置项说明

* date_time: 创建这个配置文件的时间
* lessons_list: 存储当天所有的课表
    * name: 名称
    * start: 开始的时间
    * end: 结束的时间
  > 时间和课程都位于Curriculum文件夹内 lessons内的special代表特殊课程(无单独的槽位显示)
  以及还会自动填充课间到剩下的时间内(也没有单独的槽)  
  > 如果需要更改,请保证时间的连贯性 保证不会有没有在中间的无课程安排的时间或者出现重叠的时间 并且保证时间单调递增 否则无法保证程序不会出问题
* backup: 存储信息的备份 每次输入结束或者按刷新字体时备份 程序启动的时候自动恢复
    * msg: 消息的备份
    * homework: 作业的备份