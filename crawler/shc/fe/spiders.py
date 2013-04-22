# encoding=UTF-8
'''
Created on 2013-3-31
@author: Administrator
'''
from crawler.shc.fe.const import FEConstant as const
from crawler.shc.fe.item import SHCFEShopInfo, SHCFEShopInfoConstant as voconst
from crawler.shc.fe.tools import ignore_notice, check_verification_code, \
    check_verification_code_gif, with_ip_proxy, check_blank_page, \
    check_detail_duplicate, save_detail
from scrapy import log
from scrapy.http.request import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from uuid import uuid4
import csv
import datetime
import itertools
import os

strptime = datetime.datetime.strptime
#城市名称    标题信息    信息发布时间    价格    车型名称    联系人    联系人链接地址    联系方式图片文件名    车辆颜色    行驶里程    车辆排量    变速箱    上牌时间    商户名称    
#商户地址    商户电话    入住时间    信息原始链接地址


def get_customer_fields():
    return [
          voconst.cityname,
          voconst.title,
          voconst.declaretime,
          voconst.price,
          voconst.cartype,
          voconst.contacter,
          voconst.contacter_url,
          voconst.contacter_phone_picture_name,
          voconst.car_color,
          voconst.road_haul,
          voconst.displacement,
          voconst.gearbox,
          voconst.license_date,
          voconst.shop_name,
          voconst.shop_address,
          voconst.shop_phone,
          voconst.enter_time,
          voconst.info_url,
          ]
    
def get_personal_fields():
    return [
          voconst.cityname,
          voconst.title,
          voconst.declaretime,
          voconst.price,
          voconst.cartype,
          voconst.contacter,
          voconst.contacter_url,
          voconst.contacter_phone_picture_name,
          voconst.car_color,
          voconst.road_haul,
          voconst.displacement,
          voconst.gearbox,
          voconst.license_date,
#          voconst.shop_name,
#          voconst.shop_address,
#          voconst.shop_phone,
          voconst.enter_time,
          voconst.info_url,
          ]

customer_fields = get_customer_fields()
personal_fields = get_personal_fields()

def get_customer_headers():
    return {
           voconst.cityname:u'城市名称',
           voconst.title:u'标题信息',
           voconst.declaretime:u'信息发布时间',
           voconst.price:u'价格',
           voconst.cartype:u'车型名称',
           voconst.contacter:u'联系人',
           voconst.contacter_url:u'联系人链接地址',
           voconst.contacter_phone_picture_name:u'联系方式图片文件名',
           voconst.car_color:u'车辆颜色',
           voconst.road_haul:u'行驶里程',
           voconst.displacement:u'车辆排量',
           voconst.gearbox:u'变速箱',
           voconst.license_date:u'上牌时间',
           voconst.shop_name:u'商户名称',
           voconst.shop_phone:u'商户电话',
           voconst.shop_address:u'商户地址',
           voconst.enter_time:u'入驻时间',
           voconst.info_url:u'信息原始链接地址',
           }
    
def get_personal_headers():
    return {
           voconst.cityname:u'城市名称',
           voconst.title:u'标题信息',
           voconst.declaretime:u'信息发布时间',
           voconst.price:u'价格',
           voconst.cartype:u'车型名称',
           voconst.contacter:u'联系人',
           voconst.contacter_url:u'联系人链接地址',
           voconst.contacter_phone_picture_name:u'联系方式图片文件名',
           voconst.car_color:u'车辆颜色',
           voconst.road_haul:u'行驶里程',
           voconst.displacement:u'车辆排量',
           voconst.gearbox:u'变速箱',
           voconst.license_date:u'上牌时间',
#           voconst.shop_name:u'商户名称',
#           voconst.shop_phone:u'商户电话',
#           voconst.shop_address:u'商户地址',
           voconst.enter_time:u'注册时间',
           voconst.info_url:u'信息原始链接地址',
           }


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
        
        enddate = strptime(self.settings.get(const.ENDDATE), u'%Y-%m-%d').date()
        startdate = strptime(self.settings.get(const.STARTDATE), u'%Y-%m-%d').date()

        ipproxies = self.settings[const.CONFIG_DATA].get(const.PROXY_CONFIG)\
            .get(const.PROXY_CONFIG_IPPROXIES)
            
        ipproxy_generator = itertools.cycle(ipproxies.split(u','))
        
        custom_flag = self.settings[const.CUSTOMER_FLAG]
