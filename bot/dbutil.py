# encoding=UTF-8
'''
Created on 2013-4-22
@author: Administrator
'''
from bot.config import configdata
from const import FetchConst
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

dbconfig = configdata[FetchConst.DBConfig]
# mysql://root:@localhost:3306/test
db_connect_str = u'mysql+mysqldb://%s:%s@%s:%s/%s?charset=%s' % (dbconfig[FetchConst.DBConfig_user],
                                                            dbconfig[FetchConst.DBConfig_passwd],
                                                            dbconfig[FetchConst.DBConfig_host],
                                                            dbconfig[FetchConst.DBConfig_port],
                                                            dbconfig[FetchConst.DBConfig_dbname],
                                                            dbconfig[FetchConst.DBConfig_charactset],
                                                            )
engine = create_engine(db_connect_str, echo=False)
FetchSession = sessionmaker(bind=engine)
