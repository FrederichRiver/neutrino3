#!/usr/bin/python38
import re
from libmysql_utils.header import GLOBAL_HEADER
from libutils.utils import read_url


__all__ = [
    'service_init_stock_table',
    'service_init_index_table',
    'service_init_hk_stock_table',
    'service_flag_stock',
    'service_download_stock_data',
    'service_download_index_data',
    'service_stock_data_plot',
    'service_shibor_data_plot',
    'service_treasury_yield_data_plot',
    'service_get_shibor_data',
    'service_record_company_infomation',
    'service_record_company_stock_structure',
    'service_download_news',
    'service_update_keyword',
    'service_record_us_stock',
    'service_data_monitor',
    'service_update_finance_report',
    'service_update_treasury_yield',
    'service_record_stock_interest'
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
    stock_list = StockList(GLOBAL_HEADER)._get_index()
    event = EventTradeDataManager(GLOBAL_HEADER)
    for stock_code in stock_list:
        event.create_stock_table(stock_code)


def service_init_hk_stock_table():
    """
    Init database from a blank stock list.
    """
    from libbasemodel.stock_manager import EventTradeDataManager
    from libbasemodel.stock_model import StockList
    from dev_global.path import CONF_FILE
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
    from libutils.utils import read_json
    from dev_global.path import CONF_FILE
    _, image_path = read_json("image_path", CONF_FILE)
    event = CandleView(GLOBAL_HEADER, image_path)
    event.plot("SZ002460")


def service_shibor_data_plot():
    from libbasemodel.data_view import ShiborView
    from libutils.utils import read_json
    from dev_global.path import CONF_FILE
    _, image_path = read_json("image_path", CONF_FILE)
    event = ShiborView(GLOBAL_HEADER, image_path)
    event.plot()


def service_treasury_yield_data_plot():
    from libbasemodel.data_view import TreasuryYieldView
    from libutils.utils import read_json
    from dev_global.path import CONF_FILE
    _, image_path = read_json("image_path", CONF_FILE)
    event = TreasuryYieldView(GLOBAL_HEADER, image_path)
    event.plot()


def service_get_shibor_data():
    from libbasemodel.shibor import ShiborData
    event = ShiborData(GLOBAL_HEADER)
    event.shibor_url = event.current_month
    df = event.get_excel_object(event.shibor_url)
    event.get_shibor_data(df)


def service_record_company_infomation():
    from libbasemodel.company import EventCompany
    event = EventCompany(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock_code in stock_list:
        event.record_company_infomation(stock_code)


def service_record_company_stock_structure():
    from libbasemodel.company import EventCompany
    event = EventCompany(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock in stock_list:
        event.record_stock_structure(stock)


def service_download_news():
    from dev_global.path import SOFT_PATH
    from libcontext.news_downloader import neteaseFinanceSpider
    from libmysql_utils.mysql8 import mysqlHeader
    header = mysqlHeader('stock', 'stock2020', 'corpus')
    event = neteaseFinanceSpider(header, SOFT_PATH)
    event.generate_url_list()
    # print(len(event.url_list))
    i = 0
    for url in event.url_list:
        i += 1
        # print(i, url)
        event.extract_href(url)
        event.extract_href2(url)
        # print(len(event.href))
    for href in event.href:
        art = event.extract_article(href)
        event.record_article(art)



def service_download_sina_news():
    from dev_global.path import SOFT_PATH
    from libcontext.news_downloader import SinaNewsSpider
    from libmysql_utils.mysql8 import mysqlHeader
    header = mysqlHeader('stock', 'stock2020', 'corpus')
    event = SinaNewsSpider(header, SOFT_PATH)
    event.start_url()
    i = 0
    for url in event.url_list:
        i += 1
        print(i, url)
        event.extract_href(url)
        # print(len(event.href))
    for href in event.href:
        art = event.extract_article(href)
        event.record_article(art)

def service_update_keyword():
    from libnlp.engine.news_classify import NewsBase
    from libmysql_utils.mysql8 import mysqlHeader
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
    from libbasemodel.spider_model import TreasuryYield
    head = mysqlHeader(acc="stock", pw="stock2020", host="115.159.1.221", db="stock")
    mysql = mysqlBase(head)
    url = "http://datacenter.eastmoney.com/api/data/get?callback=datatable1509410&type=RPTA_WEB_TREASURYYIELD&sty=ALL&st=SOLAR_DATE&sr=-1&token=894050c76af8597a853f5b408b759f5d&p={}&ps=50&_=1615912300344" 
    event = TreasuryYield()
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


def service_record_stock_interest():
    from libbasemodel.stock_interest import EventInterest
    event = EventInterest(GLOBAL_HEADER)
    event.j2sql.load_table('stock_interest')
    stock_list = event.get_all_stock_list()
    for stock_code in stock_list:
        event.record_interest(stock_code)


def service_record_stock():
    from libbasemodel.stock_model import StockList
    from libmysql_utils.header import REMOTE_HEADER
    event = StockList(REMOTE_HEADER)
    url = 'http://www.cninfo.com.cn/new/data/szse_stock.json'
    df = event._get_stock_list_data(url)
    event.insert_stock_manager(df)

if __name__ == "__main__":
    service_download_sina_news()
