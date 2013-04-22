# encoding=utf8
'''
Created on 2013-3-20
@author: corleone
'''
from bot.configutil import ConfigFile
from crawler.shc.fe.const import FEConstant as const
from multiprocessing import Process, Lock
from sched import scheduler
from scrapy.cmdline import execute
from scrapy.settings import CrawlerSettings
import collections
import datetime
import os
import time

lock = Lock()

class SpiderProcess(Process):
    
    def __init__(self, starttime, city_name, configdata):
        Process.__init__(self)
        self._starttime = starttime
        self.starttime = starttime.strftime('%Y%m%d%H%M%S')
        self.city_name = city_name
        self.configdata = dict(configdata)
        
        self.configdata[const.CURRENT_CITY] = city_name
    
    def unite_proxy(self, configdata):
        proxy_source_type_code = configdata[const.PROXY_CONFIG].get(const.PROXY_CONFIG_SOURCE_TYPE)
        if proxy_source_type_code == u'2':
            with open(u'enable_proxies.txt', u'r') as f:
                proxies = f.readlines()
            configdata[const.PROXY_CONFIG][const.PROXY_CONFIG_IPPROXIES] = u','.join(proxies)
            configdata[const.PROXY_CONFIG][const.PROXY_CONFIG_SOURCE_TYPE] = u'1'
            
        return configdata 
    
    def build_values(self):
        feconfig = self.configdata[const.FE_CONFIG]
        
        self.configdata = self.unite_proxy(self.configdata)
        
        try:
        #=======================================================================
        # if the city use the default config
        #=======================================================================
            city_config = eval(feconfig[self.city_name])
        except Exception:
            city_config = {}
        
        output_dir = self.configdata[const.LOG_CONFIG].get(const.LOG_CONFIG_OUTPUT_DIR)
        
        start_date = eval(feconfig[const.DEFAULT_START_DATE]).strftime(u'%Y-%m-%d')
        end_date = eval(feconfig[const.DEFAULT_END_DATE]).strftime(u'%Y-%m-%d')
        
        start_page = city_config.get(const.START_PAGE,
                                     feconfig[const.DEFAULT_START_PAGE])
        end_page = city_config.get(const.END_PAGE,
                                   feconfig[const.DEFAULT_END_PAGE])
        
        output_dir = os.sep.join([output_dir, self.starttime , ])
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        values = {const.START_TIME:self.starttime[:-2]
                  , const.CITY_NAME:self.city_name
                  , const.CURRENT_CITY:self.city_name
                  , const.CUSTOMER_FLAG:feconfig.get(const.CUSTOMER_FLAG, 1)
                  , const.OUTPUT_DIR:output_dir
                  , const.STARTDATE:city_config.get(const.STARTDATE, start_date)
                  , const.ENDDATE:city_config.get(const.ENDDATE, end_date)
                  , const.CONFIG_DATA:self.configdata
                  , const.START_PAGE:int(start_page)
                  , const.END_PAGE:int(end_page)
                  , const.LOCK:lock
                  , const.DOWNLOAD_DELAY:feconfig.get(const.DOWNLOAD_DELAY, 1)
                  , }
        
        console_flag = self.configdata[const.LOG_CONFIG].get(const.LOG_CONSOLE_FLAG)
        if console_flag != u'1':
            values[const.LOG_FILE] = os.sep.join([output_dir, self.starttime + u'.log' ])
        
        return values
    
    def run(self):
        try:
            
            values = self.build_values()
        except Exception as e:
            raise e
        settings = u'crawler.shc.fe.settings'
        module_import = __import__(settings, {}, {}, [''])
        settings = CrawlerSettings(module_import, values=values)
        execute(argv=["scrapy", "crawl", 'SHCSpider' ], settings=settings)

spider_process_mapping = {}

def read_config():
    cfg_path = os.sep.join([os.getcwd(), r'./fetch58.cfg'])
    configdata = ConfigFile.readconfig(cfg_path).data
    return configdata 

def add_task(root_scheduler):
    
    configdata = read_config()
    
