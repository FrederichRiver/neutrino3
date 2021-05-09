#!/usr/bin/python3
import numpy as np
import pandas as pd
from libbasemode.stock_model import StockBase, dataLine
from mars.utils import read_url
from dev_global.env import CONF_FILE


class EventFinanceReport(StockBase):
    def update_balance(self, stock_code):
        # get url
        url = read_url("URL_balance", CONF_FILE)
        url = url.format(stock_code[2:])
        # get data
        df = self.get_balance_sheet(stock_code, url)
        if not df.empty:
            dataline = dataLine('balance_sheet')
            try:
                insert_sql_list = dataline.insert_sql(stock_code, df)
                for sql in insert_sql_list:
                    self.mysql.engine.execute(sql)
            except Exception as e:
                print(e)

    def get_balance_sheet(self, stock_code, url):
        """
        read csv data and return a dataframe object.
        """
        import re
        from libbasemodel.form import balance_column
        from mars.utils import data_clean
        # config file is a url file.
        # _, url = read_json('URL_163_MONEY', CONF_FILE)
        df = pd.read_csv(url, encoding='gb18030')
        if not df.empty:
            df = df.T
            # drop the last line
            result = df.iloc[1:,:]
        else:
            result = df
        result = result.applymap(lambda x: 10000*float(x) if re.search(r'^-?[0-9\.,]+$', str(x)) else np.nan)
        for index,row in result.iterrows():
            if not re.match(r'\d{4}-\d{2}-\d{2}', str(index)):
                result.drop(index, axis=0, inplace=True)
        # result.columns = ['c'+str(i) for i in range(108)]
        result.columns = balance_column
        # result.loc[:, ('char_stock_code')] = stock_code
        result = data_clean(result)
        return result

    def update_cashflow(self, stock_code):
        # get url
        url = read_url("URL_cashflow", CONF_FILE)
        url = url.format(stock_code[2:])
        # get data
        df = self.get_cashflow(stock_code, url)
        if not df.empty:
            dataline = dataLine('cashflow')
            try:
                insert_sql_list = dataline.insert_sql(stock_code, df)
                for sql in insert_sql_list:
                    self.mysql.engine.execute(sql)
            except Exception as e:
                print(e)


    def get_cashflow(self, stock_code, url):
        """
        read csv data and return a dataframe object.
        """
        import re
        from venus.form import cashflow_column
        from mars.utils import data_clean
        # config file is a url file.
        # _, url = read_json('URL_163_MONEY', CONF_FILE)
        df = pd.read_csv(url, encoding='gb18030')
        if not df.empty:
            df = df.T
            # drop the last line
            result = df.iloc[1:,:]
        else:
            result = df
        result = result.applymap(lambda x: 10000*float(x) if re.search(r'^-?[0-9\.,]+$', str(x)) else np.nan)
        for index,row in result.iterrows():
            if not re.match(r'\d{4}-\d{2}-\d{2}', str(index)):
                result.drop(index, axis=0, inplace=True)
        # result.columns = ['c'+str(i) for i in range(108)]
        result.columns = cashflow_column
        # result.loc[:, ('char_stock_code')] = stock_code
        result = data_clean(result)
        return result

    def update_income(self, stock_code):
        # get url
        url = read_url("URL_income", CONF_FILE)
        url = url.format(stock_code[2:])
        # get data
        df = self.get_income(stock_code, url)
        if not df.empty:
            dataline = dataLine('income_statement')
            try:
                insert_sql_list = dataline.insert_sql(stock_code, df)
                for sql in insert_sql_list:
                    self.mysql.engine.execute(sql)
            except Exception as e:
                print(e)
        

    def get_income(self, stock_code, url):
        """
        read csv data and return a dataframe object.
        """
        import re
        from venus.form import income_column
        from mars.utils import data_clean
        # config file is a url file.
        # _, url = read_json('URL_163_MONEY', CONF_FILE)
        df = pd.read_csv(url, encoding='gb18030')
        if not df.empty:
            df = df.T
            # drop the last line
            result = df.iloc[1:,:]
        else:
            result = df
        result = result.applymap(lambda x: 10000*float(x) if re.search(r'^-?[0-9\.,]+$', str(x)) else np.nan)
        for index,row in result.iterrows():
            if not re.match(r'\d{4}-\d{2}-\d{2}', str(index)):
                result.drop(index, axis=0, inplace=True)
        # result.columns = ['c'+str(i) for i in range(108)]
        result.columns = income_column
        # result.loc[:, ('char_stock_code')] = stock_code
        result = data_clean(result)
        return result

def db_init():
    from dev_global.env import GLOBAL_HEADER
    from mars.utils import ERROR
    from polaris.mysql8 import create_table, mysqlBase, mysqlHeader
    from venus.form import formTemplate, formFinanceTemplate, formInfomation
    try:
        root_header = mysqlHeader('root', '6414939', 'stock')
        mysql = mysqlBase(root_header)
        create_table(formFinanceTemplate, mysql.engine)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    from dev_global.env import GLOBAL_HEADER
    stock_code = 'SZ300810'
    event = EventFinanceReport(GLOBAL_HEADER)
    event.update_balance(stock_code)
    event.update_cashflow(stock_code)
    event.update_income(stock_code)
