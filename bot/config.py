# encoding=UTF-8
'''
Created on 2013-4-22
@author: Administrator
'''
from bot.configutil import ConfigFile
import os

def read_config():
    cfg_path = os.sep.join([os.getcwd(), r'./fetch58.cfg'])
    configdata = ConfigFile.readconfig(cfg_path).data
    return configdata 

configdata = read_config()
