#!/usr/bin/python3
from venus.company import EventCompany
from mars.network import delay
from venus.finance_report import EventFinanceReport
import re
# from venus.cninfo import cninfoSpider
from mars.utils import ERROR
from libmysql_utils.mysql8 import GLOBAL_HEADER


__version__ = '1.2.15'
__all__ = [
    'event_adjust_factor',
    'event_download_balance_data',
    'event_download_cashflow_data',
    'event_download_finance_report',
    'event_download_income_data',
    'event_download_index_data',
    'event_download_stock_data',
    'event_flag_quit_stock',
    'event_flag_stock',
    'event_finance_info',
    'event_init_interest',
    'event_record_company_infomation',
    'event_record_company_stock_structure',
    'event_record_new_stock',
    ]

# Event Trade Data Manager


# new frame

def event_create_stock_table():
    """
    Init database from a blank stock list.
    """
    from venus.stock_manager2 import EventTradeDataManager
    from venus.stock_base2 import resolve_stock_list
    stock_list = resolve_stock_list('totalstocklist')
    event = EventTradeDataManager(GLOBAL_HEADER)
    for stock_code in stock_list:
        event.create_stock_table(stock_code)


def event_init_index():
    from venus.stock_base2 import StockList
    from venus.stock_manager2 import EventTradeDataManager
    from venus.form import formStockManager
    EventStocklist = StockList(GLOBAL_HEADER)
    stock_list = EventStocklist._get_index()
    event = EventTradeDataManager(GLOBAL_HEADER)
    for stock_code in stock_list:
        if event.stock_exist(stock_code, event.today):
            record = formStockManager(stock_code=stock_code)
            event.session.add(record)
            event.session.commit()


# new frame
def event_record_new_stock():
    from venus.stock_manager2 import EventTradeDataManager
    from venus.stock_base2 import resolve_stock_list
    event = EventTradeDataManager(GLOBAL_HEADER)
    stock_list = resolve_stock_list('stock')
    for stock_code in stock_list:
        event.init_stock_data(stock_code)


# new frame
def event_download_stock_data():
    from libbasemodel.stock_manager import EventTradeDataManager
    from libbasemodel.stock_model import resolve_stock_list
    event = EventTradeDataManager(GLOBAL_HEADER)
    stock_list = resolve_stock_list('stock')
    for stock_code in stock_list:
        event.download_stock_data(stock_code)


# new frame
def event_download_index_data():
    from venus.stock_manager import EventTradeDataManager
    event = EventTradeDataManager(GLOBAL_HEADER)
    stock_list = event.get_all_index_list()
    for stock_code in stock_list:
        event.download_stock_data(stock_code)


# new frame
def event_flag_quit_stock():
    from venus.stock_classify import StockClassify
    from venus.stock_base2 import resolve_stock_list
    event = StockClassify(GLOBAL_HEADER)
    stock_list = resolve_stock_list('stock')
    for stock_code in stock_list:
        flag = event.flag_quit_stock(stock_code)
        if flag:
            sql = (
                f"UPDATE stock_manager set flag='q' "
                f"WHERE stock_code='{stock_code}'")
            event.engine.execute(sql)


# event record interest
def event_init_interest():
    from venus.stock_interest import EventInterest
    from venus.stock_base2 import resolve_stock_list
    stock_list = resolve_stock_list('stock')
    event = EventInterest(GLOBAL_HEADER)
    event._load_template()
    for stock_code in stock_list:
        event.record_interest(stock_code)
        delay(10)


def event_adjust_factor():
    from venus.stock_interest import EventStockData
    from venus.stock_base2 import resolve_stock_list
    stock_list = resolve_stock_list('stock')
    event = EventStockData(GLOBAL_HEADER)
    for stock_code in stock_list:
        print(stock_code)
        df = event.adjust_factor(stock_code)
        event.record_factor(stock_code, df)


# new frame
def event_flag_stock():
    from venus.stock_classify import StockClassify
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


def event_record_company_infomation():
    event = EventCompany(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock_code in stock_list:
        try:
            event.record_company_infomation(stock_code)
        except Exception as e:
            ERROR(e)


def event_finance_info():
    pass


def event_record_company_stock_structure():
    event = EventCompany(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock in stock_list:
        try:
            # print(stock)
            event.record_stock_structure(stock)
            delay(10)
        except Exception as e:
            ERROR(e)


def event_download_finance_report():
    event = EventFinanceReport(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock in stock_list:
        print(f"Download finance report of {stock}.")
        # event.update_balance_sheet(stock)
        event.update_income(stock)
        event.update_balance(stock)
        event.update_cashflow(stock)


# new frame
"""
def event_update_shibor():
    from venus.shibor import EventShibor
    event = EventShibor(GLOBAL_HEADER)
    year_list = range(2006, pandas.Timestamp.today().year + 1)
    for year in year_list:
        url = event.get_shibor_url(year)
        df = event.get_excel_object(url)
        event.get_shibor_data(df)
"""


"""
def event_get_hk_list():
    event = cninfoSpider(GLOBAL_HEADER)
    df = event.get_hk_stock_list()
    event._insert_stock_manager(df)


def event_record_orgid():
    event = cninfoSpider(GLOBAL_HEADER)
    df = event.get_stock_list()
    event._update_stock_manager(df)
    df = event.get_hk_stock_list()
    event._update_stock_manager(df)
"""


def event_download_balance_data():
    event = EventFinanceReport(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock_code in stock_list:
        try:
            event.update_balance(stock_code)
        except Exception:
            ERROR(f"Error occours while recording {stock_code} balance sheet.")


def event_download_cashflow_data():
    event = EventFinanceReport(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock_code in stock_list:
        try:
            event.update_cashflow(stock_code)
        except Exception as e:
            ERROR(f"Error occours while recording {stock_code} cashflow sheet.")
            ERROR(e)


def event_download_income_data():
    event = EventFinanceReport(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock_code in stock_list:
        try:
            event.update_income(stock_code)
        except Exception as e:
            ERROR(f"Error occours while recording {stock_code} income sheet.")
            ERROR(e)


def event_download_detail_data(trade_date_list: list = None):
    import datetime
    from mars.network import delay
    from libbasemodel.stock_model import resolve_stock_list
    from libbasemodel.stock_manager import EventTradeDataManager
    stock_list = resolve_stock_list('stock')
    event = EventTradeDataManager(GLOBAL_HEADER)
    today = datetime.date.today()
    if not trade_date_list:
        trade_date_list = [
            (today - datetime.timedelta(days=i)).strftime('%Y%m%d') for i in range(1, 6)
        ]
    stock_list = event.get_all_stock_list()
    for trade_date in trade_date_list:
        for stock in stock_list:
            # print(f"Download detail trade data {stock}: {trade_date}")
            event.get_trade_detail_data(stock, trade_date)
            delay(3)


def event_set_update_date():
    from venus.stock_manager2 import EventTradeDataManager
    from venus.stock_base2 import resolve_stock_list
    event = EventTradeDataManager(GLOBAL_HEADER)
    stock_list = resolve_stock_list('stock')
    for stock_code in stock_list:
        df = event.select_values(stock_code, 'trade_date')
        try:
            update_date = df[0][-1:].values
            update = update_date[0]
            t = update.strftime('%Y-%m-%d')
            # print(t)
            event.update_value('stock_manager', 'update_date', f"'{t}'", f"stock_code='{stock_code}'")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # date_list = ['20200922', '20200923', '20200928']
    # event_download_detail_data(date_list)
    event_set_update_date()
