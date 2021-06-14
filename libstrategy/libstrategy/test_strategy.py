#!/usr/bin/python3
import unittest
from libstrategy.utils.asset import StockAsset
from libstrategy.utils.investment import Investment
from libstrategy.utils.account import PairTrading, Benchmark
from libstrategy.strategy.pair_trading import PairTradeStrategy, BenchMarkStrategy
from libstrategy.data_engine.data_engine import StockData
from libmysql_utils.mysql8 import mysqlHeader
from libstrategy.utils.kalendar import Kalendar
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

    @unittest.skip("Kalander")
    def test_calander(self):
        calendar = Kalendar((2019,1,3), (2019,2,3))
        for trade_date in calendar:
            print(trade_date)

    @unittest.skip("Benchmark")
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
        calendar = Kalendar((2019,1,3), (2021,3,1))
        latest_data = None
        end_date = None
        for trade_date in calendar:
            end_date = trade_date
            data = Data.get(trade_date)
            latest_data = data
            if not data.empty:
                signal2 = strategy_benchamark.run(trade_date)
                bench_trade = Mark.trade(signal2, trade_date, data)
                Mark.update_price(trade_date, data)
        bench_trade = Mark.trade(-1, trade_date, latest_data)
        Mark.update_price(trade_date, data)
        df2 = Mark.investment.get_hist_value()
        # print(df)
        plt.plot(df2)
        plt.show()

    #@unittest.skip("Strategy")
    def test_pair_trade(self):
        head = mysqlHeader(acc='stock', pw='stock2020', db='stock', host='115.159.1.221')
        A = 'SZ002460'
        B = 'SZ002497'
        start = '2020-01-03'
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
        calendar = Kalendar((2020,1,3), (2021,3,1))
        latest_data = None
        end_date = None
        for trade_date in calendar:
            end_date = trade_date
            data = Data.get(trade_date)
            latest_data = data
            if not data.empty:
                signal = strategy.run(trade_date, data[A], data[B])
                signal2 = strategy_benchamark.run(trade_date)
                pair_trade = Person.trade(signal, trade_date, data)
                bench_trade = Mark.trade(signal2, trade_date, data)
                bench_trade2 = Mark2.trade(signal2, trade_date, data)
                Mark.update_price(trade_date, data)
                Mark2.update_price(trade_date, data)
                Person.update_price(trade_date, data)
        end_signal = -1
        pair_trade = Person.trade(end_signal, trade_date, latest_data)
        bench_trade = Mark.trade(end_signal, trade_date, latest_data)
        bench_trade2 = Mark2.trade(end_signal, trade_date, latest_data)
        Person.update_price(trade_date, data)
        Mark.update_price(trade_date, data)
        Mark2.update_price(trade_date, data)
        df = Person.investment.get_hist_value()
        df2 = Mark.investment.get_hist_value()
        df3 = Mark2.investment.get_hist_value()
        report1 = Report('Pair Trading')
        report1.get_data(df)
        report2 = Report('SZ002460')
        report2.get_data(df2)
        report3 = Report('SZ002497')
        report3.get_data(df3)
        report_list = [report1, report2, report3]
        for report in report_list:
            data = report.run()
            print(report.id)
            print("-" * 20)
            print_report(data)
        df = df / 100000
        df2 = df2 / 100000
        df3 = df3 / 100000
        plt.plot(df, label='Pair Trading')
        plt.plot(df2, label='SZ002460')
        plt.plot(df3, label='SZ002497')
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)
        plt.show()


    @unittest.skip("Report")
    def test_report(self):
        head = mysqlHeader(acc='stock', pw='stock2020', db='stock', host='115.159.1.221')
        A = 'SZ002460'
        start = '2019-01-04'
        end = '2021-03-01'
        Data = StockData(head, start, end)
        Data.add_asset(A)
        Data.update()
        data = Data.data
        report = Report('Pair Trading')
        report.get_data(data)
        report_data = report.run()
        report_text = (
            f"Total Return: {'%.1f%%' % (100 * report_data['total_return'])}\n"
            f"Annalized Return : {'%.1f%%' % (100 * report_data['annalized_return'])}\n"
            f"Sharpe Ratio : {'%.3f' % report_data['sharpe_ratio']}\n"
            f"Max Draw : {'%.1f%%' % (100 * report_data['max_draw'])}"
            )
        print(report_text)


def print_report(report_data):
    report_text = (
            f"Total Return: {'%.1f%%' % (100 * report_data['total_return'])}\n"
            f"Annalized Return : {'%.1f%%' % (100 * report_data['annalized_return'])}\n"
            f"Sharpe Ratio : {'%.3f' % report_data['sharpe_ratio']}\n"
            f"Max Draw : {'%.1f%%' % (100 * report_data['max_draw'])}"
            )
    print(report_text)

if __name__ == "__main__":
    unittest.main()