# encoding=utf8
'''
Created on 2013-3-31
@author: Administrator
'''
from scrapy.item import Field


#城市名称    标题信息    信息发布时间    价格    车型名称    联系人    联系人链接地址    联系方式图片文件名    
#车辆颜色    行驶里程    车辆排量    变速箱    上牌时间    商户名称    商户地址    商户电话    入住时间    信息原始链接地址



class SHCFEShopInfoConstant(object):
    
    cityname = u'cityname'
    title = u"title"
    declaretime = u"declaretime"
    price = u"price"
    cartype = u"cartype"
    contacter = u"contacter"
    contacter_url = u"contacter_url"
    contacter_phone_url = u"phone_url"
    contacter_phone_picture_name = u"picture_name"
    
    car_color = u"car_color"
    road_haul = u"road_haul" # 行驶里程
    displacement = u"displacement" # 排量
    gearbox = u"gearbox" # 变速箱
    license_date = u"license_date" # 上牌时间
    shop_name = u"shop_name"
    shop_address = u"shop_address"
    shop_phone = u"shop_phone"
    enter_time = u"enter_time"
    info_url = u"info_url"
    
    sellerid = u'sellerid'
    carid = u'carid'

    custom_flag = u'customflag'
    
class SHCFEShopInfo(dict):
    '''商户信息
    '''
    cityname = Field()
    title = Field()
    declaretime = Field()
    price = Field()
    cartype = Field()
    contacter = Field()
    contacter_url = Field()
    contacter_phone_picture = Field()
    
    car_color = Field()
    
    road_haul = Field() # 行驶里程
    displacement = Field() # 排量
    gearbox = Field() # 变速箱
    
    license_date = Field() # 上牌时间
    
    shop_name = Field()
    shop_address = Field()
    
    shop_phone = Field()
    
    enter_time = Field()
    
    info_url = Field()
    
    customflag = Field()
    carid = Field()
    sellerid = Field()

    
#class SHCFEShopInfo(UserDict):
#    '''商户信息
#    '''
#    _cityname = Field()
#    _title = Field()
#    _declaretime = Field()
#    _price = Field()
#    _cartype = Field()
#    _contacter = Field()
#    _contacter_url = Field()
#    _contacter_phone_picture = Field()
#    
#    _car_color = Field()
#    
#    _road_haul = Field() # 行驶里程
#    _displacement = Field() # 排量
#    _gearbox = Field() # 变速箱
#    
#    _license_date = Field() # 上牌时间
#    
#    _shop_name = Field()
#    _shop_address = Field()
#    
#    _shop_phone = Field()
#    
#    _enter_time = Field()
#    
#    _info_url = Field()

    

    
    
