# 存储课程
>位置: data/Curriculum/lessons.json

## 
存有monday到sunday,special,with_homework总共9个列表  
例如:
```json
{
    "monday": ["None"],       
    "tuesday": ["None"],     
    "wednesday": ["None"],   
    "thursday": ["None"],   
    "friday": ["None"],   
    "saturday": ["None"],   
    "sunday": ["None"],   
    "special": ["None"],   
    "with_homework": ["None"]   
}
```
其中monday-sunday存储每天的课程列表，例如
```
"monday": ["数学","语文","道法","生物","英语","自习","音乐","班会"]
```
如果是这样的:
```"sunday": ["None"],```那么就会有窗口询问你要替换到哪一天的课程  

special内存储的是特殊课程，这种课程不会拥有独立的课程槽位，需要共有一个槽位 并且**每天都会生成** 基本上可以看作是无序的 最后程序会按时间给daily_config排序的 
>注意 special内的课程一定要在time.json里面写有时间设置 否则会导致程序无法启动

with_homework内存储的是拥有作业的课程，会交给函数自动生成今天的作业放在作业的textBrowser内
