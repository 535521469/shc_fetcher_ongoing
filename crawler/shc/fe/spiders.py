# encoding=UTF-8
'''
Created on 2013-3-31
@author: Administrator
'''
from crawler.shc.fe.const import FEConstant as const
from crawler.shc.fe.item import SHCFEShopInfo, SHCFEShopInfoConstant as voconst
from crawler.shc.fe.tools import detail_page_parse_4_save_2_db, \
    list_page_parse_4_remove_duplicate_detail_page_request, \
    seller_page_parse_4_save_2_db
from scrapy import log
from scrapy.http.request import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from uuid import uuid4
import datetime
import os

strptime = datetime.datetime.strptime
#城市名称    标题信息    信息发布时间    价格    车型名称    联系人    联系人链接地址    联系方式图片文件名    车辆颜色    行驶里程    车辆排量    变速箱    上牌时间    商户名称    
#商户地址    商户电话    入住时间    信息原始链接地址

class FESpider(BaseSpider):
    
    name = 'FESpider'
    home_url = r'http://www.58.com'
    second_hand_car = '/ershouche'
    
    def start_requests(self):
        yield self.make_requests_from_url('http://www.58.com/ershouche/changecity/')
    
    def get_page_no_from_url(self, url):
        return url[url.index('/pn') + 3:url.index('?') - 1]
    
    def get_current_city(self, cookies):
        return cookies[const.CONFIG_DATA][const.CURRENT_CITY]
    
    def build_cookies(self):
        
        cookies = {
                    const.OUTPUT_DIR:self.settings[const.OUTPUT_DIR],
                    const.END_PAGE:self.settings.get(const.END_PAGE),
                    const.START_PAGE:self.settings.get(const.START_PAGE),
                    const.CONFIG_DATA:self.settings.get(const.CONFIG_DATA),
                   }
        return cookies
    
    def get_next_proxy(self, cookies):
        return cookies[const.PROXY_CONFIG_PROXY_GENERATOR].next()
    
    def get_ipproxy_enable(self, cookies):
        proxyconfig = cookies[const.CONFIG_DATA][const.PROXY_CONFIG]
        return u'1' == proxyconfig[const.PROXY_CONFIG_ENABLE]
    
    def get_random_id(self):
        return unicode(uuid4())
    
    def save_body(self, file_dir, file_name, response):
        file_path = os.sep.join([file_dir, file_name])
        with open(file_path , u'w') as f:
            f.write(response.body)
    
    def build_shield_file_dir(self, cookies):
        shield_file_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies), u"Shield"])
        if not os.path.exists(shield_file_dir):
            os.makedirs(shield_file_dir)
        return shield_file_dir
    
    def build_blank_file_dir(self, cookies):
        blank_file_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies), u"Blank"])
        if not os.path.exists(blank_file_dir):
            os.makedirs(blank_file_dir)
        return blank_file_dir
    
    def build_detail_file_dir(self, cookies):
        detail_file_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies), u"Detail"])
        if not os.path.exists(detail_file_dir):
            os.makedirs(detail_file_dir)
        return detail_file_dir
        
    def build_custom_file_dir(self, cookies):
        custom_file_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies), u"Custom"])
        if not os.path.exists(custom_file_dir):
            os.makedirs(custom_file_dir)
        return custom_file_dir
        
    def build_contacter_miss_file_dir(self, cookies):
        contacter_miss_file_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies), u"ContacterMiss"])
        if not os.path.exists(contacter_miss_file_dir):
            os.makedirs(contacter_miss_file_dir)
        return contacter_miss_file_dir
        
    def build_pic_dir(self, cookies):
        pic_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies) + u'PIC'])
        
        if not os.path.exists(pic_dir):
            os.makedirs(pic_dir)
        
        return pic_dir
    
    def build_public_pic_dir(self, cookies):
        city = self.get_current_city(cookies)
        pic_dir = os.sep.join([cookies[const.OUTPUT_DIR], u'%sPIC' % city])
        if not os.path.exists(pic_dir):
            os.makedirs(pic_dir)
    
