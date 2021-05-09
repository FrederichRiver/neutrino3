#!/usr/bin/python38
import re
from libmysql_utils.mysql8 import GLOBAL_HEADER
from mars.utils import read_url


__all__ = [
    'service_init_stock_table',
    'service_init_index_table',
    'service_flag_stock',
    'service_download_stock_data',
    'service_download_index_data',
    'service_stock_data_plot',
    'service_shibor_data_plot',
    'service_get_shibor_data',
    'service_record_company_infomation',
    'service_record_company_stock_structure',
    'service_download_news',
    'service_update_keyword',
    'service_record_us_stock',
    'service_data_monitor',
    'service_update_finance_report',
    'service_update_treasury_yield'
    ]


def service_init_stock_table():
    """
    Init database from a blank stock list.
    """
    from libbasemodel.stock_manager import EventTradeDataManager
    from libbasemodel.stock_model import StockList
    stock_list = StockList(GLOBAL_HEADER).get_stock()
    event = EventTradeDataManager(GLOBAL_HEADER)
    for stock_code in stock_list:
        event.create_stock_table(stock_code)


def service_init_index_table():
    """
    Init database from a blank stock list.
    """
    from libbasemodel.stock_manager import EventTradeDataManager
    from libbasemodel.stock_model import StockList
    from dev_global.env import CONF_FILE
    url = read_url('url_hk_stock_list', CONF_FILE)
    stock_list = StockList(GLOBAL_HEADER).get_hk_stock_list(url)
    event = EventTradeDataManager(GLOBAL_HEADER)
    for stock_code in stock_list:
        event.create_stock_table(stock_code)


def service_flag_stock():
    from libbasemodel.stock_classify import StockClassify
    event = StockClassify(GLOBAL_HEADER)
    stock_list = event.get_all_security_list()
    for stock_code in stock_list:
        if re.match(r'^SH60|^SZ00|^SZ300|^SH688', stock_code):
            event.flag_stock_type(stock_code, 't')
        elif re.match(r'^SH900|^SZ200', stock_code):
            event.flag_stock_type(stock_code, 'b')
        elif re.match(r'^SH000|^SH950|^SZ399', stock_code):
            event.flag_stock_type(stock_code, 'i')
        elif re.match(r'^HK', stock_code):
            event.flag_stock_type(stock_code, 'h')


