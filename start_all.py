import subprocess
import time
import os
import sys

# 启动web服务
web_cmd = [sys.executable, 'start_web_app.py']
web_proc = subprocess.Popen(web_cmd)
print('已启动Web服务...')

# 等待Web服务端口可用
import socket
def wait_port(host, port, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except Exception:
            time.sleep(1)
    return False

if not wait_port('127.0.0.1', 5000, timeout=30):
    print('Web服务端口5000未就绪，启动失败！')
    web_proc.terminate()
    sys.exit(1)
print('Web服务端口已就绪，准备启动PepperCat桌宠...')

# 启动桌宠PepperCat
peppercat_dir = os.path.join(os.getcwd(), 'PepperCat-main')
peppercat_main = os.path.join(peppercat_dir, 'main.py')
if not os.path.exists(peppercat_main):
    print('未找到PepperCat桌宠入口 main.py！')
    web_proc.terminate()
    sys.exit(1)
peppercat_cmd = [sys.executable, peppercat_main]
peppercat_proc = subprocess.Popen(peppercat_cmd, cwd=peppercat_dir)
print('已启动PepperCat桌宠。')

# 等待桌宠进程结束
peppercat_proc.wait()
# 关闭web服务
web_proc.terminate()
print('PepperCat桌宠已退出，Web服务已关闭。') 