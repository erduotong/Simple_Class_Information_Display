import os
import shutil
import subprocess
import time

# 等待1秒防止出问题
time.sleep(1)

# 重命名目录
shutil.move("../../app", "../../will_delete")
shutil.move("../../will_use", "../../app")

# 更改工作目录
os.chdir("../../app")

# 执行程序
subprocess.Popen(['pythonw', './Simple Class Information Display.pyw'])