#        assert custom_flag==u'1' ,u' call corleone to extend the person type'
        
        cookies = {
                    const.CUSTOMER_FLAG:custom_flag
                   , const.OUTPUT_DIR:self.settings[const.OUTPUT_DIR]
                   , const.START_TIME:self.settings[const.START_TIME]
                   , const.STARTDATE:startdate
                   , const.ENDDATE:enddate
                   , const.START_PAGE:self.settings.get(const.START_PAGE)
                   , const.END_PAGE:self.settings.get(const.END_PAGE)
                   , const.CONFIG_DATA:self.settings.get(const.CONFIG_DATA)
                   , const.LOCK:self.settings.get(const.LOCK)
                   , const.PROXY_CONFIG_PROXY_GENERATOR:ipproxy_generator
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
    
    def in_time_period(self, dt, cookies):
        start_date = cookies[const.STARTDATE]
        end_date = cookies[const.ENDDATE]
#        return start_date <= dt <= end_date
        return 1
    
    def build_file_dir(self, cookies):
        file_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies)])
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        return file_dir
    
    def build_ignore_file_dir(self, cookies):
        ignore_file_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies), u"Ignore"])
        if not os.path.exists(ignore_file_dir):
            os.makedirs(ignore_file_dir)
        return ignore_file_dir
    
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
        
    def build_list_file_dir(self, cookies):
        list_file_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies), u"List"])
        if not os.path.exists(list_file_dir):
            os.makedirs(list_file_dir)
        return list_file_dir
        
    def build_deprecate_file_dir(self, cookies):
        deprecate_file_dir = os.sep.join([cookies[const.OUTPUT_DIR],
                            self.build_file_name(cookies), u"Deprecate"])
        if not os.path.exists(deprecate_file_dir):
            os.makedirs(deprecate_file_dir)
        return deprecate_file_dir
        
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

    def build_file_name(self, cookies):
        if self.is_customer(cookies):
            return 'total%scustomer' % cookies[const.START_TIME]
        else:
            return 'total%spersonal' % cookies[const.START_TIME] 
    
    def build_file_path(self, cookies):
        return os.sep.join([self.build_file_dir(cookies)
                           , self.build_file_name(cookies) + u'.csv'])
    
    def write_header(self, cookies):
        file_path = self.build_file_path(cookies)
        if not os.path.exists(file_path):
            lock = cookies[const.LOCK]
            with lock:
                with open(file_path, u'w') as f:
                    if self.is_customer(cookies):
                        dw = csv.DictWriter(f, customer_fields)
                        dw.writerow(get_customer_headers())
                    else :
                        dw = csv.DictWriter(f, personal_fields)
                        dw.writerow(get_personal_headers())
                    self.log(u'create file succeed %s' % file_path, log.INFO)
    
    def write_data(self, cookies, info):
        lock = cookies[const.LOCK]
        if self.is_customer(cookies):
            with lock:
                file_path = self.build_file_path(cookies)
                with open(file_path, u'a') as f:
                    dw = csv.DictWriter(f, customer_fields)
                    dw.writerow(info)
        else:
            with lock:
                file_path = self.build_file_path(cookies)
                with open(file_path, u'a') as f:
                    dw = csv.DictWriter(f, personal_fields)
                    dw.writerow(info)
            
    
    def is_customer(self, cookies):
        return unicode(cookies[const.CUSTOMER_FLAG]) == u"1"

    def is_develop_debug(self, cookies):
        return unicode(cookies[const.CONFIG_DATA][const.DEVELOP_CONFIG][const.DEVELOP_CONFIG_DEBUG]) == u"1"

