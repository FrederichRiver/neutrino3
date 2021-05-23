#!/usr/bin/python38
from datetime import datetime
import re
from urllib.request import pathname2url
import requests
import json
from lxml import etree


class SpiderBase(object):
    """
    Basic class
    """
    def __init__(self) -> None:
        self._http_header = {}

    def get_html(self, url: str):
        result = requests.get(url, headers=self._http_header)
        if result.status_code == 200:
            html = etree.HTML(result.text)
        else:
            html = None
        return html

    def get_text(self, url: str):
        result = requests.get(url, headers=self._http_header)
        if result.status_code == 200:
            return result.text
        else:
            return ""


class EMSpider(SpiderBase):
    """
    url: "http://datacenter.eastmoney.com/api/data/get?callback=datatable1509410&type=RPTA_WEB_TREASURYYIELD&sty=ALL&st=SOLAR_DATE&sr=-1&token=894050c76af8597a853f5b408b759f5d&p=1&ps=50&_=1615912300344"
    """
    def get_start_page(self, text: str) -> int:
        x = re.search(r'\w+\((.+)\)', text)
        js_string = x.group(1)
        js_data = json.loads(js_string)
        pages = js_data.get("result").get("pages")
        page_num = int(pages)
        return page_num

    def resolve_total_data(self, text: str):
        pattern = re.compile(r'"([0-9\-\.,]+)"')
        x = pattern.findall(text)
        result = []
        for line in x:
            v = re.split(',', line)
            result.append(v)
        return result


class TreasuryYield(EMSpider):
    """
    Spider for treasury yield data from www.eastmoney.com
    """
    def get_total_page(self, text: str) -> int:
        x = re.search(r'\w+\((.+)\)', text)
        js_string = x.group(1)
        js_data = json.loads(js_string)
        pages = js_data.get("result").get("pages")
        page_num = int(pages)
        return page_num

    def resolve_data(self, text: str):
        old_list = ['SOLAR_DATE', 'EMM00588704', 'EMM00166462', 'EMM00166466', 'EMM00166469', 'EMG00001306', 'EMG00001308', 'EMG00001310', 'EMG00001312']
        new_list = ['report_date', 'two_year', 'five_year', 'ten_year', 'three_decade', 'us_two_year', 'us_five_year', 'us_ten_year', 'us_three_decade']
        for x, y in zip(old_list, new_list):
            text = text.replace(x, y)
        """SOLAR_DATE:
            EMM00588704: 2 years data
            EMM00166462: 5 years data
            EMM00166466: 10 years data
            EMM00166469: 30 years data
            EMG00001306: 2 years data from us
            EMG00001308: 5 years data from us
            EMG00001310: 10 years data from us
            EMG00001312: 30 years data from us"""
        x = re.search(r'\w+\((.+)\)', text)
        js_data = json.loads(x.group(1))
        data = js_data.get("result").get("data")
        return data

    def insert_table1(self, line: dict) -> str:
        dt = line.get("report_date")
        value = []
        for key in ["two_year", "five_year", "ten_year", "three_decade"]:
            y = line.get(key) if line.get(key) else "'NULL'"
            value.append(str(y))
        v = ",".join(value)
        sql = (
            "INSERT IGNORE into china_treasury_yield ("
            "report_date,two_year,five_year,ten_year,three_decade) "
            f"VALUES ('{dt}',{v})"
        )
        return sql

    def insert_table2(self, line: dict) -> str:
        dt = line.get("report_date")
        value = []
        for key in ["us_two_year", "us_five_year", "us_ten_year", "us_three_decade"]:
            y = line.get(key) if line.get(key) else "'NULL'"
            value.append(str(y))
        v = ",".join(value)
        sql = (
            "INSERT IGNORE into us_treasury_yield ("
            "report_date,two_year,five_year,ten_year,three_decade) "
            f"VALUES ('{dt}',{v})"
        )
        return sql

    def update_table1(self, line: dict) -> str:
        dt = line.get("report_date")
        value = []
        for key in ["two_year", "five_year", "ten_year", "three_decade"]:
            y = line.get(key) if line.get(key) else "0"
            value.append(f"{key}={str(y)}")
        v = ",".join(value)
        sql = (
            "UPDATE china_treasury_yield set "
            f"report_date='{dt}',{v}"
        )
        return sql

    def update_table2(self, line: dict) -> str:
        dt = line.get("report_date")
        value = []
        for key in ["us_two_year", "us_five_year", "us_ten_year", "us_three_decade"]:
            y = line.get(key) if line.get(key) else "0"
            value.append(f"{key.replace('us_', '')}={str(y)}")
        v = ",".join(value)
        sql = (
            "UPDATE us_treasury_yield set "
            f"report_date='{dt}',{v}"
        )
        return sql

    def replace_table1(self, line: dict) -> str:
        dt = line.get("report_date")
        value = []
        for key in ["two_year", "five_year", "ten_year", "three_decade"]:
            y = line.get(key) if line.get(key) else "0"
            value.append(str(y))
        v = ",".join(value)
        sql = (
            "REPLACE into china_treasury_yield ("
            "report_date,two_year,five_year,ten_year,three_decade) "
            f"VALUES ('{dt}',{v})"
        )
        return sql

    def replace_table2(self, line: dict) -> str:
        dt = line.get("report_date")
        value = []
        for key in ["us_two_year", "us_five_year", "us_ten_year", "us_three_decade"]:
            y = line.get(key) if line.get(key) else "0"
            value.append(str(y))
        v = ",".join(value)
        sql = (
            "REPLACE into us_treasury_yield ("
            "report_date,two_year,five_year,ten_year,three_decade) "
            f"VALUES ('{dt}',{v})"
        )
        return sql


