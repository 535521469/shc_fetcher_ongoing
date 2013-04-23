# encoding=utf8
'''
Created on 2013-3-20
@author: corleone
'''
from crawler.shc.fe.const import FEConstant as const
from multiprocessing import Process
from sched import scheduler
from scrapy.cmdline import execute
from scrapy.settings import CrawlerSettings
import collections
import datetime
import time
from bot.config import configdata

class SpiderProcess(Process):
    
    def __init__(self, city_name, configdata):
        Process.__init__(self)
        self.city_name = city_name
        self.configdata = dict(configdata)
        self.configdata[const.CURRENT_CITY] = city_name
    
    def run(self):
        feconfig = self.configdata[const.FE_CONFIG]
        try:
        #=======================================================================
        # if the city use the default config
        #=======================================================================
            city_config = eval(feconfig[self.city_name])
        except Exception:
            city_config = {}
        
        start_page = city_config.get(const.START_PAGE,
                             feconfig[const.DEFAULT_START_PAGE])
        end_page = city_config.get(const.END_PAGE,
                                   feconfig[const.DEFAULT_END_PAGE])
        
        values = {
                  const.CONFIG_DATA:self.configdata,
                  const.START_PAGE:int(start_page),
                  const.END_PAGE:int(end_page),
                  }
        
        settings = u'crawler.shc.fe.settings'
        module_import = __import__(settings, {}, {}, [''])
        settings = CrawlerSettings(module_import, values=values)
        execute(argv=["scrapy", "crawl", 'SHCSpider' ], settings=settings)

spider_process_mapping = {}

def add_task(root_scheduler):
    
    city_names = configdata[const.FE_CONFIG][const.FE_CONFIG_CITIES].split(u',')
    processes = collections.deque()
    
    for city_name in city_names :
        p = SpiderProcess(city_name, configdata)
        spider_process_mapping[city_name] = p
        processes.append(p)
        
    if len(processes):
        root_scheduler.enter(1, 1, check_add_process,
                             (spider_process_mapping, processes,
                              root_scheduler, configdata))
            
def check_add_process(spider_process_mapping, processes,
                      root_scheduler, configdata):
    
    alives = filter(Process.is_alive, spider_process_mapping.values())
    
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
    while 1:
        
#        prepare_proxies(configdata)
        
        root_scheduler = scheduler(time.time, time.sleep)
        root_scheduler.enter(0, 0, add_task, (root_scheduler,))
        root_scheduler.run()

