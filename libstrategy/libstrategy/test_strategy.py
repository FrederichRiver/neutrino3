#!/usr/bin/python3
import unittest
from libstrategy.utils.asset import StockAsset
from libstrategy.utils.investment import Investment
from libstrategy.utils.account import PairTrading
from libstrategy.strategy.pair_trading import PairTrade
from libstrategy.data_engine.data_engine import StockData
from libmysql_utils.mysql8 import mysqlHeader
from libstrategy.utils.kalendar import Kalendar2
from libstrategy.utils.anzeichen import SignalPairTrade

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
    @unittest.skip("PASS!")
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

    def test_pair_trade(self):
        head = mysqlHeader(acc='stock', pw='stock2020', db='stock', host='115.159.1.221')
        A = 'SZ002460'
        B = 'SZ002497'
        start = '2019-01-01'
        end = '2021-03-01'
        Data = StockData(head, start, end)
        Data.add_asset(A)
        Data.add_asset(B)
        Data.update()
        print(Data.data)
        _, beta, mean, std = PairTrade.cointegration_check(Data.data[A], Data.data[B])
        print(beta, mean, std)
        strategy = PairTrade(A, B, start, end)
        Trade = PairTrading('John',strategy, 100000.0, A, B, beta)
        Signal = SignalPairTrade()
        Signal.set_threshold(**{"high":mean + std, "low": mean - std, "beta": beta, "alpha": mean})
        calendar = Kalendar2((2019,1,1), (2021,3,1))
        trade_list = []
        latest_data = None
        for date in calendar:
            print(date)
            data = Data.get(date)
            latest_data = data
            if not data.empty:
                signal = Signal(data[A], data[B])
                pair_trade = Trade._trade(signal, data)
                if pair_trade:
                    trade_list.extend(pair_trade)
        end_signal = Signal.set_end()
        pair_trade = Trade._trade(end_signal, latest_data)
        trade_list.extend(pair_trade)
        for trade in trade_list:
            print(trade)

if __name__ == "__main__":
    unittest.main()