'''
Created on 2013-3-31
@author: Administrator
'''
from bot.const import FetchConst

class FetchConstant(FetchConst):
    
    DBConfig = u'db'
    DBConfig_dbname = u'dbname'
    DBConfig_port = u'port'
    DBConfig_user = u'user'
    DBConfig_passwd = u'passwd'
    DBConfig_host = u'host'
    DBConfig_charactset = u'charactset'

    OUTPUT_DIR = u"op_dir"
    START_TIME = u'starttime' # relate to file dir and file name
    
    LOG_FILE = u"LOG_FILE"
    LOG_CONFIG = u'log'
    LOG_CONFIG_OUTPUT_DIR = u'op_dir'
    
    CONFIG_DATA = u'config_data'
    
    DEVELOP_CONFIG = u"develop"
    DEVELOP_CONFIG_DEBUG = u"debug"
    
    LOG_CONSOLE_FLAG = u'console'
    
    PROXY_CONFIG = u'proxy'
    PROXY_CONFIG_SOURCE_TYPE = u'proxysourcetype'
    PROXY_CONFIG_IPPROXIES = u'ipproxies'
    PROXY_CONFIG_ENABLE = u'enable'
    
    PROXY_CONFIG_PROXY_GENERATOR = u'proxy_generator'

    MULTI = u'multi'
    
    PROXY_VALID_TIME = u"proxy_valid_time"
    
