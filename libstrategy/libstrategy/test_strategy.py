#!/usr/bin/python3
import unittest
from libstrategy.utils.asset import StockAsset
from libstrategy.utils.investment import Investment
from libstrategy.utils.account import PairTrading, Benchmark
from libstrategy.strategy.pair_trading import PairTradeStrategy, BenchMarkStrategy, cointegration_check
from libstrategy.data_engine.data_engine import StockData, EventEngine
from libmysql_utils.mysql8 import mysqlHeader, mysqlQuery
from libstrategy.utils.kalendar import Kalendar
from libstrategy.utils.report import Report
import matplotlib.pyplot as plt
import pandas as pd

class unittest_capital(unittest.TestCase):
    def setUp(self):
        print("Capital test start.")
        self.head = mysqlHeader(acc='stock', pw='stock2020', db='stock', host='115.159.1.221')
        self.A = 'SZ002460'
        self.B = 'SZ002497'
        self.file = '/home/fred/Downloads/tmp_data.html'

    def tearDown(self):
        pass

    @unittest.skip("Asset buy & sell")
    def test_asset(self):
        print("Initial:")
        asset = StockAsset('SZ002460', cash=100000)
        print(asset)
        print("Buy:")
        print(f"Initial: {asset.value}")
        asset.buy('null', volume=4600, price=21.88)
        cost = 4600 * 21.88
        print(f"Cost: {cost}")
        commission = asset.Comm(cost)
        print(f"Commission: {commission}")
        fee = asset.Fee(cost)
        print(f"Transfer fee: {fee}")
        total = commission + fee
        print(f"Total fee: {total}")
        print(f"Cash: {asset.cash}")
        print(f"Value: {asset.value}")
        print("Sell")
        asset.sell('null', volume=4600, price=22.27)
        gain = 4600 * 22.27
        print(f"Gain: {gain}")
        tax = asset.TAX(gain)
        print(f"Tax: {tax}")
        commission = asset.Comm(gain)
        print(f"Commission: {commission}")
        fee = asset.Fee(gain)
        print(f"Transfer fee: {fee}")
        total = commission + fee + tax
        print(f"Total fee: {total}")
        get_cash = gain - total
        print(f"Get: {get_cash}")
        print(f"Value: {asset.value}")
        
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
        invest.buy_stock(stock_list[1], 'null', 100, 10.0)
        print(invest)
        print(invest.value)
        invest.sell_stock(stock_list[1], 'null', 100, 11.0)
        print(invest)
        print(invest.value)

    @unittest.skip("Kalander")
    def test_calander(self):
        calendar = Kalendar('2019-1-3', "2019-02-03")
        for trade_date in calendar:
            print(trade_date)

    @unittest.skip("Benchmark")
    def test_benchmark_trade(self):
        start = '2019-07-20'
        end = '2019-09-01'
        Data = StockData(self.head, start, end)
        Data.Config(**{'asset': [self.A]})
        Xrdr = EventEngine(self.head, start, end)
        Xrdr._add_asset(self.A)
        Xrdr.get_data(start=start, end=end)
        strategy_benchamark = BenchMarkStrategy(self.A, start, end)
        Mark = Benchmark('Mark', strategy_benchamark, 100000.0, self.A)
        calendar = Kalendar(start, end)
        for trade_date in calendar:
            event_list = Xrdr.get(self.A, trade_date)
            for event in event_list:
                Data.update_factor(event)
                data = Data.get(trade_date)
                Mark.investment.profolio[self.A].xrdr(trade_date, event.bonus, event.increase, event.dividend)
            data = Data.get(trade_date)
            print(data)
            if not data.empty:
                signal = strategy_benchamark.run(trade_date)
                Mark.trade(signal, trade_date, data)
                strategy_benchamark.built(True)
            print(Mark.investment)
        Mark.settle(Data.prev_date, Data.prev_dataline)
        print(Mark.investment)
        df2 = Mark.investment.get_hist_value()
        df2 = df2 / Mark.init_cash
        df2.to_html(self.file)
        plt.plot(df2)
        plt.show()

    #@unittest.skip("Strategy")
    def test_pair_trade(self):
        start = '2019-01-04'
        end = '2021-03-01'
        #end = '2019-02-01'
        pool = [self.A, self.B]
        Data = StockData(self.head, start, end)
        Data.Config(**{'asset': [self.A, self.B]})
        Xrdr = EventEngine(self.head, start, end)
        Xrdr.Config(**{'asset': pool})
        #_, beta, mean, std = cointegration_check(Data.data[self.A], Data.data[self.B])
        beta = 5.60
        mean = -8.07
        std = 8.22
        #print(beta, mean, std)
        #print(beta, mean, std)
        strategy = PairTradeStrategy(self.A, self.B, start, end)
        strategy_benchamark = BenchMarkStrategy(self.A, start, end)
        Mark = Benchmark('Mark', strategy_benchamark, 100000.0, self.A)
        Mark2 = Benchmark('Mark2', strategy_benchamark, 100000.0, self.B)
        Person = PairTrading('John',strategy, 100000.0, self.A, self.B, beta)
        strategy.set_threshold(**{"high":mean + std, "low": mean - std, "beta": beta, "alpha": mean})
        calendar = Kalendar(start, end)
        report1 = Report('Pair Trading')
        report2 = Report('SZ002460')
        report3 = Report('SZ002497')
        for trade_date in calendar:
            print(trade_date)
            event_list = Xrdr.get(trade_date)
            for event in event_list:
                Data.update_factor(event)
                Person.xrdr(trade_date, event)
            data = Data.get(trade_date)
            if not data.empty:
                print(data)
                signal = strategy.run(trade_date, data[f"{self.A}_xrdr"], data[f"{self.B}_xrdr"])
                signal2 = strategy_benchamark.run(trade_date)
                pair_trade = Person.trade(signal, trade_date, data)
                bench_trade = Mark.trade(signal2, trade_date, data)
                bench_trade2 = Mark2.trade(signal2, trade_date, data)
                strategy_benchamark.built(True)
                for order in pair_trade:
                    print(order)
                #print("SZ002460")
                for order in bench_trade:
                    print(order)
                #print("SZ002497")
                for order in bench_trade2:
                    print(order)
                report1.add_trade(pair_trade)
                report2.add_trade(bench_trade)
                report3.add_trade(bench_trade2)
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
        df = pd.concat([df, df2, df3], axis=1)
        df.to_html('/home/fred/Downloads/tmp_data.html')
        plt.show()


    @unittest.skip("Xrdr Event")
    def test_xrdr_event(self):
        start = '2019-01-03'
        end = '2021-03-01'
        Data = EventEngine(self.head, start, end)
        Data._add_asset(self.A)
        Data._add_asset(self.B)
        Data.get_data(start=start, end=end)
        calendar = Kalendar('2019-1-3', '2021-3-1')
        for trade_date in calendar:
            data = Data.get(self.A, trade_date)
            for event in data:
                print(event)

    @unittest.skip("xrdr")
    def test_xrdr(self):
        start = '2019-07-20'
        end = '2019-07-30'
        Data = StockData(self.head, start, end)
        Data.Config(**{'asset': [self.A,]})
        Xrdr = EventEngine(self.head, start, end)
        Xrdr._add_asset(self.A)
        Xrdr.get_data(start=start, end=end)
        strategy_benchamark = BenchMarkStrategy(self.A, start, end)
        Mark = Benchmark('Mark', strategy_benchamark, 100000.0, self.A)
        calendar = Kalendar(start, end)
        for trade_date in calendar:
            event_list = Xrdr.get(self.A, trade_date)
            for event in event_list:
                Data.update_factor(event)
                data = Data.get(trade_date)
                Mark.trade(3, trade_date, data, event)
            data = Data.get(trade_date)
            if not data.empty:
                signal = strategy_benchamark.run(trade_date)
                Mark.trade(signal, trade_date, data, None)
                strategy_benchamark.built(True)
        Mark.settle('null', Data.prev_dataline[self.A])
        print(Mark.investment)
        df2 = Mark.investment.get_hist_value()
        plt.plot(df2)
        plt.show()
        """
        Trade date, close price , Volume    , 
        2019-07-22, 21.88       , 4600  ,   100648   
        2019-07-23, 22          , 4600  ,   101200
        2019-07-24, 22.31       ,4600   ,   102626
        2019-07-25, 22.28       ,4600   ,   102488
        2019-07-26, 22.34, XRDR ,4600   ,   102764
        2019-07-29, 22.2        ,4600   ,   102120
        2019-07-30, 22.27       ,0      ,   102442
        """

    @unittest.skip("Report")
    def test_report(self):
        A = 'SZ002460'
        start = '2019-01-04'
        end = '2021-03-01'
        Data = StockData(self.head, start, end)
        Data.Config(**{'asset': [A, ]})
        report = Report('Pair Trading')
        report.get_data(Data.data)
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

def xrdr():
    head = mysqlHeader(acc='stock', pw='stock2020', db='stock', host='115.159.1.221')
    event = mysqlQuery(head)
    stock_code = 'SH600000'
    df = event.select_values(stock_code, 'trade_date,open_price,close_price,high_price,low_price,prev_close_price,amplitude')
    df.columns = ['date', 'open', 'close', 'high', 'low', 'prev','amplitude']
    df = df.set_index('date')
    xdf = event.condition_select('stock_interest', 'xrdr_date,float_bonus,float_increase,float_dividend', f"char_stock_code='{stock_code}'")
    xdf.columns = ['date', 'bonus', 'increase', 'dividend']
    xdf = xdf.set_index('date')
    df = pd.concat([df, xdf], axis=1)
    df.to_html('/home/fred/Downloads/tmp_data.html')
    

if __name__ == "__main__":
    unittest.main()
