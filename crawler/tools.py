# encoding=UTF-8
'''
Created on 2013-4-22
@author: Administrator
'''
from uuid import uuid4

gen_uuid = lambda :unicode(uuid4()).replace('-', u'')