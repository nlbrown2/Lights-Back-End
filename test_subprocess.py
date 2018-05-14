import subprocess
from time import sleep
import os

proc = subprocess.Popen(['nice', '-19', 'python', 'test_call.py'])
print("started process")
os.system('ps aux | grep Python')
sleep(10)
print(proc.pid)
proc.kill()
print("killed process I hope")
# cmd = 'ps -p ' + str(pid)
# os.system(cmd)
