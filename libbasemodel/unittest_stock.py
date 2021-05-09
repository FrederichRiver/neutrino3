#!/usr/bin/python38
import unittest
from libbasemodel.stock_model import StockList


class unittest_stock(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @unittest.skip("Pass")
    def test_stockbase(self):
        from libmysql_utils.mysql8 import ROOT_HEADER
        from dev_global.env import CONF_FILE
        from mars.utils import read_url
        event = StockList(ROOT_HEADER)
        url = read_url('url_szse_stock_list', CONF_FILE)
        result = event.get_stock_list(url)
        print(result.head(10))
        # event.insert_stock_manager(result)

    @unittest.skip("Pass")
    def test_download_stock_data(self):
        from libbasemodel.stock_manager import EventTradeDataManager
        from libbasemodel.stock_model import resolve_stock_list
        from libmysql_utils.mysql8 import ROOT_HEADER
        event = EventTradeDataManager(ROOT_HEADER)
        stock_list = resolve_stock_list('stock')
        for stock_code in stock_list[:7]:
            event.download_stock_data(stock_code)

    @unittest.skip("Pass")
    def test_download_detail_stock_data(self):
        import datetime
        from mars.network import delay
        from libmysql_utils.mysql8 import ROOT_HEADER
        from libbasemodel.stock_model import resolve_stock_list
        from libbasemodel.stock_manager import EventTradeDataManager
        trade_date_list = ['20201109', '20201110', '20201111', '20201112', '20201113']
        stock_list = resolve_stock_list('stock')
        event = EventTradeDataManager(ROOT_HEADER)
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

    @unittest.skip("Pass")
    def test_NoneHeaderError(self):
        try:
            raise NoneHeaderError('Test!')
        except NoneHeaderError as e:
            print(e)

    @unittest.skip("Pass")
    def test_stockEventBase(self):
        from dev_global.env import GLOBAL_HEADER
        import pandas as pd
        event = StockEventBase(GLOBAL_HEADER)
        try:
            print(event)
            event.update_date_time()
            event.get_all_stock_list()
        except Exception as e:
            print(e)

    @unittest.skip("Pass")
    def test_StockList(self):
        from stock_base import StockList
        event = StockList()
        event.get_sh_stock()
        stock_list = event.get_sz_stock()
        print(stock_list[0], stock_list[-1])

    @unittest.skip("Pass")
    def test_stock_interest(self):
        from dev_global.env import GLOBAL_HEADER
        from stock_interest import EventInterest
        import numpy as np
        event = EventInterest(GLOBAL_HEADER)
        event.get_all_stock_list()
        for stock_code in event.stock_list:
            try:
                print(stock_code)
                tab = event.resolve_table(stock_code)
                tab.replace(['--'], np.nan, inplace=True)
                tab.to_sql(
                        'test_interest', event.mysql.engine.connect(),
                        if_exists="append", index=True
                        )
            except Exception:
                print(f"Error while recording interest of {stock_code}")

    @unittest.skip("Pass")
    def test_dataline(self):
        import pandas as pd
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6],
            'name': ['Alice', 'Bob', 'Cindy', 'Eric', 'Helen', 'Grace'],
            'math': [90, 89, 99, 78, 97, 93],
            'english': [89, 94, 80, 94, 94, 90]})
        dt = dataLine('test_interest')
        sql_list = dt.insert_sql(df)
        sql_list = dt.update_sql(df, ['id', 'name'])
        for sql in sql_list:
            print(sql)

    @unittest.skip("Pass")
    def test_financeReport(self):
        from dev_global.env import GLOBAL_HEADER
        from finance_report import EventFinanceReport
        event = EventFinanceReport(GLOBAL_HEADER)
        event.update_balance_sheet("SH601818")

    @unittest.skip("Pass")
    def test_stockcode(self):
        from venus.stock_base import StockCodeFormat
        event = StockCodeFormat()
        call_result = event('600000.SH')
        func_result = event.net_ease_code('SH601818')
        print(call_result)
        print(func_result)

    @unittest.skip("Pass")
    def test_absolute_path(self):
        from venus.stock_manager import absolute_path
        x = 'path/path2/path3'
        y = 'path/path2/path3/'
        z = 'path4/file'
        z2 = '/path4/file'
        print(absolute_path(x,z))
        print(absolute_path(x,z2))
        print(absolute_path(y,z))
        print(absolute_path(y,z2))

    @unittest.skip("Pass")
    def test_stockBase(self):
        from venus.stock_base import StockBase
        from polaris.mysql8 import GLOBAL_HEADER
        event = StockBase(GLOBAL_HEADER)
        result = event.get_all_stock_list()
        print(result)

    @unittest.skip("Pass")
    def test_stock_manager(self):
        from polaris.mysql8 import GLOBAL_HEADER
        from venus.stock_manager2 import EventTradeDataManager
        from venus.stock_base2 import resolve_stock_list
        stock_list = resolve_stock_list('totalstocklist')
        event = EventTradeDataManager(GLOBAL_HEADER)
        result = event.get_trade_data('SH600000', event.today)
        print(result)

    @unittest.skip("Pass")
    def test_shibor(self):
        import pandas as pd
        from libbasemodel.shibor import ShiborData
        from libmysql_utils.mysql8 import LOCAL_HEADER
        event = ShiborData(LOCAL_HEADER)
        year_list = range(2006, pd.Timestamp.today().year + 1)
        for year in year_list:
            print(year)
            url = event.get_shibor_url(year)
            df = event.get_excel_object(url)
            event.get_shibor_data(df)


unittest.main()


if __name__ == "__main__":
    pass
