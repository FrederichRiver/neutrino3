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
    def __init__(self, header: mysqlHeader) -> None:
        super().__init__(header)
        self.pool = []
        self.data = DataFrame()

    def Config(self, **args):
        raise NotImplementedError

    def add_asset(self, stock_code):
        """
        param: stock_code is list or str type
        """
        if isinstance(stock_code, str):
            self.pool.append(stock_code)
        elif isinstance(stock_code, list):
            self.pool.extend(stock_code)

class StockData(DataBase):
    """
    param: from_date, format "2021-05-25" 
    param: end_date, format "2022-05-25"\n
    Provide api: 
    1. iter method: by using iter of StockData to get dataline
    2. get: query data for a specific date 

    """
    def __init__(self, header: mysqlHeader, from_date: str, end_date: str) -> None:
        super(StockData, self).__init__(header)
        self.from_date = from_date
        self.end_date = end_date
        self.__stock_list = []

    def __str__(self) -> str:
        return f"From {self.from_date} to {self.end_date}"

    def Config(self, **args):
        return super().Config(**args)

    def get_price(self, stock_code: str, start='', end='') -> DataFrame:
        query_column = 'trade_date,close_price'
        def_column = ['trade_date', f"{stock_code}"]
        if start or end:
            df = self.condition_select(stock_code, query_column, f"trade_date BETWEEN '{start}' AND '{end}'")
        else:
            df = self.select_values(stock_code, query_column)
        if not df.empty:
            df.columns = def_column
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

    def update(self, data_type='log'):
        for stock in self.pool:
            if stock not in self.data.index:
                df = self.get_price(stock_code=stock, start=self.from_date, end=self.end_date)
                self.data = pd.concat([self.data, df], axis=1)
        self.data.dropna(axis=0, how='any', inplace=True)

    def __iter__(self):
        return self.data.iterrows()

    def get(self, query_date):
        if query_date in self.data.index:
            result = self.data.loc[query_date]
        else:
            result = DataFrame()
        return result

    @property
    def stock_list(self):
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='t').all()
        df = pd.DataFrame.from_dict(query_stock_code)
        df.columns = ['stock_code']
        self.__stock_list = df['stock_code'].tolist()
        # should test if stock list is null

    def isStock(self, stock_code: str) -> bool:
        return stock_code in self.__stock_list