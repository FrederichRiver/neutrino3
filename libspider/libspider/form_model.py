#!/usr/bin/python38
from sqlalchemy import Column, String, Integer, Float, Date  # BLOB
from sqlalchemy.ext.declarative import declarative_base
# from libbasemodel.form import formStockManager
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class formStockManager(Base):
    __tablename__ = 'stock_manager'
    stock_code = Column(String(10), primary_key=True)
    stock_name = Column(String(20))
    orgId = Column(String(25))
    short_code = Column(String(10))
    create_date = Column(Date)
    update_date = Column(Date)
    xrdr_date = Column(Date)
    balance_date = Column(Date)
    income_date = Column(Date)
    cashflow_date = Column(Date)
    flag = Column(String(10))

    def __str__(self):
        return "<Stock Manager>"


class form_cpi(Base):
    __tablename__ = 'cpi'
    report_date = Column(Date, primary_key=True)
    current_month_nation = Column(Float)
    cumulate_nation = Column(Float)
    current_month_city = Column(Float)
    cumulate_city = Column(Float)
    current_month_country = Column(Float)
    cumulate_country = Column(Float)


class form_ppi(Base):
    __tablename__ = 'ppi'
    report_date = Column(Date, primary_key=True)
    current_month = Column(Float)
    cumulate = Column(Float)


class form_pmi(Base):
    __tablename__ = 'pmi'
    report_date = Column(Date, primary_key=True)
    manufacture = Column(Float)
    non_manufacture = Column(Float)


class form_gdp(Base):
    __tablename__ = 'gdp'
    report_date = Column(Date, primary_key=True)
    total_gdp = Column(Float)
    agricuture = Column(Float)
    industry = Column(Float)
    service = Column(Float)


class form_money_supply(Base):
    __tablename__ = 'money_supply'
    report_date = Column(Date, primary_key=True)
    m0 = Column(Float)
    m1 = Column(Float)
    m2 = Column(Float)


class form_researcher(Base):
    __tablename__ = 'researcher'
    idx = Column(String, primary_key=True)
    name = Column(String)


class form_institution(Base):
    __tablename__ = 'investment_institution'
    org_code = Column(String, primary_key=True)
    org_name = Column(String)
    short_name = Column(String)


class form_macro_report(Base):
    __tablename__ = 'macro_report'
    idx = Column(String)
    title = Column(String)
    author_1 = Column(String, ForeignKey("researcher.idx"))
    author_2 = Column(String, ForeignKey("researcher.idx"))
    institution = Column(String, ForeignKey("investment_institution.org_code"))
    page_url = Column(String)
    pdf_url = Column(String, primary_key=True)
    publish_date = Column(Date)
    file_type = Column(String)
    flag = Column(String)
    au_id_1 = relationship("form_researcher", foreign_keys=author_1)
    au_id_2 = relationship("form_researcher", foreign_keys=author_2)
    org_id = relationship("form_institution")


class form_industry_report(Base):
    __tablename__ = 'industry_report'
    idx = Column(String)
    title = Column(String)
    author_1 = Column(String, ForeignKey("researcher.idx"))
    author_2 = Column(String, ForeignKey("researcher.idx"))
    indu_code = Column(String)
    institution = Column(String, ForeignKey("investment_institution.org_code"))
    page_url = Column(String)
    pdf_url = Column(String, primary_key=True)
    publish_date = Column(Date)
    file_type = Column(String)
    flag = Column(String)
    au_id_1 = relationship("form_researcher", foreign_keys=author_1)
    au_id_2 = relationship("form_researcher", foreign_keys=author_2)
    org_id = relationship("form_institution")


class form_strategy_report(Base):
    __tablename__ = 'strategy_report'
    idx = Column(String)
    title = Column(String)
    author_1 = Column(String, ForeignKey("researcher.idx"))
    author_2 = Column(String, ForeignKey("researcher.idx"))
    institution = Column(String, ForeignKey("investment_institution.org_code"))
    page_url = Column(String)
    pdf_url = Column(String, primary_key=True)
    publish_date = Column(Date)
    file_type = Column(String)
    flag = Column(String)
    au_id_1 = relationship("form_researcher", foreign_keys=author_1)
    au_id_2 = relationship("form_researcher", foreign_keys=author_2)
    org_id = relationship("form_institution")


class form_stock_report(Base):
    __tablename__ = 'stock_research_report'
    info_code = Column(String)
    title = Column(String)
    stock_code = Column(String)
    author_1 = Column(String, ForeignKey("researcher.idx"))
    author_2 = Column(String, ForeignKey("researcher.idx"))
    institution = Column(String, ForeignKey("investment_institution.org_code"))
    indu_code = Column(String)
    page_url = Column(String)
    pdf_url = Column(String, primary_key=True)
    publish_date = Column(Date)
    pre_eps_1y = Column(Float)
    pre_pe_1y = Column(Float)
    pre_eps_2y = Column(Float)
    pre_pe_2y = Column(Float)
    proposal = Column(Integer)
    file_type = Column(String)
    flag = Column(String)
    au_id_1 = relationship("form_researcher", foreign_keys=author_1)
    au_id_2 = relationship("form_researcher", foreign_keys=author_2)
    org_id = relationship("form_institution")
    # indu_id = relationship("form_industry")


class form_industry(Base):
    __tablename__ = 'industry'
    idx = Column(String, primary_key=True)
    industry_name = Column(String)
