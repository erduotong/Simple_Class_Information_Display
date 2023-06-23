# 每日配置文件
>位置: data/daily_config.json
* date_time: 创建这个配置文件的时间
* lessons_list: 存储当天所有的课表
  * name: 名称
  * start: 开始的时间
  * end: 结束的时间
  * >时间和课程都位于Curriculum文件夹内 lessons内的special代表特殊课程(无单独的槽位显示) 以及还会自动填充课间到剩下的时间内(也没有单独的槽)
* backup: 存储信息的备份
  * msg: 消息的备份
  * homework: 作业的备份