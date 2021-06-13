#!/usr/bin/python3
import unittest
from libstrategy.utils.asset import StockAsset
from libstrategy.utils.investment import Investment
from libstrategy.utils.account import PairTrading, Benchmark
from libstrategy.strategy.pair_trading import PairTradeStrategy, BenchMarkStrategy
from libstrategy.data_engine.data_engine import StockData
from libmysql_utils.mysql8 import mysqlHeader
from libstrategy.utils.kalendar import Kalendar2
from libstrategy.utils.anzeichen import SignalPairTrade
from libstrategy.utils.report import Report
import matplotlib.pyplot as plt
import pandas as pd

class unittest_capital(unittest.TestCase):
    def setUp(self):
        print("Capital test start.")

    def tearDown(self):
        pass

    @unittest.skip("PASS!")
    def test_asset(self):
        print("Initial:")
        asset = StockAsset('SZ002460', cash=20000)
        print(asset)
        print("Buy:")
        asset.buy('null', volume=100, price=100)
        print(asset)
        print("Sell:")
        asset.sell('null', volume=100, price=100)
        print(asset)
        print("Buy:")
        asset.buy('null', volume=100, price=100)
        print(asset)
        print("Buy:")
        asset.buy('null', volume=100, price=100)
        print(asset)
        print("Settle:")
        asset.settle('null', price=100)
        print(asset)

    @unittest.skip("PASS!")
    def test_investment(self):
        invest = Investment(cash=100000.0)
        stock_list = ['SH601818', 'SZ000625', 'SZ002460']
        invest.init_stock(stock_list)
        invest.add_stock('SH601818')
        print(invest.profolio)
        print(invest)
        invest.del_stock(stock_list[0])
        print(invest)
        invest.buy_stock(stock_list[1], 'null', 100, 13.55)
        print(invest)
        print(invest.value)
        invest.sell_stock(stock_list[1], 'null', 100, 14.45)
        print(invest)
        print(invest.value)

    def test_calander(self):
        calendar = Kalendar2((2019,1,3), (2019,1,20))
        for trade_date in calendar:
            print(trade_date)

    @unittest.skip("TEST")
    def test_benchmark_trade(self):
        head = mysqlHeader(acc='stock', pw='stock2020', db='stock', host='115.159.1.221')
        A = 'SZ002460'
        start = '2019-01-04'
        end = '2021-03-01'
        Data = StockData(head, start, end)
        Data.add_asset(A)
        Data.update()
        #print(Data.data)
        strategy_benchamark = BenchMarkStrategy(A, start, end)
        Mark = Benchmark('Mark', strategy_benchamark, 100000.0, A)
        calendar = Kalendar2((2019,1,3), (2021,3,1))
        latest_data = None
        end_date = None
        for trade_date in calendar:
            end_date = trade_date
            data = Data.get(trade_date)
            latest_data = data
            if not data.empty:
                signal2 = strategy_benchamark.run(trade_date)
                bench_trade = Mark._trade(signal2, trade_date, data)
                Mark.update_price(trade_date, data)
        bench_trade = Mark._trade(-1, trade_date, latest_data)
        Mark.update_price(trade_date, data)
        df2 = Mark.investment.get_hist_value()
        # print(df)
        plt.plot(df2)
        plt.show()

    #@unittest.skip("None")
    def test_pair_trade(self):
        head = mysqlHeader(acc='stock', pw='stock2020', db='stock', host='115.159.1.221')
        A = 'SZ002460'
        B = 'SZ002497'
        start = '2019-01-04'
        end = '2021-03-01'
        Data = StockData(head, start, end)
        Data.add_asset(A)
        Data.add_asset(B)
        Data.update()
        #print(Data.data)
        _, beta, mean, std = PairTradeStrategy.cointegration_check(Data.data[A], Data.data[B])
        #print(beta, mean, std)
        strategy = PairTradeStrategy(A, B, start, end)
        strategy_benchamark = BenchMarkStrategy(A, start, end)
        Mark = Benchmark('Mark', strategy_benchamark, 100000.0, A)
        Mark2 = Benchmark('Mark2', strategy_benchamark, 100000.0, B)
        Person = PairTrading('John',strategy, 100000.0, A, B, beta)
        strategy.set_threshold(**{"high":mean + std, "low": mean - std, "beta": beta, "alpha": mean})
        calendar = Kalendar2((2019,1,3), (2021,3,1))
        report = Report()
        benchmark_report = Report()
        latest_data = None
        end_date = None
        for trade_date in calendar:
            end_date = trade_date
            data = Data.get(trade_date)
            latest_data = data
            if not data.empty:
                signal = strategy(data[A], data[B])
                signal2 = strategy_benchamark.run(trade_date)
                pair_trade = Person._trade(signal, trade_date, data)
                bench_trade = Mark._trade(signal2, trade_date, data)
                bench_trade2 = Mark2._trade(signal2, trade_date, data)
                Mark.update_price(trade_date, data)
                Mark2.update_price(trade_date, data)
                Person.update_price(trade_date, data)
                if pair_trade:
                    report.add_trade(pair_trade)
                if bench_trade:
                    benchmark_report.add_trade(bench_trade)
        end_signal = -1
        pair_trade = Person._trade(end_signal, trade_date, latest_data)
        bench_trade = Mark._trade(end_signal, trade_date, latest_data)
        bench_trade2 = Mark2._trade(end_signal, trade_date, latest_data)
        Person.update_price(trade_date, data)
        Mark.update_price(trade_date, data)
        Mark2.update_price(trade_date, data)
        report.add_trade(pair_trade)
        benchmark_report.add_trade(bench_trade)
        print('***************************')
        for trade in report.trade_list:
            print(trade)
        print('***************************')
        for trade in benchmark_report.trade_list:
            print(trade)
        df = Person.investment.get_hist_value()
        df2 = Mark.investment.get_hist_value()
        df3 = Mark2.investment.get_hist_value()
        df = pd.concat([df, df2, df3], axis=1)
        plt.plot(df)
        plt.show()


if __name__ == "__main__":
    unittest.main()