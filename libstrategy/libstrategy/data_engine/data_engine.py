from typing import Tuple
import pandas as pd
from libmysql_utils.mysql8 import mysqlHeader, mysqlQuery
from libbasemodel.form import formStockManager
from pandas import DataFrame, Series
from .event import XrdrEvent

"""
1.从MySQL查询数据
2.数据清理
3.生成迭代器
"""

class DataBase(mysqlQuery):
    """
    用于查询数据的基类
    """
    def __init__(self, header: mysqlHeader, from_date: str, end_date: str) -> None:
        """
        input date format
        from_date: 2021-08-01
        end_date: 2021-08-31
        """
        super().__init__(header)
        self.pool = []
        self.data = DataFrame()
        self.from_date = from_date
        self.end_date = end_date
        self._stock_list = []
        self.dataline = DataFrame()
        self.prev_date = None
        self.prev_dataline = DataFrame()
        self.factor = {}

    def Config(self, **args):
        """
        这个方法将来要被重构以适应具体的类。
        """
        raise NotImplementedError

    def _add_asset(self, stock_code: str):
        """
        param: stock_code is list or str type
        """
        if isinstance(stock_code, str):
            self.pool.append(stock_code)
        elif isinstance(stock_code, list):
            self.pool.extend(stock_code)

    @property
    def asset_list(self) -> list:
        """
        从数据库获取所有的股票代码，供查询股票代码的真实性
        """
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='t').all()
        df = pd.DataFrame.from_dict(query_stock_code)
        df.columns = ['stock_code']
        self._stock_list = df['stock_code'].tolist()
        # should test if stock list is null
        return self._stock_list

    def isStock(self, stock_code: str) -> bool:
        """
        判断是否是真实存在的股票代码
        """
        return stock_code in self._stock_list


class XrdrDataEngine(DataBase):
    """
    专用于相关性计算的数据引擎，仅提供复权数据。
    """
    def Config(self, **args):
        """
        param: {'asset': [stock_1, stock_2, ...]}
        """
        asset_list = args.get('asset', [])
        for asset in asset_list:
            self._add_asset(asset)
        self._update()

    def get_data(self, stock_code: str, start='', end='') -> Series:
        """
        每个stock返回3列数据‘收盘价’，‘前收盘价’，‘复权价(未复权,待复权计算)’
        """
        query_column = 'trade_date,close_price,adjust_factor'
        def_column = ['trade_date', f"{stock_code}", "adjust_factor"]
        if start or end:
            df = self.condition_select(stock_code, query_column, f"trade_date BETWEEN '{start}' AND '{end}'")
        else:
            df = self.select_values(stock_code, query_column)
        if not df.empty:
            df.columns = def_column
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            df[stock_code] = df[stock_code] * df['adjust_factor']
        else:
            df = DataFrame()
        return df[stock_code]



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

    """用于初始化"""
    def Config(self, **args):
        """
        param: {'asset': [stock_1, stock_2, ...]}
        """
        asset_list = args.get('asset', [])
        for asset in asset_list:
            self._add_asset(asset)
        self._update()

    def get_data(self, stock_code: str, start='', end='') -> DataFrame:
        """
        每个stock返回3列数据‘收盘价’，‘前收盘价’，‘复权价(未复权,待复权计算)’
        """
        query_column = 'trade_date,close_price,adjust_factor'
        def_column = ['trade_date', f"{stock_code}", f"{stock_code}_factor"]
        if start or end:
            df = self.condition_select(stock_code, query_column, f"trade_date BETWEEN '{start}' AND '{end}'")
        else:
            df = self.select_values(stock_code, query_column)
        if not df.empty:
            df.columns = def_column
            df[f"{stock_code}_xrdr"] = df[stock_code] * df[f"{stock_code}_factor"]
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            result = df[[stock_code, f"{stock_code}_xrdr"]]
            return result
        else:
            df = DataFrame()
            return df

    def _update(self):
        for stock in self.pool:
            if stock not in self.data.index:
                df = self.get_data(stock_code=stock, start=self.from_date, end=self.end_date)
                self.data = pd.concat([self.data, df], axis=1)
            self.factor[stock] = 1.0
        self.data.dropna(axis=0, how='any', inplace=True)


    """用于逐日回测"""
    def __iter__(self):
        return self.data.iterrows()

    def get(self, query_date: pd.Timestamp) -> DataFrame:
        """
        按日期返回数据行，用于逐日回测
        """
        if query_date in self.data.index:
            self.prev_date = query_date
            self.prev_dataline = self.dataline
            self.dataline = self.data.loc[query_date]
            for stock_code in self.pool:
                self.dataline[f"{stock_code}_xrdr"] = self.dataline[f"{stock_code}_xrdr"] * self.factor[stock_code]
        return self.dataline

    def update_factor(self, Xrdr_event: XrdrEvent) -> float:
        """
        根据XRDR事件进行复权因子更新。
        """
        stock_id = Xrdr_event.stock_id
        price = self.prev_dataline[f"{stock_id}_prev"]
        self.factor[stock_id] = (1 - Xrdr_event.dividend / (10 * price)) / (1 + Xrdr_event.increase / 10 + Xrdr_event.bonus / 10)
        return self.factor[stock_id]


class EventEngine(DataBase):
    table_name = 'stock_interest'
    # query data
    # event, return (x1, x2, x3)，分红，送股，转股
    # API
    def Config(self, **args):
        """
        param: {'asset': [stock_1, stock_2, ...]}
        """
        asset_list = args.get('asset', [])
        for asset in asset_list:
            self._add_asset(asset)
        self.load()

    def _reset(self):
        """
        仅被load调用，将类重置
        """
        self.data = {}

    def load(self):
        """
        类重置之后，重新载入数据。
        """
        self._reset()
        for stock in self.pool:
            df = self.get_data(stock_code=stock, start=self.from_date, end=self.end_date)
            self.data[stock] = df

    def get_data(self, stock_code: str, start='', end='') -> DataFrame:
        query_column = 'float_bonus,float_increase,float_dividend,xrdr_date,char_stock_code'
        if start or end:
            df = self.condition_select(self.table_name, query_column, f"char_stock_code='{stock_code}' AND (xrdr_date BETWEEN '{start}' AND '{end}')")
        else:
            df = self.select_values(self.table_name, query_column)
        if not df.empty:
            def_column = ['bonus', 'increase', 'dividend', 'xrdr_date', 'stock_code']
            df.columns = def_column
            df['xrdr_date'] = pd.to_datetime(df['xrdr_date'])
            df.set_index('xrdr_date', inplace=True)
        else:
            df = DataFrame()
        return df


    # API
    def get(self, query_date: pd.Timestamp) -> Tuple[XrdrEvent, XrdrEvent]:
        event_list = []
        for stock_code in self.pool:
            if not self.data[stock_code].empty:
                if query_date in self.data[stock_code].index:
                    self.dataline = self.data[stock_code].loc[query_date]
                    event_list.append(XrdrEvent(query_date, self.dataline))
        return event_list
