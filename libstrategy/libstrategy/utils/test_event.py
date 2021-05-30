from libstrategy.utils.kalendar import Kalendar
from libmysql_utils.mysql8 import mysqlHeader
from libstrategy.data_engine import StockDataSet
import pandas as pd

event = Kalendar((2019, 1, 1))
event.config('china')

REMOTE_HEAD = mysqlHeader('stock', 'stock2020', 'stock', '115.159.1.221')
StockData = StockDataSet(REMOTE_HEAD)
df = StockData.query('SH600000', '2019-01-01', '2019-03-30')
for d in event:
    data = StockData.get_data(pd.Timestamp(d))
    print(d, data)