class SHCSpider(FESpider):
    
    
    name = u'SHCSpider'
    
    def start_requests(self):
        cookies = self.build_cookies()
        req = Request('http://www.58.com/ershouche/changecity/'
                      , self.parse, cookies=cookies)
        
        msg = (u'prepared to crawl %s , page %s - %s'
               '') % (self.get_current_city(cookies),
                      cookies[const.START_PAGE],
                      cookies[const.END_PAGE],
                     )
        
        self.log(msg, log.INFO)
        
        yield req
    
    def parse(self, response):
        cookies = response.request.cookies
        city_name = self.get_current_city(cookies)
        hxs = HtmlXPathSelector(response)
        a_tags = hxs.select('//div[@class="index_bo"]/dl//a')
        
        for a_tag in a_tags:
            city = a_tag.select('text()').extract()[0]
            city_url = a_tag.select('@href').extract()[0]
            if unicode(city.strip()) == unicode(city_name.strip()):
                url = u'%s?selpic=1' % city_url
                yield Request(url, CarListSpider().parse,
                              dont_filter=True,
                              cookies=cookies
                              )
                break
        else:
            msg = u" not find city %s" % city_name
            self.log(msg.rjust(30, u"="), log.CRITICAL)
        
class CarListSpider(FESpider):
    
    
    @list_page_parse_4_remove_duplicate_detail_page_request
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        cookies = dict(response.request.cookies)
        current_city = self.get_current_city(cookies)
        
        start_page = cookies[const.START_PAGE]
        end_page = cookies[const.END_PAGE]
        
        current_url = response.url
        current_page_no = 1
        try:
            current_page_no = int(self.get_page_no_from_url(current_url))
        except ValueError:
            pass
        
        
        #=======================================================================
        # whether if out of page number config
        #=======================================================================
        if start_page <= current_page_no <= end_page:
            tr_tags = hxs.select('//table[@class="tbimg list_text_pa"]//tr')
        else:
            msg = (u"page No.%s out of page scope , ignore analyse"
                   " contents , %s , %s") % (current_page_no,
                                             current_city,
                                             response.url,
                                             )
            self.log(msg, log.INFO)
            tr_tags = []
        
        url_len = 0
        
        for tr_tag in tr_tags:
            
            td_tags = tr_tag.select('td').extract()
            if len(td_tags) == 1:
                continue
            
            url = tr_tag.select('td[1]/a/@href').extract()[0]
            
            url_len = url_len + 1
            self.log((u'add detail page in list page %s '
                      '%s ') % (self.get_current_city(cookies), url), log.DEBUG)
            
            yield Request(url, CarDetailSpider().parse,
                          dont_filter=True,
                          cookies=cookies,
                          )
        else:
            self.log((u'%s list page No %s , total add detail page '
                      '%s') % (self.get_current_city(cookies),
                               current_page_no,
                               url_len), log.INFO)

        #=======================================================================
        # catch next page
        #=======================================================================
        
        current_domain = current_url[:current_url.find(u'/ershouche')]
        try:
            next_url = hxs.select('//a[@class="next"]/@href').extract()[0]
            page_no = self.get_page_no_from_url(next_url)
            
            if int(page_no) <= end_page:
                next_page_url = current_domain + next_url
                msg = (u'add next page No.%s into schedule '
                                    '%s %s') % (page_no, current_city, next_page_url)
                self.log(msg, log.INFO)
                yield Request(next_page_url,
                              CarListSpider().parse,
                              dont_filter=True,
                              cookies=cookies)
            else:
                msg = (u'reach the largest page of config , '
                                    'stop crawl %s , %s ') % (current_city, response.url) 
                self.log(msg, log.INFO)
                
        except IndexError:
            msg = (u"reach last page , need not to crawl"
                    " anymore , %s , %s ") % (current_city, current_url)
            self.log(msg, log.INFO)
                
