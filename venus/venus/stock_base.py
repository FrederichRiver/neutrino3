#!/usr/bin/python3
import datetime
import pandas as pd
import re
import requests
import lxml
from lxml import etree
from dev_global.env import TIME_FMT
from libmysql_utils.mysql8 import (mysqlBase, mysqlHeader)
from mars.utils import trans
from mars.log_manager import error_log
from requests.models import HTTPError
from venus.form import formStockManager


__version__ = '1.0.10'


class StockBase(mysqlBase):
    """
    param  header: mysqlHeader
    """
    def __init__(self, header):
        if not isinstance(header, mysqlHeader):
            raise HeaderException("Error due to incorrect header.")
        super(StockBase, self).__init__(header)
        # date format: YYYY-mm-dd
        self._Today = datetime.date.today().strftime(TIME_FMT)
        # date format: YYYYmmdd
        self.today = datetime.date.today().strftime('%Y%m%d')
        # self.TAB_STOCK_MANAGER = "stock_manager"

    @property
    def Today(self) -> str:
        self._Today = datetime.date.today().strftime(TIME_FMT)
        return self._Today

    def get_all_stock_list(self) -> list:
        """
        Return stock code --> list.
        """
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='t')
        df = pd.DataFrame.from_dict(query_stock_code)
        stock_list = df['stock_code'].tolist()
        # should test if stock list is null
        return stock_list

    def get_all_index_list(self):
        """
        Return stock code --> list.
        """
        query_stock_code = self.session.query(formStockManager.stock_code).filter_by(flag='i')
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


class HeaderException(BaseException):
    pass


class StockEventBase(object):
    """
    Today: date format like yyyy-mm-dd \n
    today: date format like yyyymmdd
    """
    def __init__(self, header):
        self.Today = datetime.date.today().strftime(TIME_FMT)
        self.today = datetime.date.today().strftime('%Y%m%d')
        if not header:
            raise Exception
        self.mysql = mysqlBase(header)
        self.stock_list = []
        self.coder = StockCodeFormat()

    def __str__(self):
        return "<Stock Event Base>"

    def data_clean(self, df):
        for index, col in df.iteritems():
            try:
                if re.search('date', index):
                    df[index] = pd.to_datetime(df[index])
                elif re.search('int', index):
                    df[index] = pd.to_numeric(df[index])
                elif re.search('float', index):
                    df[index] = pd.to_numeric(df[index])
                elif re.search('char', index):
                    pass
                else:
                    pass
            except Exception:
                error_log(
                    f"Error while record interest of {col['char_stock_code']}")
        return df

    def update_date_time(self):
        """
        Get date of today.
        """
        self.Today = datetime.date.today().strftime(TIME_FMT)

    def get_all_stock_list(self):
        """
        Return stock code --> list.
        """
        query = self.mysql.condition_select(
            "stock_manager", "stock_code", "flag='t'"
        )
        df = pd.DataFrame.from_dict(query)
        self.stock_list = df['stock_code'].tolist()
        return self.stock_list

    def get_all_index_list(self):
        """
        Return stock code --> list.
        """
        query = self.mysql.condition_select(
            "stock_manager", "stock_code", "flag='i'"
        )
        df = pd.DataFrame.from_dict(query)
        self.stock_list = df['stock_code'].tolist()
        return self.stock_list

    def get_all_security_list(self):
        """
        Return stock code --> list
        """
        # Return all kinds of securities in form stock list.
        # Result : List type data.
        from venus.form import formStockManager
        result = self.mysql.session.query(
            formStockManager.stock_code).all()
        df = pd.DataFrame.from_dict(result)
        result = df['stock_code'].tolist()
        return result

    def get_html_object(self, url, header=None):
        """
        result is a etree.HTML object
        """
        content = requests.get(url, headers=None, timeout=3)
        content.encoding = content.apparent_encoding
        html = etree.HTML(content.text)
        return html

    def get_excel_object(self, url):
        df = pd.read_excel(url)
        return df

    def get_html_table(self, url, attr=''):
        # get html table from url.
        # Return a string like table object.
        # attr: [@class='table_bg001 border_box limit_scale scr_table']
        # //table[contains(@id,'historyTable')]
        html = self.get_html_object(url)
        table_list = html.xpath(f"//table{attr}")
        result = []
        if table_list:
            for table in table_list:
                df = etree.tostring(table).decode()
                result.append(df)
        return result

    def update_stock_manager(self, stock_code: str, option='update'):
        if option == 'update':
            col = 'modified_date'
        elif option == 'xrdr':
            col = 'xrdr_date'
        elif option == 'balance':
            col = 'balance_date'
        elif option == 'income':
            col = 'income_date'
        elif option == 'cashflow':
            col = 'cashflow_date'
        else:
            col = None
        if col:
            self.mysql.update_value(
                'stock_manager', col,
                f"'{self.Today}'", f"stock_code='{stock_code}'")

    def close(self):
        self.mysql.engine.close()


class EventStockList(StockEventBase):
    def get_all_stock_list(self):
        """
        Return stock code --> list.
        """
        query = self.mysql.condition_select(
            "stock_manager", "stock_code", "flag='t'"
        )
        df = pd.DataFrame.from_dict(query)
        self.stock_list = df[0].tolist()
        return self.stock_list

    def get_all_index_list(self):
        """
        Return stock code --> list.
        """
        query = self.mysql.condition_select(
            "stock_manager", "stock_code", "flag='i'"
        )
        df = pd.DataFrame.from_dict(query)
        self.stock_list = df[0].tolist()
        return self.stock_list

    def get_all_security_list(self):
        """
        Return stock code --> list
        """
        # Return all kinds of securities in form stock list.
        # Result : List type data.
        from venus.form import formStockManager
        result = self.mysql.session.query(
            formStockManager.stock_code).all()
        df = pd.DataFrame.from_dict(result)
        result = df['stock_code'].tolist()
        return result


class StockCodeFormat(object):
    def __call__(self, stock_code):
        if isinstance(stock_code, str):
            # format <SH600000> or <SZ000001>
            stock_code = stock_code.upper()
            if result := re.match(r'(\d{6}).([A-Z][A-Z])\Z', stock_code):
                # format <600000.SH> or <000001.SZ>
                stock_code = result.group(2)+result.group(1)
            elif re.match(r'[A-Z][A-Z]\d{6}', stock_code):
                # format <SH600000> or <SZ000001>
                pass
            else:
                stock_code = None
            return stock_code

    def net_ease_code(self, stock_code):
        """
        input: SH600000, return: 0600000\n;
        input: SZ000001, return: 1000001.
        """
        stock_code = self.__call__(stock_code)
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


class StockCodeList(object):
    """
    Generate stock code list.
    API:
    1. get_stock()
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


class dataLine(object):
    def __init__(self, table_name):
        # self.data = df
        self.table_name = table_name

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


if __name__ == "__main__":
    from polaris.mysql8 import GLOBAL_HEADER
    event = StockBase(GLOBAL_HEADER)
    result = event.get_all_stock_list()
