#!/usr/bin/python3
from abc import ABCMeta, abstractmethod
from venus.stock_base import StockEventBase, StockBase
from venus import stock_base
import pandas
import datetime
import numpy as np
from jupiter.utils import TIME_FMT

"""
趋势跟踪法
所有的择时法，最终都输出一个stock list
所有的风控，都实时输出signal
所有的选股法，最终也输出一个stock list
1.当90日线位于250日线以下，30日线上穿60日线时，发出买入信号
2.判断n日线lower than m日线
3.判断n日线上穿m日线，或下穿m日线
4.获取一个时间段内的数据线
"""

   

def bs_signal(x):
    if x>0:
        return 'B'
    elif x<0:
        return 'S'
    else:
        return np.nan

class StratagyBase(StockDataSet):
    def __init__(self, header):
        super(StockDataSet, self).__init__()
        self.header = header
        self.price_data = ClosePrice(header)
        self.data = StockDataSet()

    def set_benchmark(self, stock_code)->bool:
        return self.price_data.get_benchmark(stock_code)

    def get_stock_data(self, stock_code:str):
        return self.price_data.get_benchmark(stock_code)

    def detect_cross(self):
        self.data['DIFF'] = self.data['MA5'] - self.data['MA10']
        self.data['DIFF2'] = self.data['DIFF'].shift(-1)
        self.data['flag'] = 0
        print(self.data)
            
def conv(x:list, y:list)-> float:
    result = 0
    for i in range(len(x)):
        result += x[i]*y[i]
    return result

class RiskBase(object):
    def __init__(self):
        pass

    def set_threshold(self, threshold):
        raise NotImplementedError

