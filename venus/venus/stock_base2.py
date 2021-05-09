#!/usr/bin/python3
import datetime
import pandas as pd
from pandas import DataFrame
import re
import json
import numpy as np
import requests
import lxml.etree
from dev_global.env import TIME_FMT
from libmysql_utils.mysql8 import (mysqlBase, mysqlHeader, Json2Sql)
from requests.models import HTTPError
from venus.form import formStockManager
from venus.cninfo import spiderBase
from mars.utils import read_json


__version__ = '1.0.10'


class StockBase(mysqlBase):
    """
    param  header: mysqlHeader
    """
    def __init__(self, header: mysqlHeader) -> None:
        # if not isinstance(header, mysqlHeader):
        #    raise HeaderException("Error due to incorrect header.")
        super(StockBase, self).__init__(header)
        # date format: YYYY-mm-dd
        self._Today = datetime.date.today().strftime(TIME_FMT)
        # date format: YYYYmmdd
        self._today = datetime.date.today().strftime('%Y%m%d')
        # self.TAB_STOCK_MANAGER = "stock_manager"
        self.j2sql = Json2Sql(header)

    @property
    def Today(self) -> str:
        """
        Format: 1983-01-22
        """
        self._Today = datetime.date.today().strftime(TIME_FMT)
        return self._Today

    @property
    def today(self) -> str:
        """
        Format: 19830122
        """
        self._today = datetime.date.today().strftime('%Y%m%d')
        return self._today

    def get_all_stock_list(self) -> list:
        """
        Return stock code --> list.
        """
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='t').all()
        df = pd.DataFrame.from_dict(query_stock_code)
        stock_list = df['stock_code'].tolist()
        # should test if stock list is null
        return stock_list

    def get_all_index_list(self):
        """
        Return stock code --> list.
        """
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='i').all()
        df = pd.DataFrame.from_dict(query_stock_code)
        stock_list = df['stock_code'].tolist()
        return stock_list

    def get_all_security_list(self):
        """
        Return stock code --> list
        """
        # Return all kinds of securities in form stock list.
        # Result : List type data.
        query_stock_code = self.session.query(formStockManager.stock_code).all()
        df = pd.DataFrame.from_dict(query_stock_code)
        stock_list = df['stock_code'].tolist()
        return stock_list

    @staticmethod
    def get_html_object(url: str, HttpHeader=None):
        """
        result is a etree.HTML object
        """
        response = requests.get(url, HttpHeader=None, timeout=3)
        if response.status_code == 200:
            # setting encoding
            response.encoding = response.apparent_encoding
            html = lxml.etree.HTML(response.text)
        else:
            html = None
            raise HTTPError(f"Status code: {response.status_code} for {url}")
        return html

    @staticmethod
    def get_excel_object(url: str) -> pd.DataFrame:
        df = pd.read_excel(url)
        return df

    @staticmethod
    def set_date_as_index(df):
        df['date'] = pd.to_datetime(df['date'], format=TIME_FMT)
        df.set_index('date', inplace=True)
        # exception 1, date index not exists.
        # exception 2, date data is not the date format.
        return df

    @staticmethod
    def dataframe_data_translate(df: DataFrame) -> DataFrame:
        """
        Translate data format in dataframe to correct type.
        """
        for index in df.columns:
            try:
                if re.search('date', index):
                    df[index] = pd.to_datetime(df[index])
                elif re.search('int', index):
                    df[index] = pd.to_numeric(df[index])
                    df[index].replace(np.nan, 0, inplace=True)
                elif re.search('float', index):
                    df[index] = pd.to_numeric(df[index])
                    df[index].replace(np.nan, 0.0, inplace=True)
                elif re.search('char', index):
                    df[index].replace(np.nan, 'NULL', inplace=True)
            except Exception:
                pass
        return df

    @staticmethod
    def read_url(key, url_file):
        """
        It is a method base on read_json, returns a url.
        """
        _, url = read_json(key, url_file)
        return url

    def get_close_price(self, stock_code: str) -> DataFrame:
        df = self.select_values(stock_code, 'trade_date,close_price')
        if not df.empty:
            df.columns = ['trade_date, close_price']
            df.set_index('trade_date', inplace=True)
        return df