class CarDetailSpider(FESpider):
    
    
    name = u'CarDetailSpider'
    
    @detail_page_parse_4_save_2_db
    def parse(self, response):
        '''
        parse 
        '''
        info = SHCFEShopInfo()
        cookies = dict(response.request.cookies)
        cookies[const.sellerinfo] = info
        
        hxs = HtmlXPathSelector(response)
        xps = '//div[@class="breadCrumb f12"]/span/a[1]/text()'
        city_ = hxs.select(xps).extract()[0]
        city_name = city_[:city_.find(u'58')]
        info[voconst.cityname] = city_name
        
        try:
            custom_flag = hxs.select('//em[@class="shenfen"]/text()').extract()[0].strip().replace(u"）", u'').replace(u"（", u'')
            info[voconst.custom_flag] = u'1' if custom_flag.find(u'\u5546\u5bb6') != -1 else u'2'
        except Exception as e:
#            info[voconst.custom_flag] = u'1' if self.is_customer(cookies) else u'2'
            info[voconst.custom_flag] = u'0'
        
        try:
            declaretime = hxs.select('//li[@class="time"]/text()').extract()[0]
            info[voconst.declaretime] = declaretime
            
        except Exception as e:
            self.log((u"something wrong %s " % (response.url,)), log.CRITICAL)
            raise e
        
        xps = '//span[@id="t_phone"]/script/text()'
        phone_picture_url = hxs.select(xps).extract()
                    
        try:
            phone_picture_url = phone_picture_url[0]
            phone_picture_url = phone_picture_url.split('\'')[1]
            
            xps = '//div[@class="col_sub mainTitle"]/h1/text()'
            title = hxs.select(xps).extract()[0]
            info[voconst.title] = title
                    
        except Exception as e:
            self.log((u"info deprecated %s " % (response.url,)),
                     log.INFO)
            phone_picture_url = None
        
        xps = '//div[@class="col_sub sumary"]/ul[@class="suUl"]/li'
        li_tags = hxs.select(xps)
        for idx, li_tag in enumerate(li_tags):
            try:
                blank = li_tag.select('child::*')
                if blank:
                    div_val = li_tag.select('div[1]/text()').extract()
                    div_val = div_val[0].strip()
            except IndexError as ie:
                self.log((u"something wrong %s , index %s"
                         " of %s" % (response.url, idx, xps)), log.CRITICAL)
                raise ie
            
            title_div_tag_val = div_val.replace(u'：', u'')
            if title_div_tag_val == u'价    格':
                price_num = li_tag.select('div[2]/span/text()').extract()[0]
                price_unit = li_tag.select('div[2]/text()').extract()[0]
                info[voconst.price] = price_num + price_unit
            elif title_div_tag_val == u'联 系 人':
                try:
                    contacter = li_tag.select('div[2]/a/text()').extract()[0]
                    contacter_url = li_tag.select('div[2]/a/@href').extract()[0]
                except IndexError:
                    contacter = li_tag.select('div[2]/span/a/text()').extract()[0]
                    contacter_url = li_tag.select('div[2]/span/a/@href').extract()[0]
                info[voconst.contacter] = contacter.strip()
                info[voconst.contacter_url] = contacter_url
                
            elif title_div_tag_val in (u"品牌车系", u"车型名称"):
                xps = u'descendant-or-self::text()'
                a_vals = li_tag.select('div[2]').select(xps).extract()
                cartype = u''.join(a_vals).strip().replace(u'\n', u'')
                info[voconst.cartype] = cartype
            
        li_tags = hxs.select('//ul[@class="ulDec clearfix"]/li')
        
        for label_tag in li_tags:
            xps = 'span[@class="it_l fb"]/text()'
            label = label_tag.select(xps).extract()[0].strip().replace(' ', '')
            label = label.replace(u'\xa0', u'')
            if label == u'车辆颜色':
                car_color = label_tag.select('span[2]/text()').extract()[0]
                info[voconst.car_color] = car_color
            elif label == u'\u53d8\u901f\u7bb1': # 变  速  箱
                gearbox = label_tag.select('span[2]/text()').extract()[0]
                info[voconst.gearbox] = gearbox
            elif label == u'上牌时间':
                license_date = label_tag.select('span[2]/text()').extract()[0]
                info[voconst.license_date] = license_date
            elif label == u'车辆排量':
                displacement = label_tag.select('span[2]/text()').extract()[0]
                info[voconst.displacement] = displacement
            elif label == u'行驶里程':
                road_haul = label_tag.select('span[2]/text()').extract()[0]
                info[voconst.road_haul] = road_haul
        
        try:
            info_url = response.url
            info[voconst.info_url] = info_url 
            picture_name = info_url.split(u'/')[-1]
            picture_name = picture_name[:picture_name.index(u'.')]
            info[voconst.contacter_phone_picture_name] = picture_name + u".gif"
            
            cookies[const.sellerinfo] = info
        except Exception as e:
            self.log((u"something wrong %s " % (response.url,)),
                            log.CRITICAL)
            raise e
        contacter_url = info.get(voconst.contacter_url)
        info[voconst.contacter_phone_url] = phone_picture_url
        
        yield info
        
        
