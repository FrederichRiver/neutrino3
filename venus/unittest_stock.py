#!/usr/bin/python38
import unittest


class unittest_stock(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @unittest.skip("Pass")
    def test_download_stock_data(self):
        from libbasemodel.stock_manager import EventTradeDataManager
        from libbasemodel.stock_model import resolve_stock_list
        from libmysql_utils.mysql8 import LOCAL_HEADER
        event = EventTradeDataManager(LOCAL_HEADER)
        stock_list = resolve_stock_list('stock')
        for stock_code in stock_list[:7]:
            event.download_stock_data(stock_code)

    @unittest.skip("Pass")
    def test_download_detail_stock_data(self):
        import datetime
        from mars.network import delay
        from libmysql_utils.mysql8 import LOCAL_HEADER
        from libbasemodel.stock_model import resolve_stock_list
        from libbasemodel.stock_manager import EventTradeDataManager
        trade_date_list = ['20201109', '20201110', '20201111', '20201112', '20201113']
        stock_list = resolve_stock_list('stock')
        event = EventTradeDataManager(LOCAL_HEADER)
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


if __name__ == "__main__":
    unittest.main()
