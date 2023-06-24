import subprocess
import sys

libraries = ['PyQt5']
for library in libraries:
    try:
        # 检查库是否已经安装
        __import__(library)
        print(f"{library}已安装")
    except ImportError:
        # 如果库未安装，则安装它
        print(f"{library}未安装,安装中......")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', library])
print("Finish!")
input("按enter键退出或直接关闭本窗口")