class PersonPhoneSpider(FESpider):

    
    def parse(self, response):
        
        def build_public_pic_dir():
            pic_dir = os.sep.join([os.getcwd(), u"58_PIC"])
            if not os.path.exists(pic_dir):
                os.makedirs(pic_dir)
            return pic_dir
            
        cookies = response.request.cookies
        
        pic_path = os.sep.join([build_public_pic_dir(), cookies[voconst.contacter_phone_picture_name]])
        
        with open(pic_path , 'wb') as f:
            f.write(response.body)
        
class CustomerShopSpider(FESpider):

    @seller_page_parse_4_save_2_db
    def parse(self, response):
        
        hxs = HtmlXPathSelector(response)
        
        cookies = response.request.cookies
        
        info = dict(cookies)
        
        try:
            shop_name = hxs.select('//div[@class="bi_tit"]/text()').extract()[0]
            info[voconst.shop_name] = shop_name.strip()
        except Exception:
            pass
        
        try:
            xps = '//div[@class="title_top"]/ul[1]/li[2]/text()'
            shop_address = hxs.select(xps).extract()[0]
            info[voconst.shop_address] = shop_address[3:].strip()
        except Exception :
            pass
        
        try:
            xps = '//dl[@class="ri_info_dl_01"]/dd'
            for dd_tag in hxs.select(xps):
                if dd_tag.select('text()').extract()[0] == u'联系电话：':
                    xps = "parent::dl/dt/text()"
                    shop_phone = dd_tag.select(xps).extract()[0]
                    info[voconst.shop_phone] = shop_phone.strip()
                elif dd_tag.select('text()').extract()[0] == u'入驻时间：':
                    xps = "parent::dl/dt/text()"
                    enter_time = dd_tag.select(xps).extract()[0].strip()
                    info[voconst.enter_time] = enter_time.strip()
        except Exception:
            pass

        if info.get(voconst.enter_time) is None:
            #===================================================================
            # individual
            #===================================================================
            xps = '//div[@class="xqxinfo"]//tr'
            for tr_tag in hxs.select(xps):
                td_val = tr_tag.select('th[1]/text()').extract()[0]
                if td_val == u'\u6ce8\u518c\u65f6\u95f4': # u'注册时间'
                    info[voconst.enter_time] = tr_tag.select('td[1]/text()').extract()[0].strip()
                    break
                
        yield info
        
