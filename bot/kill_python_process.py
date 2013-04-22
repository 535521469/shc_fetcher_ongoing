# encoding=utf8
'''
Created on 2013-4-5
@author: Administrator
'''
import os
import psutil
import signal

for p in psutil.get_process_list():
#    print p
    if p.name ==u'python.exe':
        if p.pid != os.getpid():
            print os.getpid()
            os.kill(p.pid, signal.SIGILL)
