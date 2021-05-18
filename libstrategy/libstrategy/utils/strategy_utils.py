#!/usr/bin/python38
from libmysql_utils.mysql8 import mysqlBase
from libbasemodel.form import formStockManager
import pandas
from pandas import DataFrame
import numpy as np
from libstrategy.pair_trading import TradeMessage


class StockPrice(mysqlBase):
    """
    A smart application to get close price.
    : stock_code : benchmark code
    : header : header
    : return: result like DataFrame
    """
    def get_stock_list(self):
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='t').all()
        df = DataFrame.from_dict(query_stock_code)
        stock_list = df['stock_code'].tolist()
        # should test if stock list is null
        return stock_list

    def get_log_price(self, stock_code: str, start='', end='') -> DataFrame:
        query_column = 'trade_date,close_price'
        def_column = ['trade_date', f"{stock_code}"]
        if start or end:
            result = self.condition_select(stock_code, query_column, f"(trade_date>'{start}') and (trade_date<'{end}')")
        else:
            result = self.select_values(stock_code, query_column)
        if not result.empty:
            result.columns = def_column
            result[stock_code].apply(np.log)
            result['trade_date'] = pandas.to_datetime(result['trade_date'])
            result.set_index('trade_date', inplace=True)
        else:
            result = DataFrame()
        return result

    def get_data(self, stock_code: str, query_type='close', start='', end='') -> DataFrame:
        if query_type == 'close':
            query_column = 'trade_date,close_price'
            def_column = ['trade_date', f"{stock_code}"]
        elif query_type == 'full':
            query_column = 'trade_date,open_price,close_price,high_price,low_price'
            def_column = ['trade_date', 'open', 'close', 'high', 'low']
        else:
            query_column = 'trade_date,open_price,close_price,high_price,low_price'
            def_column = ['trade_date', 'open', 'close', 'high', 'low']
        if start or end:
            result = self.condition_select(stock_code, query_column, f"(trade_date>'{start}') and (trade_date<'{end}')")
        else:
            result = self.select_values(stock_code, query_column)
        if not result.empty:
            result.columns = def_column
            result['trade_date'] = pandas.to_datetime(result['trade_date'])
            result.set_index('trade_date', inplace=True)
        else:
            result = DataFrame()
        return result

    def get_benchmark(self, stock_code: str) -> DataFrame:
        return self.get_data(stock_code, query_type='close')

    @classmethod
    def profit_matrix(cls, stock_code: str, df: DataFrame) -> DataFrame:
        df[stock_code] = df[stock_code] / df[stock_code].shift(1)
        return df
