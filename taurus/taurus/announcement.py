#!/usr/bin/python3

from venus.cninfo import spiderBase
from venus.stock_base2 import StockBase
from libmysql_utils.mysql8 import mysqlBase, GLOBAL_HEADER, mysqlHeader
from dev_global.env import TIME_FMT
import requests
import datetime
import time
import random

__all__ = ['event_record_announce_url', ]


class cninfoAnnounce(StockBase, spiderBase):
    def __init__(self, header: mysqlHeader) -> None:
        spiderBase.__init__(self)
        StockBase.__init__(self, header)

    def _set_param(self):
        self.path = 'root'
        self.index = mysqlBase(GLOBAL_HEADER)
        self.url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
        self.http_header = {
            "Accept": 'application/json, text/javascript, */*; q=0.01',
            "Accept-Encoding": 'gzip, deflate',
            "Accept-Language": 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            "Connection": 'keep-alive',
            "Content-Length": '157',
            "Content-Type": 'application/x-www-form-urlencoded; charset=UTF-8',
            "Cookie": 'JSESSIONID=BFBF1E4A2BB770FDC299840EBF23A51D; _sp_ses.2141=*; cninfo_user_browse=000603,gssz0000603,%E7%9B%9B%E8%BE%BE%E8%B5%84%E6%BA%90|603019,9900023134,%E4%B8%AD%E7%A7%91%E6%9B%99%E5%85%89|000521,gssz0000521,%E9%95%BF%E8%99%B9%E7%BE%8E%E8%8F%B1; UC-JSESSIONID=800AC4F4588B800E4B0C0469250DF5C8; _sp_id.2141=12284594-c734-478d-82ca-0a1ccbb7de3f.1585407313.7.1585576172.1585500168.83476562-29c9-4d02-9a3a-ee515406e161',
            "Host": 'www.cninfo.com.cn',
            "Origin": 'http://www.cninfo.com.cn',
            "Referer": 'http://www.cninfo.com.cn/new/disclosure/stock?plate=szse&stockCode=000603&orgId=gssz0000603',
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            "X-Requested-With": 'XMLHttpRequest',
            }
        self.form_data = 'stock=603019%2C9900023134&tabName=fulltext&pageSize=30&pageNum=1&column=sse&category=&plate=sh&seDate=&searchkey=&secid=&sortName=&sortType=&isHLtitle=true'

    def set_formdata(self, stock_code, orgid, page, total_page=30):
        """
        translate formdata from json to string.
        Return : a string of query data.
        """
        form_data = {
            "stock": f'{stock_code[2:]}%2C{orgid}',
            "tabName": 'fulltext',
            "pageSize": '30',
            "pageNum": f"{page}",
            "column": 'sse',
            "category": '',
            "plate": f'{str.lower(stock_code[:2])}',
            "seDate": '',
            "searchkey": '',
            "secid": '',
            "sortName": '',
            "sortType": '',
            "isHLtitle": 'true'
        }
        result = ''
        temp = []
        for k, v in form_data.items():
            line = k + '=' + v
            temp.append(line)
        result = '&'.join(temp)
        return result

    def set_http_header(self, stock_code, flag):
        self.http_header["Referer"] = f"http://www.cninfo.com.cn/new/disclosure/stock?stockCode={stock_code[2:]}&orgId={flag}"

    def set_cookie(self):
        pass

    def get_cookie(self):
        pass

    def run(self, stock_code: str):
        """
        Record announcement into database.
        """
        select_orgid = self.index.select_one('stock_manager', 'orgid', f"stock_code='{stock_code}'")
        i = 1
        while has_more := self.resolve_announce_page(stock_code, select_orgid[0], i):
            i += 1
            time.sleep(random.randint(3, 10))

    def resolve_announce_page(self, stock_code: str, orgid: str, page):
        self.form_data = self.set_formdata(stock_code, orgid, page)
        resp = self.request.post(
            self.url, data=self.form_data, headers=self.http_header)
        json_result_list = resp.json()
        self.record_announce_page(stock_code, json_result_list)
        hasMore = json_result_list["hasMore"]
        return hasMore

    def record_announce_page(self, stock_code, json_content_list: dict):
        import pymysql
        json_list = json_content_list['announcements']
        for ann in json_list:
            # title = base64.b64encode(ann['announcementTitle'].encode())
            title = pymysql.Binary(ann['announcementTitle'].encode())
            sql = (
                f"INSERT IGNORE into announce_manager ("
                f"announce_id,stock_code,title,announce_timestamp,url,announce_type) "
                "VALUES ("
                f"'{ann['announcementId']}','{stock_code}',"
                f"%s,{ann['announcementTime']/1000},"
                f"'{ann['adjunctUrl']}','{ann['announcementType']}')"
            )
            self.engine.execute(sql, title)
        return json_content_list["hasMore"]

    def get_pdf_url(self, ann_id):
        result = self.mysql.condition_select(
            'announce_manager', 'stock_code,announce_id,title,announce_timestamp,url',
            f"announce_id='{ann_id}'")
        pdf_name = result[0][0] + '_' + str(result[2][0], encoding='utf-8') + '_' + result[1][0] + '_' + datetime.datetime.fromtimestamp(int(result[3][0])).strftime(TIME_FMT) + '.pdf'
        url = 'http://static.cninfo.com.cn/' + result[4][0]
        return pdf_name, url

    def save_pdf(self, pdf_name, url):
        r = requests.get(url)
        pdf_name = '/home/friederich/Dev/test/' + pdf_name
        # filename = "requests.pdf"
        with open(pdf_name, 'wb+') as f:
            f.write(r.content)


def event_record_announce_url():
    from polaris.mysql8 import mysqlHeader
    from dev_global.env import GLOBAL_HEADER
    from venus.stock_base import StockEventBase
    event_stock_list = StockEventBase(GLOBAL_HEADER)
    stock_list = event_stock_list.get_all_stock_list()
    mysql_header = mysqlHeader('stock', 'stock2020', 'natural_language')
    event = cninfoAnnounce(mysql_header)
    event._set_param()
    for stock in stock_list:
        event.run(stock)


if __name__ == "__main__":
    from libmysql_utils.mysql8 import mysqlHeader
    print('ok')