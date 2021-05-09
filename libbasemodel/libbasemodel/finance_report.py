#!/usr/bin/python3
from libmysql_utils.mysql8 import mysqlHeader
import numpy as np
import pandas as pd
import re
from libbasemodel.stock_model import StockBase, dataLine
from mars.utils import read_url
from dev_global.env import CONF_FILE
from mars.log_manager import log_with_return


class EventFinanceReport(StockBase):
    def update_balance(self, stock_code):
        # get url
        url = read_url("URL_balance", CONF_FILE)
        url = url.format(stock_code[2:])
        # get data
        df = self.get_balance_sheet(stock_code, url)
        if df is not None:
            if not df.empty:
                dataline = dataLine('balance_sheet')
                insert_sql_list = dataline.insert_sql(stock_code, df)
                for sql in insert_sql_list:
                    self.exec(sql)

    @log_with_return
    def get_balance_sheet(self, stock_code, url):
        """
        read csv data and return a dataframe object.
        """
        from libbasemodel.form import balance_column
        from mars.utils import data_clean
        # config file is a url file.
        # _, url = read_json('URL_163_MONEY', CONF_FILE)
        df = pd.read_csv(url, encoding='gb18030')
        if df is not None:
            if not df.empty:
                df = df.T
                # drop the last line
                result = df.iloc[1:, :]
                result = result.applymap(lambda x: 10000*float(x) if re.search(r'^-?[0-9\.,]+$', str(x)) else np.nan)
                for index, row in result.iterrows():
                    if not re.match(r'\d{4}-\d{2}-\d{2}', str(index)):
                        result.drop(index, axis=0, inplace=True)
                # result.columns = ['c'+str(i) for i in range(108)]
                result.columns = balance_column
                # result.loc[:, ('char_stock_code')] = stock_code
                result = data_clean(result)
            else:
                result = df
        else:
            result = pd.DataFrame()
        return result

    def update_cashflow(self, stock_code):
        # get url
        url = read_url("URL_cashflow", CONF_FILE)
        url = url.format(stock_code[2:])
        # get data
        df = self.get_cashflow(stock_code, url)
        if df is not None:
            if not df.empty:
                dataline = dataLine('cashflow')
                insert_sql_list = dataline.insert_sql(stock_code, df)
                for sql in insert_sql_list:
                    self.exec(sql)

    @log_with_return
    def get_cashflow(self, stock_code, url):
        """
        read csv data and return a dataframe object.
        """
        import re
        from libbasemodel.form import cashflow_column
        from mars.utils import data_clean
        # config file is a url file.
        # _, url = read_json('URL_163_MONEY', CONF_FILE)
        df = pd.read_csv(url, encoding='gb18030')
        if df is not None:
            if not df.empty:
                df = df.T
                # drop the last line
                result = df.iloc[1:, :]
            else:
                result = df
            result = result.applymap(lambda x: 10000*float(x) if re.search(r'^-?[0-9\.,]+$', str(x)) else np.nan)
            for index, row in result.iterrows():
                if not re.match(r'\d{4}-\d{2}-\d{2}', str(index)):
                    result.drop(index, axis=0, inplace=True)
            # result.columns = ['c'+str(i) for i in range(108)]
            result.columns = cashflow_column
            # result.loc[:, ('char_stock_code')] = stock_code
            result = data_clean(result)
        else:
            result = pd.DataFrame()
        return result

    def update_income(self, stock_code):
        # get url
        url = read_url("URL_income", CONF_FILE)
        url = url.format(stock_code[2:])
        # get data
        df = self.get_income(stock_code, url)
        if df is not None:
            if not df.empty:
                dataline = dataLine('income_statement')
                insert_sql_list = dataline.insert_sql(stock_code, df)
                for sql in insert_sql_list:
                    self.exec(sql)

    @log_with_return
    def get_income(self, stock_code, url):
        """
        read csv data and return a dataframe object.
        """
        import re
        from libbasemodel.form import income_column
        from mars.utils import data_clean
        # config file is a url file.
        # _, url = read_json('URL_163_MONEY', CONF_FILE)
        df = pd.read_csv(url, encoding='gb18030')
        if df is not None:
            if not df.empty:
                df = df.T
                # drop the last line
                result = df.iloc[1:, :]
            else:
                result = df
            result = result.applymap(lambda x: 10000*float(x) if re.search(r'^-?[0-9\.,]+$', str(x)) else np.nan)
            for index, row in result.iterrows():
                if not re.match(r'\d{4}-\d{2}-\d{2}', str(index)):
                    result.drop(index, axis=0, inplace=True)
            # result.columns = ['c'+str(i) for i in range(108)]
            result.columns = income_column
            # result.loc[:, ('char_stock_code')] = stock_code
            result = data_clean(result)
        else:
            result = pd.DataFrame()
        return result


if __name__ == "__main__":
    from libmysql_utils.mysql8 import mysqlHeader
    remote_head = mysqlHeader(acc="stock", pw="stock2020", host="115.159.1.221", db="stock")
    stock_code = 'SH600002'
    event = EventFinanceReport(remote_head)
    event.update_balance(stock_code)
    event.update_cashflow(stock_code)
    event.update_income(stock_code)
