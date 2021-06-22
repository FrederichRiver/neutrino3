from abc import ABC
import numpy as np
import pandas as pd
from libmysql_utils.mysql8 import mysqlHeader, mysqlQuery
from libbasemodel.form import formStockManager
from pandas import DataFrame


"""
1.从MySQL查询数据
2.数据清理
3.生成迭代器
"""

class DataBase(mysqlQuery):
    def __init__(self, header: mysqlHeader, from_date: str, end_date: str) -> None:
        super().__init__(header)
        self.pool = []
        self.data = DataFrame()
        self.from_date = from_date
        self.end_date = end_date
        self.__stock_list = []
        self.dataline = DataFrame()
        self.prev_dataline = DataFrame()
        self.factor = {}

    def Config(self, **args):
        raise NotImplementedError

    def _add_asset(self, stock_code):
        """
        param: stock_code is list or str type
        """
        if isinstance(stock_code, str):
            self.pool.append(stock_code)
        elif isinstance(stock_code, list):
            self.pool.extend(stock_code)

    @property
    def asset_list(self):
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='t').all()
        df = pd.DataFrame.from_dict(query_stock_code)
        df.columns = ['stock_code']
        self.__stock_list = df['stock_code'].tolist()
        # should test if stock list is null

    def isStock(self, stock_code: str) -> bool:
        return stock_code in self.__stock_list


class StockData(DataBase):
    """
    Active data engine
    param: from_date, format "2021-05-25" 
    param: end_date, format "2022-05-25"\n
    Provide api: 
    1. iter method: by using iter of StockData to get dataline
    2. get: query data for a specific date 

    """
    def __str__(self) -> str:
        return f"From {self.from_date} to {self.end_date}"

    def Config(self, **args):
        """
        param: {'asset': [stock_1, stock_2, ...]}
        """
        asset_list = args.get('asset', [])
        for asset in asset_list:
            self._add_asset(asset)
        self._update()

    def get_price(self, stock_code: str, start='', end='') -> DataFrame:
        query_column = 'trade_date,close_price,prev_close_price'
        def_column = ['trade_date', f"{stock_code}", f"{stock_code}_prev"]
        if start or end:
            df = self.condition_select(stock_code, query_column, f"trade_date BETWEEN '{start}' AND '{end}'")
        else:
            df = self.select_values(stock_code, query_column)
        if not df.empty:
            df.columns = def_column
            df[f"{stock_code}_xrdr"] = df[stock_code]
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
        else:
            df = DataFrame()
        return df

    def get_log_price(self, stock_code: str, start='', end='') -> DataFrame:
        df = self.get_price(stock_code, start, end)
        if not df.empty:
            df[stock_code].apply(np.log)
        return df

    def _update(self, data_type='log'):
        for stock in self.pool:
            if stock not in self.data.index:
                df = self.get_price(stock_code=stock, start=self.from_date, end=self.end_date)
                self.data = pd.concat([self.data, df], axis=1)
            self.factor[stock] = 1.0
        self.data.dropna(axis=0, how='any', inplace=True)

    def __iter__(self):
        return self.data.iterrows()

    def get(self, query_date: pd.Timestamp):
        if query_date in self.data.index:
            self.prev_dataline = self.dataline
            self.dataline = self.data.loc[query_date]
            for stock_code in self.pool:
                self.dataline[f"{stock_code}_xrdr"] = self.dataline[f"{stock_code}_xrdr"] * self.factor[stock_code]
        return self.dataline

    def update_factor(self, Xrdr_event):
        stock_id = Xrdr_event.stock_id
        price = self.prev_dataline[f"{stock_id}_prev"]
        self.factor[stock_id] = (1 - Xrdr_event.bonus / (10 * price)) / (1 + Xrdr_event.increase / 10 + Xrdr_event.dividend / 10)
        return self.factor[stock_id]

class EventEngine(DataBase):
    # query data
    # event, return (x1, x2, x3)，分红，送股，转股
    # 
    def get_data(self, start='', end=''):
        self.data = {}
        query_column = 'float_bonus,float_increase,float_dividend,xrdr_date,char_stock_code'
        for stock_code in self.pool:
            if start or end:
                df = self.condition_select('stock_interest', query_column, f"char_stock_code='{stock_code}' AND (xrdr_date BETWEEN '{start}' AND '{end}')")
            else:
                df = self.select_values('stock_interest', query_column)
            if not df.empty:
                def_column = ['bonus', 'increase', 'dividend', 'xrdr_date', 'stock_code']
                df.columns = def_column
                df['xrdr_date'] = pd.to_datetime(df['xrdr_date'])
                df.set_index('xrdr_date', inplace=True)
            else:
                df = DataFrame()
            self.data[stock_code] = df

    def get(self, stock_code, query_date: pd.Timestamp):
        if query_date in self.data[stock_code].index:
            self.dataline = self.data[stock_code].loc[query_date]
            return XrdrEvent(query_date, self.dataline)
        else:
            return None

class EventBase(ABC):
    def __init__(self) -> None:
        self.id = 0
        self._timestamp = None
        self.dataline = {}
from enum import Enum

class EventType(Enum):
    XRDR = 1


class XrdrEvent(EventBase):
    def __init__(self, date_time, dataline) -> None:
        super().__init__()
        self.id = 1
        self._timestamp = date_time
        self.stock_id = dataline['stock_code']
        self.bonus= dataline['bonus']
        self.increase = dataline['increase']
        self.dividend = dataline['dividend']

    def __str__(self) -> str:
        text = f"bonus {self.bonus}, increase {self.increase}, dividend {self.dividend} on {self._timestamp}"
        return text