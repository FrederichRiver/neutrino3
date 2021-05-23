#!/usr/bin/python3
import datetime
from libutils.network import RandomHeader
from libutils.log import Log, method
from libutils.utils import trans
import pandas as pd
import re
import json
import numpy as np
import requests
from lxml import etree
from dev_global.env import TIME_FMT
from libmysql_utils.mysql8 import (mysqlBase, mysqlHeader, Json2Sql)
from pandas import DataFrame
from requests.models import HTTPError
from libbasemodel.form import formStockManager
from libbasemodel.cninfo import cninfoSpider


"""
Public method:
> class StockBase
> class StockCodeList
> class StockList
"""


class eastmoneySpider(object):
    def __init__(self) -> None:
        self.http_header = {
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate",
            # "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            # "Cache-Control": "max-age=0",
            # "Connection": "keep-alive",
            # "Cookie": "intellpositionL=583.188px; qgqp_b_id=c296d37f90f4c939cacc16224744f41a; em_hq_fls=js; intellpositionT=1091px; waptgshowtime=202139; HAList=a-sz-300059-%u4E1C%u65B9%u8D22%u5BCC%2Ca-sh-603776-%u6C38%u5B89%u884C%2Ca-sz-300227-%u5149%u97F5%u8FBE%2Ca-sh-603929-%u4E9A%u7FD4%u96C6%u6210%2Ca-sz-300604-%u957F%u5DDD%u79D1%u6280%2Ca-sz-002245-%u6FB3%u6D0B%u987A%u660C; st_si=80758845330570; st_asi=delete; st_pvi=99506938076002; st_sp=2020-07-19%2022%3A28%3A41; st_inirUrl=https%3A%2F%2Fwww.eastmoney.com%2F; st_sn=15; st_psi=20210309233831816-111000300841-6472437881",
            # "Host": "quote.eastmoney.com",
            # "If-Modified-Since": "Wed, 10 Mar 2021 00:42:17 GMT",
            # "If-None-Match": 'W/"e87c88912663d51:0"',
            # "Referer": "https://www.baidu.com/s?wd=%E7%BE%8E%E8%82%A1%E5%88%97%E8%A1%A8",
            # "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36"
            }


class StockBase(mysqlBase):
    """
    param  header: mysqlHeader\n
    API:\n

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
        self._Header = RandomHeader()

    @property
    def httpHeader(self) -> dict:
        return self._Header()

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
        Query stock code from database.
        Return stock code --> list.
        """
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='t').all()
        df = pd.DataFrame.from_dict(query_stock_code)
        df.columns = ['stock_code']
        stock_list = df['stock_code'].tolist()
        # should test if stock list is null
        return stock_list

    def get_all_index_list(self) -> list:
        """
        Return stock code --> list.
        """
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='i').all()
        df = pd.DataFrame.from_dict(query_stock_code)
        df.columns = ['stock_code']
        stock_list = df['stock_code'].tolist()
        return stock_list

    def get_all_security_list(self) -> list:
        """
        Return stock code --> list
        """
        # Return all kinds of securities in form stock list.
        # Result : List type data.
        query_stock_code = self.session.query(formStockManager.stock_code).all()
        df = pd.DataFrame.from_dict(query_stock_code)
        df.columns = ['stock_code']
        stock_list = df['stock_code'].tolist()
        return stock_list

    @staticmethod
    def get_html_object(url: str, HttpHeader: dict) -> etree.HTML:
        """
        result is a etree.HTML object
        """
        response = requests.get(url, headers=HttpHeader, timeout=3)
        if response.status_code == 200:
            # setting encoding
            response.encoding = response.apparent_encoding
            html = etree.HTML(response.text)
        elif response.status_code == 304:
            html = None
        else:
            html = None
            raise HTTPError(f"Status code: {response.status_code} for {url}")
        return html

    @staticmethod
    def get_excel_object(url: str) -> DataFrame:
        df = pd.read_excel(url)
        return df

    @staticmethod
    def set_date_as_index(df: DataFrame) -> DataFrame:
        """
        Input must be DataFrame type and must have a column named 'date'.\n
        This is a INPLACE operation.
        """
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
    This is a base method use for generate stock code list.\n
    API:\n
    @: get_stock()\n
    @: get_index()
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
    def get_index():
        """
        @API function
        """
        stock_list = StockCodeList._get_index()
        return stock_list

    @staticmethod
    def _get_fund():
        pass


class StockList(cninfoSpider, StockBase):
    """
    基于cninfo网站爬虫获取股票列表。
    API: \n
    > get_stock() : 获取所有股票代码\n
    > get_stock_list : 获取所有股票代码，从上证网站上获取。\n
    > get_hk_stock_list : 获取所有港股代码。\n
    > get_fund_stock_list : 获取基金代码。\n
    > get_bond_stock_list : 获取债券代码。\n
    """
    def __init__(self, header: mysqlHeader) -> None:
        cninfoSpider.__init__(self)
        StockBase.__init__(self, header)
        self.j2sql = Json2Sql(header)
        self.j2sql.load_table('stock_manager')

    def _get_stock_list_data(self, url: str) -> DataFrame:
        # result -> http.response
        result = requests.get(url, self.http_header)
        # jr -> json like data
        jr = json.loads(result.text)
        df = pd.DataFrame(jr['stockList'])
        df.drop(['category'], axis=1, inplace=True)
        df.columns = ['orgId', 'stock_code', 'short_code', 'stock_name']
        return df

    def get_stock_list(self, url: str) -> DataFrame:
        """
        Get stock list from url: 'http://www.cninfo.com.cn/new/data/szse_stock.json'
        """
        df = self._get_stock_list_data(url)
        for _, row in df.iterrows():
            if re.match(r'^0|^3|^2', row['stock_code']):
                row['stock_code'] = 'SZ' + row['stock_code']
            elif re.match(r'^6|^9', row['stock_code']):
                row['stock_code'] = 'SH' + row['stock_code']
        return df

    def get_hk_stock_list(self, url: str) -> DataFrame:
        """
        Get stock list from url: 'http://www.cninfo.com.cn/new/data/hke_stock.json'
        """
        df = self._get_stock_list_data(url)
        for _, row in df.iterrows():
            row['code'] = 'HK' + row['code']
        return df

    def get_fund_stock_list(self, url: str) -> DataFrame:
        # url = 'http://www.cninfo.com.cn/new/data/fund_stock.json'
        df = self._get_stock_list_data(url)
        for _, row in df.iterrows():
            row['code'] = 'F' + row['code']
        return df

    def get_bond_stock_list(self, url: str) -> DataFrame:
        # url = 'http://www.cninfo.com.cn/new/data/bond_stock.json'
        df = self._get_stock_list_data(url)
        for _, row in df.iterrows():
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


