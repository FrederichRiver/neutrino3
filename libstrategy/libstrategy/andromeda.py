#!/usr/bin/python3

from venus import stock_base
import pandas
import datetime
import numpy as np
from abc import abstractmethod, ABC
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

class StockDataSet(object):
    """
    get data from a exterior data like pandas.DataFrame.
    method: StockDataSet.data = pandas.DataFrame
    """
    def __init__(self):
        self.data = pandas.DataFrame()

    def set_stock_data(self, df:pandas.DataFrame):
        """
        :param df columns [trade_date, open_price, close_price, high_price, low_price]
        """
        if df.shape[1] != 5:
            print("data shape error, input date should has 5 columns, date type first, and others float.")
        df.columns = ['trade_date', 'open', 'close', 'high', 'low']
        df['trade_date'] = pandas.to_datetime(df['trade_date'],format=TIME_FMT)
        df.set_index('trade_date', inplace=True)
        mean = [5, 10,]
        for i in mean:
            df[f"MA{i}"] = df['close'].rolling(i).mean()
        return df

    def set_time_period(self, start_date:datetime.date, end_date:datetime.date):
        self.data = self.data.loc[start_date:end_date]
        return self.data

    def get_data(self):
        return self.data

    def detect_cross(self):
        import numpy as np
        self.data['DIFF'] = self.data['MA5'] - self.data['MA10']
        self.data['DIFF2'] = self.data['DIFF'].shift(1)
        self.data.dropna(inplace=True)
        self.data['flag'] = self.data['DIFF'] * self.data['DIFF2'] 
        self.data['flag'] = self.data['flag'].apply(lambda x:  1 if x<=0 else 0 )
        self.data['flag'] *= np.sign(self.data['DIFF'])
        self.data['signal'] = self.data['flag'].apply(bs_signal )
        self.data['amp'] = self.data['close'] / self.data['close'].shift(1)
        # print(self.data)
    
    def profit(self):
        self.data['value'] = 1.0
        p = 0
        v = 1.0
        for index,row in self.data.iterrows():
            if p:
                v *= row['amp']
            self.data.loc[index,'value'] = v
            if row['signal'] == 'B':
                p = 1.0
            elif row['signal'] == 'S':
                p = 0.0
        print(self.data)
        import matplotlib.pyplot as plt
        result = pandas.DataFrame()
        #result['close'] = self.data['close']
        result['value'] = self.data['value']
        result.index = self.data.index
        result.plot()
        plt.show()
     

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

if __name__ == "__main__":
    
    from polaris.mysql8 import mysqlBase
    from dev_global.env import GLOBAL_HEADER

    mysql = mysqlBase(GLOBAL_HEADER)
    event = StockDataSet()
    event.data = mysql.select_values('SH000300', 'trade_date,open_price,close_price,highest_price,lowest_price')
    event.set_stock_data(event.data)
    event.set_time_period(datetime.date(2019,1,1), datetime.date(2020,1,1))
    event.detect_cross()
    event.profit()
    