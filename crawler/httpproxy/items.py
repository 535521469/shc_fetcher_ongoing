# encoding=utf8
'''
Created on 2013-4-10
@author: corleone
'''
from scrapy.item import Item, Field

class IPProxyItem(Item):
    
    ip = Field()
    port = Field()
    country = Field()
    

    