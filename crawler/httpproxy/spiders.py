# encoding=utf8
'''
Created on 2013-4-10
@author: corleone
'''
from crawler.httpproxy.items import IPProxyItem
from scrapy import log
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

class FiveOneHomeSpider(BaseSpider):
    name = u"FiveOneHomeSpider"
    home_page = u'http://51dai.li/'

class FiveOneNewHTTPProxySpider(FiveOneHomeSpider):
    
    name = u"FiveOneNewHTTPProxySpider"
    
    start_urls = [u'%shttp_fast.html' % FiveOneHomeSpider.home_page,
                  #=============================================================
                   u'%shttp_anonymous.html' % FiveOneHomeSpider.home_page,
#                   u'%shttp_non_anonymous.html' % FiveOneHomeSpider.home_page,
                  #=============================================================
                  ]
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        tb_tags = hxs.select(u'//div[@id="tb"]/table')
        
        with open(u'proxy.txt', 'w') :pass
#            f.write(u'http://%s:%s\n' % (ip_td, port_td))
            
        for tr_tag in tb_tags.select('tr'):
            
            td_tags = tr_tag.select('td/text()').extract()
            if td_tags:
                idx_td, ip_td, port_td, country_td = td_tags
                ipi = IPProxyItem()
                ipi['ip'] = ip_td
                ipi['port'] = port_td
                
#                if country_td != u"CN":
#                    continue
                
#                try:
#                    map(int, ip_td.split(u'.'))
#                except Exception:
#                    continue
                
                with open(u'proxy.txt', 'a') as f:
                    f.write(u'http://%s:%s\n' % (ip_td, port_td))
                
                
class BaiDuHomePageSpider(BaseSpider):
    
    name = u'BaiDuHomePageSpider'
    
    def start_requests(self):
        
        proxies = []
        with open(u'proxy.txt', u'r') as f:
            proxies = map(str.strip, f.readlines())
        
        proxies = set(proxies)
        with open(u'enable_proxies.txt', u'w') :pass
        
        for proxy in proxies:
            yield Request(u'http://www.ip138.com/',
                          meta={u'proxy':proxy},
                          dont_filter=True)
        
    
    def parse(self, response):
        
        if response.status == 200:
            meta = response.request.meta
            with open(u'enable_proxies.txt', u'a')as f:
                self.log(u'check %s is enable' % meta[u'proxy'], log.INFO)
                f.write(meta[u'proxy'] + u'\n')
        
    
    
