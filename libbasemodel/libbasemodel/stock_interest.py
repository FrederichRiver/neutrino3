#!/usr/bin/python38
from libutils.log import Log, method
import numpy as np
import pandas as pd
from pandas import DataFrame
from dev_global.var import stock_interest_column
from dev_global.path import CONF_FILE
from libmysql_utils.mysql8 import mysqlHeader
from libbasemodel.stock_model import StockBase
from libutils.utils import read_url

__version__ = '1.2.4'


class EventInterest(StockBase):
    """
    """
    def __init__(self, header):
        super(EventInterest, self).__init__(header)
        self.df = DataFrame()

    def _load_template(self):
        """
        return 1 means success.\n
        """
        self.j2sql.table_def = self.j2sql.load_table('stock_interest')
        return 1

    def create_interest_table(self):
        """
        Initial interest table.
        """
        from libmysql_utils.orm.form import formInterest
        self.create_table_from_table("stock_interest", formInterest.__tablename__)

    def resolve_interest_table(self, stock_code: str):
        """
        Recognize interest table from html,
        returns a dataframe table.\n
        Used for batch insert.
        """
        url = read_url('URL_fh_163', CONF_FILE)
        url = url.format(stock_code[2:])
        # result is a list of DataFrame table.
        result = pd.read_html(url, attrs={'class': 'table_bg001 border_box limit_sale'})
        if result:
            df = result[0]
            df.columns = [
                'report_date', 'int_year', 'float_bonus',
                'float_increase', 'float_dividend',
                'record_date', 'xrdr_date', 'share_date']
            df['char_stock_code'] = stock_code
            df.replace('--', np.nan, inplace=True)
            # change column type according to their pre_fix.
            result = self.dataframe_data_translate(df)
        else:
            result = DataFrame()
        return result

    @method
    @Log
    def record_interest(self, stock_code: str) -> None:
        df = self.resolve_interest_table(stock_code)
        json_data = self.j2sql.dataframe_to_json(df, stock_interest_column)
        for data in json_data:
            # print(data)
            sql = self.j2sql.to_sql_insert(data, 'stock_interest')
            self.engine.execute(sql)


class EventStockData(StockBase):
    def __init__(self, header: mysqlHeader) -> None:
        super(EventStockData, self).__init__(header)

    def set_ipo_date(self, stock_code):
        """
        Fetch the first date of stock and set it as ipo date.
        """
        query = self.select_values(stock_code, 'trade_date')
        ipo_date = pd.to_datetime(query[0])
        # ipo_date = datetime.date(1990,12,19)
        self.update_value('stock_manager', 'ipo_date', f"'{ipo_date[0]}'", f"stock_code='{stock_code}'")
        return ipo_date[0]

    def get_ipo_date(self, stock_code):
        query = self.select_values(stock_code, 'trade_date')
        ipo_date = pd.to_datetime(query[0])
        return ipo_date[0]

    def adjust_factor(self, stock_code: str):
        # fetch close price data.
        df_stock = self.select_values(stock_code, 'trade_date,close_price,prev_close_price')
        df_interest = self.condition_select('stock_interest', 'float_bonus,float_increase,float_dividend,xrdr_date', f"char_stock_code='{stock_code}'")
        if not df_interest.empty:
            df_stock.columns = ['trade_date', 'close_price', 'prev_close_price']
            df_stock.set_index('trade_date', inplace=True)
            # fetch bonus data.
            df_interest.columns = ['bonus', 'increase', 'dividend', 'trade_date']
            df_interest.set_index('trade_date', inplace=True)
            df = pd.concat([df_stock, df_interest], axis=1)
            df['bonus'] = df['bonus'].apply(lambda x: 0 if pd.isna(x) else x)
            df['increase'] = df['increase'].apply(lambda x: 0 if pd.isna(x) else x)
            df['dividend'] = df['dividend'].apply(lambda x: 0 if pd.isna(x) else x)
            # factor calculation
            df['prev'] = df['close_price'].shift(1)
            df['factor'] = 1.0
            for index, row in df.iterrows():
                if (row['dividend'] + row['increase'] + row['bonus']) > 0:
                    tmp = adjust_factor(row['prev'], row['dividend'],  row['bonus'], row['increase'])
                    df.loc[index, 'factor'] = row['prev'] / tmp
            df['adjust_factor'] = 1.0
            cum_factor = 1.0
            for index, row in df.iterrows():
                cum_factor *= row['factor']
                df.loc[index, 'adjust_factor'] = cum_factor
            df['adjust_price'] = df['close_price'] * df['adjust_factor']
        else:
            df = df_stock
            df['adjust_factor'] = 1.0
        result = DataFrame(df, columns=['adjust_factor'], index=df.index)
        # result['trade_date'] = df.index
        return result

    @method
    @Log
    def record_factor(self, stock_code, df):
        self.j2sql.load_table(stock_code)
        tmp_df = self.j2sql.dataframe_to_json(df, keys=['adjust_factor', 'trade_date'])
        for data in tmp_df:
            sql = self.j2sql.to_sql_update(data, keys=['trade_date'])
            self.engine.execute(sql)


def adjust_factor(x, div, b, i):
    result = (x - div/10) / (1 + b/10 + i/10)
    # result = x / (1 + b/10 + i/10)
    return result


if __name__ == "__main__":
    pass