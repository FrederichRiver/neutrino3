#!/usr/bin/python3
import pandas as pd
import numpy as np
from dev_global.env import CONF_FILE
from mars.utils import read_url, drop_space
from venus.stock_base import StockEventBase
from sqlalchemy.types import Date, DECIMAL, Integer, NVARCHAR
from venus.form import formStockManager
from mars.log_manager import info_log, log_decorator


class EventTradeDataManager(StockEventBase):
    """
    It is a basic event, which fetch trade data and manage it.
    """
    # def __init__(self):
    #    super(StockEventBase, self).__init__()
    def url_netease(self, stock_code, start_date, end_date):
        url = read_url('URL_163_MONEY', CONF_FILE)
        query_code = self.coder.net_ease_code(stock_code)
        netease_url = url.format(query_code, start_date, end_date)
        return netease_url

    def get_trade_data(self, stock_code, end_date, start_date='19901219'):
        """
        read csv data and return dataframe type data.
        """
        # config file is a url file.
        url = self.url_netease(stock_code, start_date, end_date)
        result = pd.read_csv(url, encoding='gb18030')
        return result

    def get_stock_name(self, stock_code):
        """
        Searching stock name from net ease.
        """
        stock_name = None
        result = self.get_trade_data(stock_code, self.today)
        if not result.empty:
            stock_name = drop_space(result.iloc[1, 2])
        return stock_code, stock_name

    @log_decorator
    def record_stock(self, stock_code):
        """
        Record table <stock_code> into database.
        """
        result = self.check_stock(stock_code)
        # if table exists, result = (stock_code,)
        # else result = (,)
        if not result:
            self.create_stock_table(stock_code)
            self.init_stock_data(stock_code)

    def check_stock(self, stock_code):
        """
        Check whether table <stock_code> exists.
        """
        result = self.mysql.select_one(
            'stock_manager', 'stock_code', f"stock_code='{stock_code}'")
        return result

    def create_stock_table(self, stock_code):
        _, stock_name = self.get_stock_name(stock_code)
        if stock_name:
            sql = (
                f"Insert into stock_manager set "
                f"stock_code='{stock_code}',"
                f"stock_name='{stock_name}',"
                f"create_date='{self.Today}'"
            )
            self.mysql.engine.execute(sql)
            self.mysql.create_table_from_table(
                stock_code, 'template_stock')
            info_log(f"Create table {stock_code}.")

    def data_cleaning(self, df):
        """
        Param: df is a DataFrame like data.
        """
        df.drop(['stock_code'], axis=1, inplace=True)
        df.replace('None', np.nan, inplace=True)
        df = df.dropna(axis=0, how='any')
        return df

    def init_stock_data(self, stock_code):
        """
        used when first time download stock data.
        """
        result = self.get_trade_data(stock_code, self.today)
        result.columns = ['trade_date', 'stock_code',
                          'stock_name', 'close_price',
                          'highest_price', 'lowest_price',
                          'open_price', 'prev_close_price',
                          'change_rate', 'amplitude',
                          'volume', 'turnover']
        result = self.data_cleaning(result)
        columetype = {
            'trade_date': Date,
            'stock_name': NVARCHAR(length=10),
            'close_price': DECIMAL(7, 3),
            'highest_price': DECIMAL(7, 3),
            'lowest_price': DECIMAL(7, 3),
            'open_price': DECIMAL(7, 3),
            'prev_close_price': DECIMAL(7, 3),
            'change_rate': DECIMAL(7, 3),
            'amplitude': DECIMAL(7, 4),
            'volume': Integer(),
            'turnover': DECIMAL(20, 2)
        }
        result.to_sql(
            name=stock_code,
            con=self.mysql.engine,
            if_exists='append',
            index=False,
            dtype=columetype)
        query = self.mysql.session.query(
                formStockManager.stock_code,
                formStockManager.update_date
            ).filter_by(stock_code=stock_code)
        if query:
            query.update(
                    {"update_date": self.Today})
        self.mysql.session.commit()

    def download_stock_data(self, stock_code):
        query_result = self.mysql.select_one(
            'stock_manager', 'update_date', f"stock_code='{stock_code}'"
        )
        if query_result[0]:
            update = query_result[0].strftime('%Y%m%d')
        else:
            update = '19901219'
        result = self.get_trade_data(
            stock_code, self.today, start_date=update)
        result.columns = ['trade_date', 'stock_code',
                          'stock_name', 'close_price',
                          'highest_price', 'lowest_price',
                          'open_price', 'prev_close_price',
                          'change_rate', 'amplitude',
                          'volume', 'turnover']
        result = self.data_cleaning(result)
        result = result.sort_values('trade_date')
        for index, row in result.iterrows():
            insert_sql = (
                    f"INSERT IGNORE into {stock_code} "
                    "(trade_date,stock_name,close_price,"
                    "highest_price,lowest_price,open_price,prev_close_price,"
                    "change_rate,amplitude,volume,turnover)"
                    f"VALUES('{row['trade_date']}','{row['stock_name']}',"
                    f"{row['close_price']},{row['highest_price']},"
                    f"{row['lowest_price']},{row['open_price']},"
                    f"{row['prev_close_price']},{row['change_rate']},"
                    f"{row['amplitude']},{row['volume']},{row['turnover']})"
                    )
            self.mysql.engine.execute(insert_sql)
            update_sql = (
                    f"UPDATE stock_manager "
                    f"set update_date='{row['trade_date']}' "
                    f"Where stock_code='{stock_code}'")
            self.mysql.engine.execute(update_sql)

    def get_trade_detail_data(self, stock_code, trade_date):
        # trade_date format: '20191118'
        root_path = '/root/download/'
        code = self.coder.net_ease_code(stock_code)
        url = read_url("URL_tick_data", CONF_FILE).format(
            trade_date[:4], trade_date, code)
        df = pd.read_excel(url)
        filename = absolute_path(root_path, f"{stock_code}_{trade_date}.csv")
        if not df.empty:
            df.to_csv(filename, encoding='gb18030')

    def set_ipo_date(self, stock_code):
        query = self.mysql.select_values(stock_code, 'trade_date')
        ipo_date = pd.to_datetime(query[0])
        # ipo_date = datetime.date(1990,12,19)
        self.mysql.update_value(
            'stock_manager', 'ipo_date',
            f"'{ipo_date[0]}'", f"stock_code='{stock_code}'")
        return ipo_date[0]

    def get_ipo_date(self, stock_code):
        query = self.mysql.select_values(stock_code, 'trade_date')
        ipo_date = pd.to_datetime(query[0])
        return ipo_date[0]

    def repaire_lost_data(self, stock_code):
        ipo_date = self.get_ipo_date(stock_code)
        query = self.mysql.condition_select(
            stock_code, 'trade_date,close_price,highest_price,lowest_price,open_price,prev_close_price,change_rate,amplitude,volume,turnover',
            f"trade_date>='{ipo_date}'"
            )
        query.columns = [
            'trade_date', 'close_price', 'highest_price',
            'lowest_price', 'open_price', 'prev_close_price',
            'change_rate', 'amplitude', 'volume', 'turnover']
        query['trade_date'] = pd.to_datetime(query['trade_date'])
        query.set_index('trade_date', inplace=True)
        basic = self.mysql.condition_select(
            'SH000001', 'trade_date, close_price', f"trade_date>='{ipo_date}'"
        )
        basic.columns = ['trade_date', 'sh000001']
        basic['trade_date'] = pd.to_datetime(basic['trade_date'])
        basic.set_index('trade_date', inplace=True)
        result = pd.concat([query, basic], axis=1)
        # print(result.loc[datetime.date(2009,11,1):datetime.date(2010,1,22),])
        # print(result.dtypes)
        result = result[result['close_price'].isnull()]
        for index, row in result.iterrows():
            sql = (
                    f"INSERT ignore into {stock_code} set trade_date='{index}'"
                )
            self.mysql.insert(sql)

    def repair_prev_close_data(self, stock_code):
        ipo_date = self.get_ipo_date(stock_code)
        query = self.mysql.select_values(stock_code, 'trade_date,close_price')
        query.columns = ['trade_date', 'close_price']
        query['trade_date'] = pd.to_datetime(query['trade_date'])
        query.set_index('trade_date', inplace=True)
        query.fillna(0, inplace=True)
        query['prev_close_price'] = query['close_price'].shift(1)
        query = query[1:]
        print(query[query['close_price'].isnull()])
        for index, row in query.iterrows():
            try:
                sql = (
                    f"update {stock_code} set prev_close_price={row['prev_close_price']} "
                    f"where trade_date='{index}'"
                )
                self.mysql.engine.execute(sql)
            except Exception as e:
                print(e, index)

    def stat_problem_data(self, stock_code):
        ipo_date = self.set_ipo_date(stock_code)
        query = self.mysql.condition_select(
            stock_code, 'trade_date,close_price', f"trade_date>='{ipo_date}'"
            )
        query.columns = ['trade_date', 'close_price']
        query['trade_date'] = pd.to_datetime(query['trade_date'])
        query.set_index('trade_date', inplace=True)

        basic = self.mysql.condition_select(
            'SH000001', 'trade_date, close_price', f"trade_date>='{ipo_date}'"
        )
        basic.columns = ['trade_date', 'sh000001']
        basic['trade_date'] = pd.to_datetime(basic['trade_date'])
        basic.set_index('trade_date', inplace=True)
        result = pd.concat([query, basic], axis=1)
        result = result[result['close_price'].isnull()]
        print(stock_code, ":", result.shape[0])
        """
        for index, row in result.iterrows():
            sql = (
                    f"INSERT ignore into {stock_code}  set trade_date='{index}'"
                )
            self.mysql.insert(sql)
        """


def absolute_path(file_path: str, file_name: str) -> str:
    """
    Connect path with file, return a absolute path.
    """
    if (file_path[-1] == '/') and (file_name[0] == '/'):
        result_path = file_path + file_name[1:]
    elif (file_path[-1] != '/') and (file_name[0] != '/'):
        result_path = file_path + '/' + file_name
    else:
        result_path = file_path + file_name
    return result_path


if __name__ == "__main__":
    pass
