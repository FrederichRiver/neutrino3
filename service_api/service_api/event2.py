#!/usr/bin/python38
# from libbasemodel.spider_model import tarantula
from libbasemodel.shibor import ShiborData


def event_init_shibor():
    from libmysql_utils.mysql8 import mysqlHeader
    remote_head = mysqlHeader(acc="stock", pw="stock2020", db="stock", host="115.159.1.221")
    event = ShiborData(remote_head)
    month_list = event.month_list(from_date='2006-10', to_date='2021-03')
    for month in month_list:
        event.shibor_url = month
        df = event.get_excel_object(event.shibor_url)
        event.get_shibor_data(df)

def event_init_adjust_factor():
    """
    通过分红送转数据初始化复权因子并写入数据库。低应用事件。
    """
    from libmysql_utils.header import REMOTE_HEADER
    from libbasemodel.stock_interest import EventStockData
    event = EventStockData(REMOTE_HEADER)
    stock_list = event.get_all_stock_list()
    for stock in stock_list:
        # print(stock)
        try:
            df = event.adjust_factor(stock)
            df.to_sql(f"tmp_{stock}", event.engine, if_exists='replace')
            sql = f"UPDATE {stock},tmp_{stock} set {stock}.adjust_factor=tmp_{stock}.adjust_factor where {stock}.trade_date=tmp_{stock}.trade_date"
            event.engine.execute(sql)
            event.engine.execute(f'drop table tmp_{stock}')
        except Exception as e:
            print(e)

if __name__ == '__main__':
    pass