#    if configdata[const.PROXY_CONFIG][const.PROXY_CONFIG_SOURCE_TYPE] != u'1':
#        assert 0, u'call corleone to extend the situation'
    
    city_names = configdata[const.FE_CONFIG][const.FE_CONFIG_CITIES].split(u',')
    processes = collections.deque()
    
    starttime = datetime.datetime.now()
    
    for city_name in city_names :
        p = SpiderProcess(starttime, city_name, configdata)
#        p.daemon=False
        spider_process_mapping[city_name] = p
        processes.append(p)
        
    if len(processes):
#        root_scheduler.enter(0, 1, processes.popleft().start, ())
        root_scheduler.enter(1, 1, check_add_process,
                             (spider_process_mapping, processes,
                              root_scheduler, configdata))
            
            
def check_add_process(spider_process_mapping, processes,
                      root_scheduler, configdata):
    
#    alives = filter(lambda x:x , [p.is_alive() for p in spider_process_mapping.values()])
    alives = filter(Process.is_alive, spider_process_mapping.values())
#    print len(alives)
    
    if len(processes):
        pool_size = int(configdata[const.FE_CONFIG].get(const.MULTI, 1))
        if len(alives) < pool_size:
            p = processes.popleft()
            print (u'%s enqueue %s ,pool size %d , %d cities '
                   'waiting ') % (datetime.datetime.now(), p.city_name,
                                  pool_size, len(processes))
            root_scheduler.enter(0, 1, p.start, ())
        #=======================================================================
        # check to add process 10 seconds later
        #=======================================================================
            if not len(processes):
                print (u'%s all process enqueue ...' % datetime.datetime.now())
                
        root_scheduler.enter(5, 1, check_add_process
                             , (spider_process_mapping, processes,
                                root_scheduler, configdata))
    else:
        if len(alives) == 0:
            print ('%s crawl finished ... ' % datetime.datetime.now())
        else :
            root_scheduler.enter(5, 1, check_add_process
                                 , (spider_process_mapping, processes,
                                    root_scheduler, configdata))
            
def fetch_proxy():
    module_ = __import__('crawler.httpproxy.settings', {}, {}, [''])
    values = {u'DOWNLOAD_DELAY':0,
            u'DOWNLOAD_TIMEOUT':1,
            u'RETRY_ENABLED':0
             }
    
    settings = CrawlerSettings(module_, values=values)
    execute(argv=["scrapy", "crawl", "FiveOneNewHTTPProxySpider" ], settings=settings)

def valid_proxy():
    module_ = __import__('crawler.httpproxy.settings', {}, {}, [''])
    values = {u'RETRY_ENABLED':0,
              u'DOWNLOAD_TIMEOUT':2,
              }
    settings = CrawlerSettings(module_, values=values)
    execute(argv=["scrapy", "crawl", "BaiDuHomePageSpider" ], settings=settings)
    

def prepare_proxies(configdata):
    
    if configdata[const.PROXY_CONFIG].get(const.PROXY_CONFIG_SOURCE_TYPE, u'1') != u'2':
        return 
    
    p = Process(group=None, target=fetch_proxy,)
    p.start()
    p.join()
    
    print u'%s get %d free proxy' % (datetime.datetime.now(),
                                   len(open(u'proxy.txt', u'r').readlines()))
    
    c = Process(group=None, target=valid_proxy,)
    c.start()
    
    valid_time = int(configdata[const.PROXY_CONFIG].get(const.PROXY_VALID_TIME))
    print u'%s following %d seconds will valid the proxy' % (datetime.datetime.now(), valid_time)
    
    for i in range(valid_time):
        if not c.is_alive():
            break
    
        time.sleep(1)
    
    c.terminate()
    
    print u'%s get %d effective proxy' % (datetime.datetime.now(),
                                len(open(u'enable_proxies.txt', u'r').readlines()))

if __name__ == '__main__':
    
#    root_scheduler = scheduler(time.time, time.sleep)
#    root_scheduler.enter(0, 0, add_task, (root_scheduler,))
#    root_scheduler.run()
    
    configdata = read_config()
    prepare_proxies(configdata)
    
    root_scheduler = scheduler(time.time, time.sleep)
    root_scheduler.enter(0, 0, add_task, (root_scheduler,))
    root_scheduler.run()