class SHCSpider(FESpider):
    
    name = u'SHCSpider'
    
    def start_requests(self):
        cookies = self.build_cookies()
        req = Request('http://www.58.com/ershouche/changecity/'
                      , self.parse, cookies=cookies)
        
        msg = (u'prepared to crawl %s %s,%s - %s , page %s - %s'
               '') % (
                      self.get_current_city(cookies),
                      'Customer ' if self.is_customer(cookies) else u"Person",
                      cookies[const.STARTDATE].strftime('%Y-%m-%d'),
                      cookies[const.ENDDATE].strftime('%Y-%m-%d'),
                      cookies[const.START_PAGE],
                      cookies[const.END_PAGE],
                     )
        
        self.write_header(cookies)
        
        self.log(msg, log.INFO)
        
        yield req
    
    @check_blank_page
    def parse(self, response):
        cookies = response.request.cookies
        city_name = self.get_current_city(cookies)
        hxs = HtmlXPathSelector(response)
        a_tags = hxs.select('//div[@class="index_bo"]/dl//a')
        
        for a_tag in a_tags:
            city = a_tag.select('text()').extract()[0]
            city_url = a_tag.select('@href').extract()[0]
            if unicode(city.strip()) == unicode(city_name.strip()):
                customer = 1 if self.is_customer(cookies) else 0
                tmp_url = u'%s/?selpic=1' % customer
                yield Request(city_url + tmp_url, CarListSpider().parse,
                              dont_filter=True,
                              cookies=cookies
                              )
                break
        else:
            msg = u" not find city %s" % city_name
            self.log(msg.rjust(30, u"="), log.CRITICAL)
        
class CarListSpider(FESpider):
    
    DOWNLOAD_DELAY = 20
    
