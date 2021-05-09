#!/usr/bin/python38
from libbasemodel.spider_model import tarantula
from libbasemodel.shibor import ShiborData


def event_record_total_treasury_yield():
    """
    Treasury yield data of China & US from eastmoney.com
    """
    from libmysql_utils.mysql8 import mysqlHeader, mysqlBase
    head = mysqlHeader(acc="stock", pw="stock2020", host="115.159.1.221", db="stock")
    mysql = mysqlBase(head)
    url = "http://datacenter.eastmoney.com/api/data/get?callback=datatable1509410&type=RPTA_WEB_TREASURYYIELD&sty=ALL&st=SOLAR_DATE&sr=-1&token=894050c76af8597a853f5b408b759f5d&p={}&ps=50&_=1615912300344" 
    event = tarantula()
    result = event.get_text(url.format(1))
    p = event.get_total_page(result)
    for i in range(p+1):
        result = event.get_text(url.format(i))
        data = event.resolve_data(result)
        for dataline in data:
            sql = event.insert_table1(dataline)
            sql2 = event.insert_table2(dataline)
            mysql.engine.execute(sql)
            mysql.engine.execute(sql2)


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
