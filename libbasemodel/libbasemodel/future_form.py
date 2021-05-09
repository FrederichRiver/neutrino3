#!/usr/bin/python38
from sqlalchemy import Column, String, Integer, Float, Date, Time, DateTime
from sqlalchemy.ext.declarative import declarative_base

futureformTemplate = declarative_base()


class future(futureformTemplate):
    __tablename__ = 'future_data'
    date_time = Column(DateTime, primary_key=True)
    price = Column(Float)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    prev_price = Column(Float)
    buy = Column(Integer(4))
    sell = Column(Integer(4))
    volume = Column(Integer(12))
    open_interest = Column(Float)