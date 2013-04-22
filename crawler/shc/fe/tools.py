# encoding=utf8
'''
Created on 2013-3-31
@author: Administrator
'''
from bot.dbutil import FetchSession
from bot.item import CarInfo, SellerInfo
from crawler.shc.fe.item import SHCFEShopInfoConstant
from crawler.tools import gen_uuid
from functools import wraps
from scrapy import log
from scrapy.http.request import Request
from scrapy.selector import HtmlXPathSelector
from uuid import uuid4
import datetime
import os
from crawler.shc.fe.const import FEConstant

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
        

def check_detail_duplicate(parse):
    
    @wraps(parse)
    def parse_simulate(self, response):
        rss = parse(self, response)
        from crawler.shc.fe.spiders import CarDetailSpider, CarListSpider
        if rss:
            for rs in rss:
                if rs.callback.im_class == CarDetailSpider:
                    if isinstance(rs, Request):
                        fs = FetchSession()
                        try:
                            if fs.query(CarInfo).filter(CarInfo.sourceurl == rs.url).all():
                                self.log(u'give up fetched url %s' % rs.url, log.INFO)
                            else:
                                ci = CarInfo()
                                ci.sourceurl = rs.url
                                ci.sourcetype = u'58'
                                ci.cityname = self.get_current_city(rs.cookies)
                                fs.add(ci)
                                fs.commit()
                                yield rs
                        except Exception as e:
                            self.log(u'something wrong %s' % str(e), log.CRITICAL)
                        finally:
                            fs.close()
                elif rs.callback.im_class == CarListSpider:
                    yield rs
                    
    return parse_simulate

def save_detail(parse):
    
    @wraps(parse)
    def parse_simulate(self, response):
        rss = parse(self, response)
        from crawler.shc.fe.spiders import PersonPhoneSpider, CustomerShopSpider
        if rss:
            for rs in rss:
                fs = FetchSession()
                try:
                    if isinstance(rs, Request):
                        cookies = rs.cookies
                        sellerinfo = cookies[FEConstant.sellerinfo]
                        sourceurl = sellerinfo.get(SHCFEShopInfoConstant.info_url)
                        ci = fs.query(CarInfo).filter(CarInfo.sourceurl == sourceurl).first()
                        if ci is not None:
                            ci.statustype = 1
                            ci.title = sellerinfo.get(SHCFEShopInfoConstant.title)
                            ci.declaredate = sellerinfo.get(SHCFEShopInfoConstant.declaretime)
                            ci.fetchdatetime = datetime.datetime.now()
                            ci.lastactivedatetime = datetime.datetime.now()
                            
                            ci.price = sellerinfo.get(SHCFEShopInfoConstant.price)
                            ci.cartype = sellerinfo.get(SHCFEShopInfoConstant.cartype)
                            ci.contacter = sellerinfo.get(SHCFEShopInfoConstant.contacter)
                            ci.contacterurl = sellerinfo.get(SHCFEShopInfoConstant.contacter_url)
                            ci.contacterphonepicname = sellerinfo.get(SHCFEShopInfoConstant.contacter_phone_picture_name)
                            ci.carcolor = sellerinfo.get(SHCFEShopInfoConstant.car_color)
                            ci.roadhaul = sellerinfo.get(SHCFEShopInfoConstant.road_haul)
                            ci.displacement = sellerinfo.get(SHCFEShopInfoConstant.displacement)
                            ci.gearbox = sellerinfo.get(SHCFEShopInfoConstant.gearbox)
                            ci.licenseddate = sellerinfo.get(SHCFEShopInfoConstant.license_date)
    
                        si = fs.query(SellerInfo).filter(SellerInfo.sellerurl == sellerinfo[SHCFEShopInfoConstant.contacter_url]).first()
                        if si is not None:
                            ci.sellerid = si.seqid
                            fs.commit()
                        else:
                            ci.sellerid = gen_uuid()
                            si = SellerInfo()
                            si.seqid = ci.sellerid
                            si.selleraddress = sellerinfo.get(SHCFEShopInfoConstant.shop_address)
                            si.sellername = sellerinfo.get(SHCFEShopInfoConstant.shop_name)
                            si.sellerphone = sellerinfo.get(SHCFEShopInfoConstant.shop_phone)
                            si.sellerurl = sellerinfo.get(SHCFEShopInfoConstant.contacter_url)
                            si.enterdate = sellerinfo.get(SHCFEShopInfoConstant.enter_time)
                            si.sellertype = u'1' if self.is_customer(cookies) else u'2'
                            fs.add(si)
                            fs.commit()
                        
#                    if rs.callback.im_class == PersonPhoneSpider:
#                        
#                    elif rs.callback.im_class == CustomerShopSpider:
#                        pass
                except Exception as e:
                    self.log(u'something wrong %s' % str(e), log.CRITICAL)
                finally:
                    fs.close()
                    
                    
    return parse_simulate
