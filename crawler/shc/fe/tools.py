# encoding=utf8
'''
Created on 2013-3-31
@author: Administrator
'''
from functools import wraps
from scrapy import log
from scrapy.http.request import Request
from scrapy.selector import HtmlXPathSelector
from uuid import uuid4
import os

def ignore_notice(parse):
    
    @wraps(parse)
    def parse_simulate(self, response):
        '''
        the page is not exist
        '''
        hxs = HtmlXPathSelector(response)
        notice_div = hxs.select('//div[@id="Notice"]')
        url = response.url
        cookies = response.request.cookies
        if notice_div:
            file_name = unicode(uuid4())
            file_path = os.sep.join([
                         self.build_ignore_file_dir(response.request.cookies),
                         file_name])
            
            if self.is_develop_debug(cookies):
                with open(file_path + u'.html', u'wb') as f:
                    f.write(response.body)
            self.log((u'ignore crawl , with Notice div %s, '
                                '%s') % (url, file_name), log.INFO)
        else:
            rss = parse(self, response)
            for rs in rss:
                if isinstance(rs, Request):
                    rs = rs.replace(dont_filter=True)
                    yield rs
    return parse_simulate

def check_verification_code(parse):
    @wraps(parse)
    def parse_simulate(self, response):
        '''
        need you to input verification code
        '''
        cookies = response.request.cookies
        
        hxs = HtmlXPathSelector(response)
        verification_div = hxs.select('//div[@class="w_990"]')
        url = response.url
        if verification_div:
            self.log(u'need input verification code crawl %s' % url,
                     log.CRITICAL)
            
            precede_url = url[url.index(u'url=') + 4:]
            shield_file_name = self.get_random_id()
            
            self.log((u'use ip proxy to request %s again , '
                      'shield %s') % (precede_url, shield_file_name),
                     log.INFO)
            
            proxy = self.get_next_proxy(cookies)
                        
            if self.is_develop_debug(cookies):
                self.save_body(self.build_shield_file_dir(cookies),
                                shield_file_name + u'.html', response)
            
            yield Request(precede_url, self.parse, meta={'proxy':proxy},
                          cookies=cookies, dont_filter=True)
        else:
            rss = parse(self, response)
            for rs in rss:
                if isinstance(rs, Request):
                    rs = rs.replace(dont_filter=True)
                    yield rs
                
    return parse_simulate

def check_blank_page(parse):
    @wraps(parse)
    def parse_simulate(self, response):
        '''
        the whole page is blank 
        '''
        cookies = response.request.cookies
        if not len(response.body.strip()):
            url = response.url
            self.log(u'the page is blank %s' % url,
                     log.CRITICAL)
            
            blank_file_name = self.get_random_id()
            
            self.log((u'use ip proxy to request %s again , '
                      'blank %s') % (url, blank_file_name),
                     log.INFO)
            
            if self.is_develop_debug(cookies):
                self.save_body(self.build_blank_file_dir(cookies),
                                blank_file_name + u'.html', response)
            
            proxy = self.get_next_proxy(cookies)
            yield Request(url, self.parse,
                          meta={'proxy':proxy},
                          cookies=cookies,
                          dont_filter=True)
        else:
            rss = parse(self, response)
            for rs in rss:
                if isinstance(rs, Request):
                    rs = rs.replace(dont_filter=True)
                    yield rs
                
    return parse_simulate

def check_verification_code_gif(parse):
    @wraps(parse)
    def parse_simulate(self, response):
        '''
        need you to input verification code
        '''
        try:
            cookies = response.request.cookies
            hxs = HtmlXPathSelector(response)
            verification_div = hxs.select('//div[@class="w_990"]')
            url = response.url
            if verification_div:
                self.log(u'need input verification code crawl %s' % url,
                         log.CRITICAL)
                
                precede_url = url[url.index(u'url=') + 4:]
                shield_file_name = self.get_random_id()
                
                self.log((u'use ip proxy to request %s again , '
                          'shield %s') % (precede_url, shield_file_name),
                         log.INFO)
                proxy = self.get_next_proxy(cookies)
                
                if self.is_develop_debug(cookies):
                    self.save_body(self.build_shield_file_dir(cookies),
                                    shield_file_name + u'.html', response)
                
                yield Request(precede_url, self.parse, meta={'proxy':proxy},
                              cookies=cookies, dont_filter=True)
                    
        except Exception:
            rss = parse(self, response)
            if rss:
                for rs in rss:
                    if isinstance(rs, Request):
                        rs = rs.replace(dont_filter=True)
                        yield rs
                
    return parse_simulate
        
def with_ip_proxy(parse):
    @wraps(parse)
    def parse_simulate(self, response):
        
        cookies = response.request.cookies

        rss = parse(self, response)
        if rss:
            for rs in rss:
                if isinstance(rs, Request) and self.get_ipproxy_enable(cookies):
                    proxy = self.get_next_proxy(cookies)
                    rs = rs.replace(meta={'proxy':proxy}).replace(dont_filter=True)
                    msg = (u'%s use proxy %s access '
                           '%s ') % (self.get_current_city(cookies),
                                        proxy,
                                        rs.url) 
                    self.log(msg, log.INFO)
                    yield rs
                else:
                    yield rs
        
    return parse_simulate
        