class USStockList(eastmoneySpider, StockBase):
    def __init__(self, header: mysqlHeader) -> None:
        eastmoneySpider.__init__(self)
        StockBase.__init__(self, header)

    def get_us_stock_list(self):
        url = "http://quote.eastmoney.com/usstocklist.html"
        html = self.get_html_object(url, self.http_header)
        lines = html.xpath("//div[@id='quotesearch']/ul/li/a/text()")
        us_stock_list = self.resolve_us_stock_list(lines)
        return us_stock_list

    @method
    @Log
    def resolve_us_stock_list(self, stock_code):
        stock_list = []
        for stock in stock_code:
            # print(stock)
            x = re.match(r'([a-zA-Z0-9\u4e00-\u9fa5\.]+)\(([A-Z]+)\)', stock)
            if x:
                if x.group(2):
                    stock_list.append(x.group(2))
        return stock_list

    @method
    @Log
    def record_us_stock(self, stock_code):
        self.insert('us_stock_manager', {"stock_code": f"'{stock_code}'"})


class StockData(StockBase):
    def get_stock_data(self, stock_code: str, length=80) -> DataFrame:
        """
        Return stock data in DataFrame format.
        """
        df = self.select_values(
            stock_code,
            'trade_date,open_price,close_price,high_price,low_price,volume')
        # data cleaning
        df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']
        df['Date'] = pd.to_datetime(df['Date'], format=TIME_FMT)
        df.set_index('Date', inplace=True)
        df = df[-length:].copy()
        return df


class FinanceData(StockBase):
    def get_stock_data(self, stock_code: str, length=80) -> DataFrame:
        """
        Return stock data in DataFrame format.
        """
        df = self.select_values(
            stock_code,
            'trade_date,open_price,close_price,high_price,low_price,volume')
        # data cleaning
        df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']
        df['Date'] = pd.to_datetime(df['Date'], format=TIME_FMT)
        df.set_index('Date', inplace=True)
        df = df[-length:].copy()
        return df

    def get_shibor_data(self, length=60) -> DataFrame:
        df = self.select_values(
            "shibor", 'release_date,one_week')
        # data cleaning
        df.columns = ['Date', 'one_week']
        df['Date'] = pd.to_datetime(df['Date'], format=TIME_FMT)
        df.set_index('Date', inplace=True)
        df.dropna(axis=0, how='any', inplace=True)
        df = df[-length:].copy()
        return df


class dataLine(object):
    def __init__(self, table_name):
        # self.data = df
        self.table_name = table_name

    @method
    @Log
    def insert_sql(self, stock_code, df):
        """
        Result: Return a list of sql.
        """
        sql = f"INSERT IGNORE into {self.table_name} ("
        sql += 'char_stock_code,report_date,'
        sql += ','.join(df.columns)
        sql += ") VALUES ({})"
        value = []
        result = []
        for index, row in df.iterrows():
            value = [f"'{stock_code}'", f"'{index}'"]
            for col in df.columns:
                value.append(trans(row[col]))
            result_sql = sql.format(','.join(value))
            result.append(result_sql)
        return result

    @method
    @Log
    def update_sql(self, df, primary_key):
        """
        Result: Return a list of sql.
        """
        value_list = ''
        condition = ''
        sql = f"UPDATE {self.table_name} set "
        sql += "{} WHERE {}"
        value = []
        result = []
        for index, row in df.iterrows():
            value = []
            for label in df.columns:
                v = label + '=' + trans(row[label])
                value.append(v)
            value_list = ','.join(value)
            condition = (
                f"({primary_key[0]}={trans(row[primary_key[0]])},"
                f"{primary_key[1]}={trans(row[primary_key[1]])})")
            result_sql = sql.format(value_list, condition)
            result.append(result_sql)
        return result


# On Client
def resolve_stock_list(stock_type='stock'):
    """
    Use Flask service to get full stock list.
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
    from libmysql_utils.mysql8 import LOCAL_HEADER
    event = USStockList(LOCAL_HEADER)
    # text = ['安捷伦(A)', '美国铝业(AA)', 'Alcoa...(AA_)', 'Alcoa...(AA.)', 'Alcoa...(AA_B)', 'Alcoa...(AA.B)', 'Advan...(AAAP)', 'Perth...(AAAU)', '雅虎(AABA)', 'AACHo...(AAC)']
    result = event.get_us_stock_list()
    # result = event.resolve_us_stock_list(text)
    for stock_code in result:
        print(stock_code)
        event.record_us_stock(stock_code)