#    @check_blank_page
#    @with_ip_proxy
#    @check_verification_code
#    @ignore_notice

    @check_detail_duplicate
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
        
        
        if self.is_develop_debug(cookies):
            file_name = current_city + unicode(current_page_no) + u'.html'
            self.save_body(self.build_list_file_dir(cookies), file_name , response)
        
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
            #===================================================================
            # declare_date = None
            # try:
            #    declare_date = tr_tag.select('//span[@class="c_999"]/text()').extract()[0]
            # except IndexError:
            #    pass
            # url_title = tr_tag.select('td[1]/a/text()').extract()[0]
            # if declare_date:
            #    declare_date_str = u'%s-%s' % (cookies[const.START_TIME][:4]
            #                                   , declare_date)
            #    try:
            #        declare_date = strptime(declare_date_str, '%Y-%m-%d').date()
            #        
            #        if not self.in_time_period(declare_date, cookies):
            #            msg = (u"ignore for out of time %s,%s,%s in "
            #                   "%s ") % (current_city, declare_date_str
            #                             , url, response.url)
            #            self.log(msg, log.INFO)
            #            continue 
            #    except ValueError:
            #        #===========================================================
            #        # not standar datetime format
            #        #===========================================================
            #        self.log(u'%s ' % declare_date_str, log.DEBUG)
            #===================================================================
            
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
                msg = (u'add next page No.%s into schedule '
                                    '%s') % (page_no, current_city)
                self.log(msg, log.INFO)
                yield Request(current_domain + next_url,
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
    
    DOWNLOAD_DELAY = 5
    
#    @check_blank_page
#    @with_ip_proxy
#    @check_verification_code
#    @ignore_notice

    @save_detail
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
        
        continue_flag = 1
        
        try:
            declaretime = hxs.select('//li[@class="time"]/text()').extract()[0]
            info[voconst.declaretime] = declaretime
            
        except Exception as e:
            self.log((u" something wrong %s " % (response.url,)), log.CRITICAL)
            raise e
        
        if not self.in_time_period(strptime(declaretime, '%Y.%m.%d').date()
                                   , cookies):
            continue_flag = 0

            if self.is_develop_debug(cookies):
                file_name = self.get_random_id() + u'.html'
                self.save_body(self.build_deprecate_file_dir(cookies),
                           file_name, response)
                msg = u'not in time period %s , %s ' % (declaretime, file_name)
            else:
                msg = u'not in time period %s ' % (declaretime)
            
        else:
            xps = '//span[@id="t_phone"]/script/text()'
            phone_picture_url = hxs.select(xps).extract()
            if not phone_picture_url:
                continue_flag = 0
                if self.is_develop_debug(cookies):
                    file_name = self.get_random_id() + u'.html'
                    self.save_body(self.build_contacter_miss_file_dir(cookies),
                               file_name, response)
                    msg = u'contacter\'s phone picture is miss %s ' % file_name
                else:
                    msg = u'contacter\'s phone picture is miss '
                    
                
        if continue_flag:
            try:
                phone_picture_url = phone_picture_url[0]
                phone_picture_url = phone_picture_url.split('\'')[1]
                
                xps = '//div[@class="col_sub mainTitle"]/h1/text()'
                title = hxs.select(xps).extract()[0]
                info[voconst.title] = title
                        
            except Exception as e:
                self.log((u"something wrong %s " % (response.url,)),
                                    log.CRITICAL)
                raise e
            
            xps = '//div[@class="col_sub sumary"]/ul[@class="suUl"]/li'
            li_tags = hxs.select(xps)
            for idx, li_tag in enumerate(li_tags):
                try:
                    blank = li_tag.select('child::*')
                    if blank:
                        div_val = li_tag.select('div[1]/text()').extract()
                        div_val = div_val[0].strip()
                except IndexError as ie:
                    self.log((u" something wrong %s , index %s"
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
                info[voconst.contacter_phone_picture_name] = picture_name + u".jpg"
                
                cookies[const.sellerinfo] = info
            except Exception as e:
                self.log((u" something wrong %s " % (response.url,)),
                                log.CRITICAL)
                raise e
            
            contacter_url = info.get(voconst.contacter_url)
            
            if self.is_develop_debug(cookies):
                self.save_body(self.build_detail_file_dir(cookies),
                               picture_name + u'.html', response)
            
            if contacter_url is None :
                self.log((u'with no contacter info %s , %s , '
                          '%s') % (self.get_current_city(cookies),
                                   response.request.url,
                                   phone_picture_url), log.INFO)
                
                yield Request(phone_picture_url,
                              PersonPhoneSpider().parse,
                              cookies=cookies,
                              dont_filter=True)
            else:
                cookies[voconst.contacter_phone_url] = phone_picture_url
                self.log((u'with contacter info %s ,%s,'
                          '%s') % (self.get_current_city(cookies),
                                   response.request.url,
                                   contacter_url), log.INFO)
                
#                contacter_url = u'http://my.58.com/13463298588423/'
                yield Request(contacter_url,
                              CustomerShopSpider().parse,
                              cookies=cookies,
                              dont_filter=True)
            
        else:
            self.log((u"ignore in detail page %s %s %s") 
                     % (self.get_current_city(cookies), msg, response.url),
                     log.INFO)
        
        
class PersonPhoneSpider(FESpider):

#    DOWNLOAD_DELAY = 0.3
    
    @check_blank_page
    @with_ip_proxy
    @check_verification_code_gif
    def parse(self, response):
        cookies = response.request.cookies
        info = cookies[const.sellerinfo]
        
        filename = info[voconst.contacter_phone_picture_name]
        
        pic_path = os.sep.join([self.build_pic_dir(cookies), filename]) 
        
        with open(pic_path , 'wb') as f:
            f.write(response.body)
        
#        info[voconst.contacter_phone_picture_name] = filename
        
        self.write_data(cookies, info)
        
        self.log(u"fetch 1 %s , %s" % (info[voconst.cityname],
                                       info[voconst.info_url]), log.INFO)
        
        
class CustomerShopSpider(FESpider):
    
    @check_blank_page
    @with_ip_proxy
    @check_verification_code
    def parse(self, response):
        
        hxs = HtmlXPathSelector(response)
        
        cookies = response.request.cookies
        
        
        if self.is_develop_debug(cookies):
            custom_url = self.get_random_id() + u'.html'
            self.save_body(self.build_custom_file_dir(cookies),
                           custom_url + u'.html', response)
            self.log(u"custom %s in custom folder %s " % (response.url,
                                                          custom_url,),
                     log.DEBUG)
        
        info = dict(cookies[const.sellerinfo])
        
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
                    info[voconst.enter_time] = enter_time.replace('-', '.')
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

        cookies[const.sellerinfo] = info
        yield Request(response.request.cookies[voconst.contacter_phone_url],
                      PersonPhoneSpider().parse,
                      dont_filter=True,
                      cookies=cookies)
        
        response.request
