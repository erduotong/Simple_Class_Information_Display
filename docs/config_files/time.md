# time.json

[回到README](../../README.md)

## 基本信息:

**警告 不建议直接对文件进行修改 如果要修改参数请前往设置页面修改**  
在从文件直接修改前 请关闭Simple Class Information Display防止出错

* 配置文件位置:data/Curriculum/time.json

## 可配置项说明

l1-ln 程序会在根据选择的星期数查看[lessons](lessons.md)中今天的课程, 并且根据课程数选则l1-l课程数的时间,依次进行对应  
其余的为lessons中special课程的对应时间 special内的每节课必须有对应的 否则程序会发生崩溃
<details>
  <summary>一个写好的示例</summary>

```json
{
  "l1": {
    "start": "08:30",
    "end": "09:15"
  },
  "l2": {
    "start": "09:25",
    "end": "10:10"
  },
  "l3": {
    "start": "10:20",
    "end": "11:05"
  },
  "l4": {
    "start": "11:15",
    "end": "12:00"
  },
  "l5": {
    "start": "14:00",
    "end": "14:45"
  },
  "l6": {
    "start": "14:55",
    "end": "15:40"
  },
  "l7": {
    "start": "15:55",
    "end": "16:40"
  },
  "l8": {
    "start": "16:50",
    "end": "17:35"
  },
  "早操": {
    "start": "07:40",
    "end": "08:10"
  },
  "晨读": {
    "start": "08:15",
    "end": "08:30"
  },
  "延时服务": {
    "start": "17:45",
    "end": "18:30"
  },
  "中午休息": {
    "start": "12:00",
    "end": "13:40"
  }
}
```

</details>


