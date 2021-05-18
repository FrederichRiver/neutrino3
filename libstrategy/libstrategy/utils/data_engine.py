import pandas as pd
from datetime import date
from pandas import DataFrame
from libmysql_utils.mysql8 import mysqlBase
from dev_global.env import TIME_FMT


class StockDataSet(mysqlBase):
    """
    get data from a exterior data like pandas.DataFrame.
    method: StockDataSet.data = pandas.DataFrame
    """
    def __init__(self, header):
        super(StockDataSet, self).__init__(header)
        self.data = DataFrame()

    def query(self, stock_code: str, from_date: str, end_date: str):
        """
        stock_code : str
        """
        df = self.condition_select(
            stock_code, 'trade_date,open_price,close_price,high_price,low_price',
            f"trade_date BETWEEN '{from_date}' AND '{end_date}'")
        df.columns = ['trade_date', 'open', 'close', 'high', 'low']
        df['trade_date'] = pd.to_datetime(df['trade_date'],format=TIME_FMT)
        df.set_index('trade_date', inplace=True)
        return df

    def get_data(self, query_date) -> list:
        if query_date in self.data.index:
            result = self.data.loc[query_date]
        else:
            result = []
        return list(result)


from libstrategy.utils.kalendar import Kalendar
from libmysql_utils.mysql8 import mysqlHeader
#from libstrategy.utils.data_engine import StockDataSet
import pandas as pd

event = Kalendar((2019, 1, 1))
event.config('china')
event.length = 10

REMOTE_HEAD = mysqlHeader('stock', 'stock2020', 'stock', '115.159.1.221')
StockData = StockDataSet(REMOTE_HEAD)
StockData.data = StockData.query('SH600000', '2019-01-01', '2019-03-30')
for d in event:
    data = StockData.get_data(pd.Timestamp(d))
    print(d, data)