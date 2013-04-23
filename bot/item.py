# encoding=UTF-8
'''
Created on 2013-4-22
@author: Administrator
'''
from crawler.tools import gen_uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Date

Base = declarative_base()
class CarInfo(Base):
    
    __tablename__ = 'CarInfo'
  
    seqid = Column("SEQID", String, primary_key=True, default=gen_uuid)
    cityname = Column("CityName", String,)
    sourcetype = Column("SourceType", String,)
    statustype = Column("StatusType", String,)
    title = Column("Title", String,)
    declaredate = Column("DeclareDate", Date,)
    fetchdatetime = Column("FetchDateTime", DateTime,)
    lastactiveDateTime = Column("LastActiveDateTime", DateTime,)
    offlinedatetime = Column("OffLineDateTime", DateTime,)
    sourceurl = Column("SourceURL", String,)
    popularizeurl = Column("PopularizeURL", String,)
    sellerid = Column("SellerID", String,)
    price = Column("Price", String,)
    cartype = Column("CarType", String,)
    contacter = Column("Contacter", String,)
    contacterurl = Column("ContacterURL", String,)
    contacterphonepicname = Column("ContacterPhonePicName", String,)
    contacterphonepicmd5 = Column("ContacterPhonePicMD5", String,)
    contacterphone = Column("ContacterPhone", String,)
    carcolor = Column("CarColor", String,)
    roadhaul = Column("RoadHaul", String,)
    displacement = Column("Displacement", String,)
    gearbox = Column("Gearbox", String,)
    licenseddate = Column("LicenseDate", Date,)
    carsourcetype = Column("CarSourceType", String,)
    contacterphonepicurl= Column("ContacterPhonePicURL", String,)

class SellerInfo(Base):
    
    __tablename__ = 'SellerInfo'
  
    seqid = Column("SEQID", String, primary_key=True, default=gen_uuid)
    sellername = Column("SellerName", String,)
    selleraddress = Column("SellerAddress", String,)
    sellerphone = Column("SellerPhone", String,)
    enterdate = Column("EnterDate", Date,)
    sellerurl = Column("SellerUrl", Date,)