# Event (market, signal, order, fill)
# Event Queue
# portfolio
# DataHandler(abstract base class)产生market event
# Strategy
class Strategy(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def interface(self):
        raise NotImplementedError
# ExecutionHandler
# Back test
class MarketEventBase(object):
    pass

class SingalBase(object):
    def __init__(self):
        pass

class CAMP(StockEventBase):
    def __init__(self, header):
        super(CAMP, self).__init__(header)
        self._rate = 0.0
        self._market_asset = 'SH000300'

    @property
    def risk_free_rate(self):
        return self._rate
    
    @risk_free_rate.setter
    def risk_free_rate(self, rate):
        self._rate = rate

    @property
    def market_asset(self):
        return self.get_stock_var(self._market_asset)

    @market_asset.setter
    def market_asset(self, stock_code):
        self._market_asset = stock_code

    def get_stock_var(self, stock_code:str):
        import pandas
        from dev_global.env import TIME_FMT
        df = self.mysql.select_values(stock_code, 'trade_date,close_price')
        df.columns = ['date', 'close']
        df['date'] = pandas.to_datetime(df['date'], format=TIME_FMT)
        df.set_index('date', inplace=True)
        df[stock_code] = ( df['close'] - df['close'].shift(1) ) / df['close'].shift(1)
        result = df[stock_code]
        return result

    def asset_beta(self, df:pandas.DataFrame, market_asset:str):
        import numpy as np
        beta_matrix = {}
        for index, col in df.iteritems():
            beta = df[[index, market_asset]].cov().iloc[0, 1] / df[market_asset].var()
            beta_matrix[index] = beta
        return beta_matrix
    
    def sharpe_ratio(self, df:pandas.DataFrame, market_asset:str):
        import numpy as np
        sharpe_matrix = {}
        for index, col in df.iteritems():
            sharpe_ratio = np.sqrt(250)*( df[index].mean() - self.risk_free_rate/250 ) / df[index].std()
            sharpe_matrix[index] = sharpe_ratio
        return sharpe_matrix

def event_sharpe_analysis():
    from dev_global.env import GLOBAL_HEADER
    event = CAMP(GLOBAL_HEADER)
    event.risk_free_rate = 0.03
    print(event.risk_free_rate)
    market_asset = event.market_asset
    stock_pool = [market_asset]
    stock_list = ['SH600000', 'SZ002230', 'SH601818']
    for stock in stock_list:
        df = event.get_stock_var(stock)
        stock_pool.append(df)
    asset_group = pandas.concat(stock_pool, axis=1)
    beta = event.asset_beta(asset_group[-500:], 'SH000300')
    print(beta)
    from datetime import date
    input_group = asset_group.loc[date(2017,1,1):date(2017,12,31),:]
    sharpe = event.sharpe_ratio(input_group, 'SH000300')
    print(sharpe)


class filterBase(StockBase):
    def filter_roe(self, threshold=0.1):
        """
        filter by ROE
        """
        import pandas
        today = '2020-03-31'
        df = self.mysql.condition_select(
            'finance_perspective', 'char_stock_code,float_roe', f"report_date='{today}'")
        df.columns = ['stock', 'roe']
        df = df[df['roe']>threshold]
        result = df['stock'].to_json()
        return df

    def user_defined_pool(self, tag:str):
        """
        Tag file format:
        {   "stock": "XXXXXX"  },
        """
        import os
        import json
        from dev_global.env import SOFT_PATH
        stock_pool = StockPool()
        tag_file = SOFT_PATH + f"config/{tag}-tag.json"
        if os.path.exists(tag_file):
            with open(tag_file, 'r') as f:
                file_content = f.read()
                stock_json = json.loads(file_content)
            stock_pool.pool(stock_json)
        return stock_pool

class StockPool(object):
    def __init__(self, pool_name=None):
        self._name = ''
        if isinstance(pool_name, str):
            self.name = pool_name
        self._pool = []

    @property
    def pool(self):
        return self._pool

    @pool.setter
    def pool(self, value):
        if isinstance(value, dict):
            self._pool.append(value)
        elif isinstance(value, list):
            for stock in value:
                if isinstance(stock, dict):
                    self._pool.append(stock)

    def set_empty(self):
        self._pool = []

class orderBase(object):
    def __init__(self): 
        pass

    def trade_record(self, stock_code, trade_time, trade_type, unit_cost, quantity, order_time=None, flag=None):
        bid = { 
            "order": stock_code,
            "order_time": order_time if not order_time else trade_time,
            "trade_time": trade_time,
            "trade_type": trade_type,
            "unit_cost": unit_cost,
            "quantity": quantity,
            "fee": 0.0,
            "cost": 0.0,
            "flag": False
            }
        return bid
    
    def order_deal(self, order):
        if isinstance(order, dict):
            order['flag'] = True
        return order

class assetBase(object):

    """Docstring for asset. """

    def __init__(self, code, start_time, name=None, cost=0.0, quantity=0):
        """TODO: to be defined. """
        # stock code
        self.code = code
        # stock name could be null
        self.name = name
        # to be delete
        self.unit_cost = cost
        # quantity
        self.quantity = quantity
        # cost
        self.cost = 0.0
        # asset value
        self.value = 0.0
        self.start_time = start_time
        self.trade_record = None

    def order(self):
        self.cost = self.quantity * self.unit_cost
        return self.cost

    def reset(self):
        self.unit_cost = 0.0
        self.quantity = 0.0
        self.cost = 0.0
        self.value = 0.0

#market event engine, running and generate event signal, broadcasting to market.
#date engine generate date series.
#data engine generate data to strategy.
class NoName(object):
    def __init__(self):
        pass

    #build object stock,get stock price series

    #run strategy checking, if cross, send signal

    #recieve signal, generating order

    #recieve order, record.

    #calculate returns.

    #evaluation, beta, sharpe etc.
import datetime


class DateTimeEngine(object):
    def __init__(self):
        self.START_DATE = datetime.date(1990,12,19)

    def date_range(self):
        # full date delta from start date to today.
        n = datetime.date.today() - self.START_DATE
        # generate date series.
        date_series = [self.START_DATE + datetime.timedelta(days=i) for i in range(n.days + 1)]
        return date_series
    
    def holiday_from_stock(self, date_series):
        from polaris.mysql8 import mysqlBase
        from dev_global.env import GLOBAL_HEADER
        mysql = mysqlBase(GLOBAL_HEADER)
        result = mysql.select_values('SH000001', 'trade_date')
        trade_date = list(result[0])
        for dt in trade_date:
            date_series.remove(dt)
        return date_series

    def holiday_from_file(self):
        import datetime
        import time
        holiday = []
        with open('/home/friederich/Documents/dev/neutrino/applications/config/holiday', 'r') as f:
            dt = f.readline().strip()
            while dt: 
                holiday.append(datetime.date())
                dt = f.readline().strip()
        print(holiday)


if __name__ == "__main__":
    from dev_global.env import GLOBAL_HEADER, TIME_FMT
    dateEngine = DateTimeEngine()
    date_list = dateEngine.date_range()
    holiday = dateEngine.holiday_from_stock(date_list)
    dateEngine.holiday_from_file()