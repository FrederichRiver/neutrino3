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


if __name__ == '__main__':
    pass