class CPIBot(EMSpider):
    """
    url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=datatable7266279&type=GJZB&sty=ZGZB&js=(%7Bdata%3A%5B(x)%5D%2Cpages%3A(pc)%7D)&p=1&ps=20&mkt=19&_=1616830305596"
    """
    start_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=datatable7266279&type=GJZB&sty=ZGZB&js=(%7Bdata%3A%5B(x)%5D%2Cpages%3A(pc)%7D)&p=1&ps=20&mkt=19&_=1616830305596"

    total_data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery11230994022668721799_1616830305597&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=19&_=1616830305598"

    def value2sql(self, l: list) -> str:
        SQL = (
            "REPLACE into cpi (report_date,current_month_nation,cumulate_nation,current_month_city,cumulate_city,current_month_country,cumulate_country) "
            f"VALUES ('{l[0]}',{float(l[1])},{float(l[4])},{float(l[5])},{float(l[8])},{float(l[9])},{float(l[12])})"
        )
        return SQL


class PPIBot(EMSpider):
    total_data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery1123028535293032132514_1616833814561&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=22&_=1616833814562"

    def value2sql(self, l: list) -> str:
        SQL = (
            "REPLACE into ppi (report_date,current_month,cumulate) "
            f"VALUES ('{l[0]}',{float(l[1])},{float(l[3])})"
        )
        return SQL


class PMIBot(EMSpider):
    total_data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery1123017001035921084284_1616834447950&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=21&_=1616834447951"
    
    def value2sql(self, l: list) -> str:
        SQL = (
            "REPLACE into pmi (report_date,manufacture,non_manufacture) "
            f"VALUES ('{l[0]}',{float(l[1])},{float(l[3])})"
        )
        return SQL


class GDPBot(EMSpider):
    total_data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery112304441260065840724_1616834805096&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=20&_=1616834805099"

    def value2sql(self, l: list) -> str:
        SQL = (
            "REPLACE into gdp (report_date,total_gdp,agricuture,industry,service) "
            f"VALUES ('{l[0]}',{float(l[1])},{float(l[3])},{float(l[5])},{float(l[7])})"
        )
        return SQL


class MoneyBot(EMSpider):
    total_data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery112309693797280652459_1616835080694&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=11&_=1616835080697"

    def value2sql(self, l: list) -> str:
        SQL = (
            "REPLACE into money_supply (report_date,m0,m1,m2) "
            f"VALUES ('{l[0]}',{float(l[7])},{float(l[4])},{float(l[1])})"
        )
        return SQL


if __name__ == '__main__':
    """from libmysql_utils.mysql8 import mysqlHeader, mysqlBase
    head = mysqlHeader('stock', 'stock2020', 'stock')
    mysql = mysqlBase(head)
    event = PPIBot()
    resp = requests.get(event.total_data_url)
    data = event.resolve_total_data(resp.text)
    for line in data:
        sql = event.value2sql(line)
        mysql.exec(sql)"""
    from libmysql_utils.mysql8 import mysqlHeader, mysqlBase
    head = mysqlHeader('stock', 'stock2020', 'stock')
    mysql = mysqlBase(head)
    event = MoneyBot()
    resp = requests.get(event.total_data_url)
    data = event.resolve_total_data(resp.text)
    for line in data:
        sql = event.value2sql(line)
        mysql.exec(sql)