class HeaderException(BaseException):
    pass


class StockCodeList(object):
    """
    Generate stock code list.\n
    API:   @: get_stock()\n
           @: get_fund()\n
           @: get_
    """
    @staticmethod
    def _get_sh_stock():
        stock_list = [f"SH60{str(i).zfill(4)}" for i in range(4000)]
        return stock_list

    @staticmethod
    def _get_sz_stock():
        stock_list = [f"SZ{str(i).zfill(6)}" for i in range(1, 1000)]
        return stock_list

    @staticmethod
    def _get_cyb_stock():
        stock_list = [f"SZ300{str(i).zfill(3)}" for i in range(1, 1000)]
        return stock_list

    @staticmethod
    def _get_zxb_stock():
        stock_list = [f"SZ002{str(i).zfill(3)}" for i in range(1, 1000)]
        return stock_list

    @staticmethod
    def _get_b_stock():
        s1 = [f"SH900{str(i).zfill(3)}" for i in range(1, 1000)]
        s2 = [f"SZ200{str(i).zfill(3)}" for i in range(1, 1000)]
        stock_list = s1 + s2
        return stock_list

    @staticmethod
    def _get_index():
        index1 = [f"SH000{str(i).zfill(3)}" for i in range(1000)]
        index2 = [f"SH950{str(i).zfill(3)}" for i in range(1000)]
        index3 = [f"SZ399{str(i).zfill(3)}" for i in range(1000)]
        stock_list = index1 + index2 + index3
        return stock_list

    @staticmethod
    def _get_kcb_stock():
        stock_list = [f"SH688{str(i).zfill(3)}" for i in range(1000)]
        return stock_list

    @staticmethod
    def _get_xsb_stock():
        stock_list = [f"SH83{str(i).zfill(3)}" for i in range(1000)]
        return stock_list

    @staticmethod
    def get_stock():
        """
        @API function
        """
        stock_list = StockCodeList._get_sh_stock()
        stock_list += StockCodeList._get_sz_stock()
        stock_list += StockCodeList._get_cyb_stock()
        stock_list += StockCodeList._get_zxb_stock()
        stock_list += StockCodeList._get_kcb_stock()
        stock_list += StockCodeList._get_b_stock()
        stock_list += StockCodeList._get_index()
        return stock_list

    @staticmethod
    def _get_fund():
        pass