def service_download_stock_data():
    from libbasemodel.stock_manager import EventTradeDataManager
    event = EventTradeDataManager(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock_code in stock_list:
        event.download_stock_data(stock_code)


def service_download_index_data():
    from libbasemodel.stock_manager import EventTradeDataManager
    event = EventTradeDataManager(GLOBAL_HEADER)
    stock_list = event.get_all_index_list()
    for stock_code in stock_list:
        event.download_stock_data(stock_code)


def service_stock_data_plot():
    from libbasemodel.data_view import CandleView
    from libmysql_utils.mysql8 import GLOBAL_HEADER
    from mars.utils import read_json
    from dev_global.env import CONF_FILE
    _, image_path = read_json("image_path", CONF_FILE)
    event = CandleView(GLOBAL_HEADER, image_path)
    event.plot("SZ002460")


def service_shibor_data_plot():
    from libbasemodel.data_view import ShiborView
    from libmysql_utils.mysql8 import GLOBAL_HEADER
    from mars.utils import read_json
    from dev_global.env import CONF_FILE
    _, image_path = read_json("image_path", CONF_FILE)
    event = ShiborView(GLOBAL_HEADER, image_path)
    event.plot()


def service_get_shibor_data():
    from libbasemodel.shibor import ShiborData
    from libmysql_utils.mysql8 import GLOBAL_HEADER
    event = ShiborData(GLOBAL_HEADER)
    event.shibor_url = event.current_month
    df = event.get_excel_object(event.shibor_url)
    event.get_shibor_data(df)


def service_record_company_infomation():
    from libbasemodel.company import EventCompany
    from libmysql_utils.mysql8 import GLOBAL_HEADER
    event = EventCompany(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock_code in stock_list:
        event.record_company_infomation(stock_code)


def service_record_company_stock_structure():
    from libbasemodel.company import EventCompany
    from libmysql_utils.mysql8 import GLOBAL_HEADER
    event = EventCompany(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock in stock_list:
        event.record_stock_structure(stock)


def service_download_news():
    from dev_global.env import SOFT_PATH
    from libcontext.news_downloader import neteaseNewsSpider
    header = mysqlHeader('stock', 'stock2020', 'corpus')
    event = neteaseNewsSpider(header, SOFT_PATH)
    hfile = SOFT_PATH + 'config/HREF_LIST'
    event.load_href_file(hfile)
    for url in event.href:
        # url = "https://money.163.com/21/0302/19/G43UHG4S00259DLP.html"
        art = event.extract_article(url)
        event.record_article(art)


def service_update_keyword():
    from libnlp.engine.news_classify import NewsBase
    nlp_head = mysqlHeader('stock', 'stock2020', 'natural_language')
    event = NewsBase(nlp_head)
    idx_list = event.news_idx()
    for idx in idx_list:
        text = event.news_text(idx)
        if text:
            event.update_keyword(idx, text)


def service_record_us_stock():
    from libmysql_utils.mysql8 import GLOBAL_HEADER
    from libbasemodel.stock_model import USStockList
    event = USStockList(GLOBAL_HEADER)
    us_stock_list = event.get_us_stock_list()
    for stock_code in us_stock_list:
        event.record_us_stock(stock_code)


def service_data_monitor():
    import time
    import random
    from libbasemodel.data_monitor import PriceMonitor
    event = PriceMonitor()
    while True:
        i = random.randint(-5, 10)
        try:
            event.foriegn_future()
            event.inland_future()
        except Exception:
            pass
        time.sleep(30 + i)


def service_update_treasury_yield():
    """
    Treasury yield data of China & US from eastmoney.com
    """
    from libmysql_utils.mysql8 import mysqlHeader, mysqlBase
    from libbasemodel.spider_model import tarantula
    head = mysqlHeader(acc="stock", pw="stock2020", host="115.159.1.221", db="stock")
    mysql = mysqlBase(head)
    url = "http://datacenter.eastmoney.com/api/data/get?callback=datatable1509410&type=RPTA_WEB_TREASURYYIELD&sty=ALL&st=SOLAR_DATE&sr=-1&token=894050c76af8597a853f5b408b759f5d&p={}&ps=50&_=1615912300344" 
    event = tarantula()
    result = event.get_text(url.format(1))
    data = event.resolve_data(result)
    for dataline in data:
        sql1 = event.replace_table1(dataline)
        sql2 = event.replace_table2(dataline)
        mysql.exec(sql1)
        mysql.exec(sql2)


def service_update_finance_report():
    from libbasemodel.finance_report import EventFinanceReport
    event = EventFinanceReport(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock_code in stock_list:
        event.update_balance(stock_code)
        event.update_cashflow(stock_code)
        event.update_income(stock_code)


if __name__ == "__main__":
    from libmysql_utils.mysql8 import mysqlHeader
    remote_head = mysqlHeader(acc="stock", pw="stock2020", db="stock", host="115.159.1.221")
    from dev_global.env import SOFT_PATH
    from libcontext.news_downloader import neteaseFinanceSpider
    header = mysqlHeader('stock', 'stock2020', 'corpus')
    event = neteaseFinanceSpider(header, SOFT_PATH)
    hfile = SOFT_PATH + 'config/HREF_LIST'
    event.load_href_file(hfile)
    for url in event.href:
        # url = "https://money.163.com/21/0302/19/G43UHG4S00259DLP.html"
        art = event.extract_article(url)
        event.record_article(art)
