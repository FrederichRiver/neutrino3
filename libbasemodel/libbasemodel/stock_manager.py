#!/usr/bin/python3
import os
import numpy as np
import pandas as pd
import requests
from datetime import timedelta
from pandas import DataFrame
from dev_global.var import stock_table_column, stock_table_column2
from dev_global.env import CONF_FILE
# from dev_global.var import stock_table_column
from mars.log_manager import log_with_return, log_wo_return
from mars.utils import read_url, drop_space
from .stock_model import StockBase
from .form import formStockManager


class EventTradeDataManager(StockBase):
    """
    It is a basic event, which fetch trade data and manage it.
    """
    def __init__(self, header):
        super(EventTradeDataManager, self).__init__(header)
        self.url = read_url('URL_163_MONEY', CONF_FILE)
        self.j2sql.load_table('template_stock')

    @staticmethod
    def net_ease_code(stock_code):
        """
        input: SH600000, return: 0600000\n;
        input: SZ000001, return: 1000001.
        """
        if isinstance(stock_code, str):
            if stock_code[:2] == 'SH':
                stock_code = '0' + stock_code[2:]
            elif stock_code[:2] == 'SZ':
                stock_code = '1' + stock_code[2:]
            else:
                stock_code = None
        else:
            stock_code = None
        return stock_code

    def url_netease(self, stock_code, start_date, end_date):
        query_code = self.net_ease_code(stock_code)
        netease_url = self.url.format(query_code, start_date, end_date)
        return netease_url

    def get_trade_data(self, stock_code, end_date, start_date='19901219') -> DataFrame:
        """
        read csv data and return dataframe type data.
        """
        # config file is a url file.
        url = self.url_netease(stock_code, start_date, end_date)
        df = DataFrame()
        df = pd.read_csv(url, names=stock_table_column, encoding='gb18030')
        return df

    def get_stock_name(self, stock_code):
        """
        Searching stock name from net ease.
        """
        result = self.get_trade_data(stock_code, self.today)
        if not result.empty:
            stock_name = drop_space(result.iloc[1, 2])
        else:
            stock_name = None
        return stock_code, stock_name

    def stock_exist(self, stock_code, end_date, start_date='19901219'):
        url = self.url_netease(stock_code, start_date, end_date)
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                return True
            else:
                return False
        except Exception:
            return False

    def check_stock(self, stock_code):
        """
        Check whether table <stock_code> exists.
        Used in record_stock()
        """
        result = self.session.query(formStockManager.stock_code).filter_by(stock_code=stock_code).first()
        return result

    @log_with_return
    def create_stock_table(self, stock_code):
        if self.create_table_from_table(stock_code, 'template_stock'):
            stock = formStockManager(stock_code=stock_code, create_date=self.Today)
            self.session.add(stock)
            self.session.commit()
            return 1
        else:
            return 0

    def _clean(self, df: pd.DataFrame):
        """
        Param: df is a DataFrame like data.
        """
        if 'stock_code' in df.columns:
            df.drop(['stock_code'], axis=1, inplace=True)
        df = df[1:].copy()
        df.replace('None', np.nan, inplace=True)
        df.dropna(axis=0, how='any', inplace=True)
        return df

    @log_wo_return
    def init_stock_data(self, stock_code):
        """
        used when first time download stock data.
        """
        df = self.get_trade_data(stock_code, self.today)
        df = self._clean(df)
        if not df.empty:
            df.to_sql(name=stock_code, con=self.engine, if_exists='append', index=False)
            query = self.session.query(
                formStockManager.stock_code,
                formStockManager.update_date
            ).filter_by(stock_code=stock_code)
            if query:
                query.update(
                        {"update_date": self.Today})
            self.session.commit()

    @log_wo_return
    def download_stock_data(self, stock_code):
        # fetch last update date.
        update = self.session.query(formStockManager.update_date).filter_by(stock_code=stock_code).first()
        if update[0]:
            tmp = update[0] + timedelta(days=1)
            # tmp = update[0]
            update_date = tmp.strftime('%Y%m%d')
        else:
            update_date = '19901219'
        # fetch trade data.
        df = self.get_trade_data(stock_code, self.today, start_date=update_date)
        if not df.empty:
            df = self._clean(df)
            df = df.sort_values(['trade_date'])
            df_json = self.j2sql.dataframe_to_json(df, keys=stock_table_column2)
            for data in df_json:
                sql = self.j2sql.to_sql_insert(data, table_name=stock_code)
                self.engine.execute(sql)

    @log_wo_return
    def get_trade_detail_data(self, stock_code, trade_date):
        # trade_date format: '20191118'
        DOWNLOAD_PATH = '/home/friederich/Downloads/stock_data/'
        code = self.net_ease_code(stock_code)
        url = read_url("URL_tick_data", CONF_FILE).format(
            trade_date[:4], trade_date, code)
        df = pd.read_excel(url)
        filename = os.path.join(DOWNLOAD_PATH, f"{stock_code}_{trade_date}.csv")
        if not df.empty:
            df.to_csv(filename, encoding='gb18030')

    def set_ipo_date(self, stock_code):
        query = self.select_values(stock_code, 'trade_date')
        ipo_date = pd.to_datetime(query[0])
        # ipo_date = datetime.date(1990,12,19)
        self.update_value(
            'stock_manager', 'ipo_date',
            f"'{ipo_date[0]}'", f"stock_code='{stock_code}'")
        return ipo_date[0]

    def get_ipo_date(self, stock_code):
        query = self.select_values(stock_code, 'trade_date')
        ipo_date = pd.to_datetime(query[0])
        return ipo_date[0]


if __name__ == "__main__":
    from libmysql_utils.mysql8 import mysqlHeader
    root = mysqlHeader('root', '6414939', 'stock')
    event = EventTradeDataManager(root)
    from .stock_model import resolve_stock_list
    stock_list = resolve_stock_list('stock')
    for stock_code in stock_list:
        print(stock_code)
        event.download_stock_data(stock_code)