class StockList(spiderBase, StockBase):
    """
    A method base on class StockCodeList.
    """
    def __init__(self, header: mysqlHeader) -> None:
        spiderBase.__init__(self)
        StockBase.__init__(self, header)
        self.j2sql = Json2Sql(header)
        self.j2sql.load_table('stock_manager')

    def get_stock_list(self):
        url = 'http://www.cninfo.com.cn/new/data/szse_stock.json'
        result = requests.get(url, self.http_header)
        jr = json.loads(result.text)
        df = pd.DataFrame(jr['stockList'])
        df.drop(['category'], axis=1, inplace=True)
        df.columns = ['orgId', 'stock_code', 'short_code', 'stock_name']
        for index, row in df.iterrows():
            if re.match(r'^0|^3|^2', row['stock_code']):
                row['stock_code'] = 'SZ' + row['stock_code']
            elif re.match(r'^6|^9', row['stock_code']):
                row['stock_code'] = 'SH' + row['stock_code']
        return df

    def get_hk_stock_list(self):
        url = 'http://www.cninfo.com.cn/new/data/hke_stock.json'
        result = requests.get(url, self.http_header)
        jr = json.loads(result.text)
        df = pd.DataFrame(jr['stockList'])
        df.drop(['category'], axis=1, inplace=True)
        for index, row in df.iterrows():
            row['code'] = 'HK' + row['code']
        return df

    def get_fund_stock_list(self):
        url = 'http://www.cninfo.com.cn/new/data/fund_stock.json'
        result = requests.get(url, self.http_header)
        jr = json.loads(result.text)
        df = pd.DataFrame(jr['stockList'])
        df.drop(['category'], axis=1, inplace=True)
        for index, row in df.iterrows():
            row['code'] = 'F' + row['code']
        return df

    def get_bond_stock_list(self):
        url = 'http://www.cninfo.com.cn/new/data/bond_stock.json'
        result = requests.get(url, self.http_header)
        jr = json.loads(result.text)
        df = pd.DataFrame(jr['stockList'])
        df.drop(['category'], axis=1, inplace=True)
        for index, row in df.iterrows():
            row['code'] = 'R' + row['code']
        return df

    def insert_stock_manager(self, df: DataFrame):
        """
        API function
        """
        json_data = self.j2sql.dataframe_to_json(df, ['orgId', 'stock_code', 'short_code', 'stock_name'])
        for data in json_data:
            sql = self.j2sql.to_sql_insert(data)
            self.engine.execute(sql)

    @staticmethod
    def _get_sh_stock():
        stock_list = [f"SH60{str(i).zfill(4)}" for i in range(4000)]
        return stock_list

    @staticmethod
    def _get_sz_stock():
        stock_list = [f"SZ{str(i).zfill(6)}" for i in range(1, 1000)]
        return stock_list

    @staticmethod
    def _get_cyb_stock():
        stock_list = [f"SZ300{str(i).zfill(3)}" for i in range(1, 1000)]
        return stock_list

    @staticmethod
    def _get_zxb_stock():
        stock_list = [f"SZ002{str(i).zfill(3)}" for i in range(1, 1000)]
        return stock_list

    @staticmethod
    def _get_b_stock():
        s1 = [f"SH900{str(i).zfill(3)}" for i in range(1, 1000)]
        s2 = [f"SZ200{str(i).zfill(3)}" for i in range(1, 1000)]
        stock_list = s1 + s2
        return stock_list

    @staticmethod
    def _get_index():
        index1 = [f"SH000{str(i).zfill(3)}" for i in range(1000)]
        index2 = [f"SH950{str(i).zfill(3)}" for i in range(1000)]
        index3 = [f"SZ399{str(i).zfill(3)}" for i in range(1000)]
        stock_list = index1 + index2 + index3
        return stock_list

    @staticmethod
    def _get_kcb_stock():
        stock_list = [f"SH688{str(i).zfill(3)}" for i in range(1000)]
        return stock_list

    @staticmethod
    def _get_xsb_stock():
        stock_list = [f"SH83{str(i).zfill(3)}" for i in range(1000)]
        return stock_list

    @staticmethod
    def get_stock():
        """
        @API function
        """
        stock_list = StockCodeList._get_sh_stock()
        stock_list += StockCodeList._get_sz_stock()
        stock_list += StockCodeList._get_cyb_stock()
        stock_list += StockCodeList._get_zxb_stock()
        stock_list += StockCodeList._get_kcb_stock()
        stock_list += StockCodeList._get_b_stock()
        stock_list += StockCodeList._get_index()
        return stock_list

    @staticmethod
    def _get_fund():
        pass


# On Client
def resolve_stock_list(stock_type='stock'):
    """
    fetch full stock list.
    """
    if stock_type == 'stock':
        url = 'http://127.0.0.1:5000/stock'
        pat = re.compile(r"S[H|Z]\d{6}", re.I)
    elif stock_type == 'hk':
        url = 'http://127.0.0.1:5000/stocklist'
        pat = re.compile(r"HK\d+", re.I)
    elif stock_type == 'index':
        url = 'http://127.0.0.1:5000/index'
        pat = re.compile(r"HK\d+", re.I)
    else:
        # total stock code list unsorted.
        url = 'http://127.0.0.1:5000/totalstocklist'
        pat = re.compile(r"S[H|Z]\d{6}", re.I)
    response = requests.get(url)
    if response.status_code == 200:
        stock_list = pat.findall(response.text)
    else:
        stock_list = []
    return stock_list


if __name__ == "__main__":
    from libmysql_utils.mysql8 import GLOBAL_HEADER
    event = StockList(GLOBAL_HEADER)
    result = event.get_stock_list()
    event.insert_stock_manager(result)
