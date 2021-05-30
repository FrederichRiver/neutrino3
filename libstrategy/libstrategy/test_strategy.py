#!/usr/bin/python3
import unittest
from libstrategy.utils.asset import StockAsset
from libstrategy.utils.investment import Investment


class unittest_capital(unittest.TestCase):
    def setUp(self):
        print("Capital test start.")

    def tearDown(self):
        pass

    @unittest.skip("PASS!")
    def test_asset(self):
        print("Initial:")
        asset = StockAsset('SZ002460', currency=20000)
        print(asset)
        print("Buy:")
        asset.buy(**{"volume": 100, "price": 100})
        print(asset)
        print("Sell:")
        asset.sell(**{"volume": -100, "price": 100})
        print(asset)
        print("Buy:")
        asset.buy(**{"volume": 100, "price": 100})
        print(asset)
        print("Buy:")
        asset.buy(**{"volume": 100, "price": 100})
        print(asset)
        print("Settle:")
        asset.settle(price=100.00)
        print(asset)

    def test_investment(self):
        invest = Investment(cash=100000.0)
        stock_list = ['SH601818', 'SZ000625', 'SZ002460']
        invest.init_stock(stock_list)
        invest.add_stock('SH601818')
        print(invest.investment)
        print(invest)
        invest.del_stock(stock_list[0])
        print(invest)
        invest.buy_stock(stock_list[1], 100, 13.55)
        print(invest)
        print(invest.value)
        invest.sell_stock(stock_list[1], 100, 14.45)
        print(invest)
        print(invest.value)




if __name__ == "__main__":
    unittest.main()