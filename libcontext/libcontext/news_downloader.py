#!/usr/bin/python38
import re
import requests
from lxml import etree
import lxml
from libcontext.model import news, formArticle
from polaris.mysql8 import mysqlHeader, mysqlBase
from sqlalchemy.ext.declarative import declarative_base
from mars.log_manager import log_with_return, log_wo_return


__version__ = '1.2.4'

article_base = declarative_base()


class newsSpiderBase(object):
    def __init__(self, header, path):
        self.mysql = mysqlBase(header)
        self.url_list = []
        self.href = []
        self.article_set = []
        self.path = path + 'config/'

    def save_process(self):
        url_file = self.path + 'URL_LIST'
        with open(url_file, 'w') as f:
            for url in self.url_list:
                f.write(str(url) + '\n')
        href_file = self.path + 'HREF_LIST'
        with open(href_file, 'w') as f:
            for url in self.href:
                f.write(str(url) + '\n')

    @log_wo_return
    def load_href_file(self, href_file):
        with open(href_file, 'r') as f:
            url = f.readlines()
            # print(url)
            self.href.extend(url)


class neteaseFinanceSpider(newsSpiderBase):
    """
    Finance channel
    """
    def generate_url_list(self):
        self._chn_list()
        self._hk_list()
        self._us_list()
        self._ipo_list()
        self._fund_list()
        self._future_list()
        self._kcb_list()
        self._forexchange_list()
        self._chairman_list()
        self._bc_list()
        self._business_list()
        self._house_list()
        self.c1()
        self.c2()
        self.c3()
        self.c4()
        self.c5()

    def _chn_list(self):
        chn_start_url = "https://money.163.com/special/002557S6/newsdata_gp_index.js?callback=data_callback"
        self.url_list.append(chn_start_url)
        chn_url_list = [f"https://money.163.com/special/002557S6/newsdata_gp_index_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += chn_url_list

    def _hk_list(self):
        hk_start_url = "https://money.163.com/special/002557S6/newsdata_gp_hkstock.js?callback=data_callback"
        self.url_list.append(hk_start_url)
        hk_url_list = [f"https://money.163.com/special/002557S6/newsdata_gp_hkstock_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += hk_url_list

    def _us_list(self):
        us_start_url = "https://money.163.com/special/002557S6/newsdata_gp_usstock.js?callback=data_callback"
        self.url_list.append(us_start_url)
        us_url_list = [f"https://money.163.com/special/002557S6/newsdata_gp_usstock_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += us_url_list

    def _ipo_list(self):
        ipo_start_url = "https://money.163.com/special/002557S6/newsdata_gp_ipo.js?callback=data_callback"
        self.url_list.append(ipo_start_url)
        ipo_url_list = [f"https://money.163.com/special/002557S6/newsdata_gp_ipo_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += ipo_url_list

    def _future_list(self):
        qhzx_start_url = "https://money.163.com/special/002557S6/newsdata_gp_qhzx.js?callback=data_callback"
        self.url_list.append(qhzx_start_url)
        qhzx_url_list = [f"https://money.163.com/special/002557S6/newsdata_gp_qhzx_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += qhzx_url_list

    def _forexchange_list(self):
        forex_start_url = "https://money.163.com/special/002557S6/newsdata_gp_forex.js?callback=data_callback"
        self.url_list.append(forex_start_url)
        forex_url_list = [f"https://money.163.com/special/002557S6/newsdata_gp_forex_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += forex_url_list

    def _bc_list(self):
        bitcoin_start_url = "https://money.163.com/special/002557S6/newsdata_gp_bitcoin.js?callback=data_callback"
        self.url_list.append(bitcoin_start_url)
        bitcoin_url_list = [f"https://money.163.com/special/002557S6/newsdata_gp_bitcoin_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += bitcoin_url_list

    def _kcb_list(self):
        kcb_start_url = "http://money.163.com/special/00259D2D/fund_newsflow_hot.js?callback=data_callback"
        self.url_list.append(kcb_start_url)
        kcb_url_list = [f"http://money.163.com/special/00259D2D/fund_newsflow_hot_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += kcb_url_list

    def _fund_list(self):
        fund_start_url = "http://money.163.com/special/00259CPE/data_kechuangban_kechuangban.js?callback=data_callback"
        self.url_list.append(fund_start_url)
        fund_url_list = [f"http://money.163.com/special/00259CPE/data_kechuangban_kechuangban_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += fund_url_list

    def _chairman_list(self):
        chairman_start_url = "http://money.163.com/special/00259CTD/data-yihuiman.js?callback=data_callback"
        self.url_list.append(chairman_start_url)
        chairman_url_list = [f"http://money.163.com/special/00259CTD/data-yihuiman_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += chairman_url_list

    def _business_list(self):
        business_start_url = "http://money.163.com/special/002557RF/data_idx_shangye.js?callback=data_callback"
        self.url_list.append(business_start_url)
        business_url_list = [f"http://money.163.com/special/002557RF/data_idx_shangye_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += business_url_list

    def _house_list(self):
        house_start_url = "http://money.163.com/special/002534NU/house2010.html"
        self.url_list.append(house_start_url)
        house_url_list = [f"http://money.163.com/special/002534NU/house2010_{str(i).zfill(2)}.html" for i in range(2, 21)]
        self.url_list += house_url_list

    # New url
    def c1(self):
        start_url = "https://temp.163.com/special/00804KVA/cm_guonei.js?callback=data_callback"
        self.url_list.append(start_url)
        url = [f"https://temp.163.com/special/00804KVA/cm_guonei_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += url

    def c2(self):
        start_url = "https://temp.163.com/special/00804KVA/cm_guoji.js?callback=data_callback"
        self.url_list.append(start_url)
        url = [f"https://temp.163.com/special/00804KVA/cm_guonei_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += url

    def c3(self):
        start_url = "https://temp.163.com/special/00804KVA/cm_war.js?callback=data_callback"
        self.url_list.append(start_url)
        url = [f"https://temp.163.com/special/00804KVA/cm_war_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += url

    def c4(self):
        start_url = "https://temp.163.com/special/00804KVA/cm_hangkong.js?callback=data_callback&a=2"
        self.url_list.append(start_url)
        url = [f"https://temp.163.com/special/00804KVA/cm_hangkong_0{i}.js?callback=data_callback&a=2" for i in range(2, 10)]
        self.url_list += url

    def c5(self):
        start_url = "https://news.163.com/uav/special/000189N0/uav_index.js?callback=data_callback"
        self.url_list.append(start_url)
        url = [f"https://news.163.com/uav/special/000189N0/uav_index_0{i}.js?callback=data_callback" for i in range(2, 10)]
        self.url_list += url

    def extract_href(self, url):
        resp = requests.get(url)
        result = re.findall(
            r'\"docurl\":\"(http.://money.163.com/\d{2}/\d{4}/\d{2}/\w+\.html)\"',
            resp.text)
        self.href += result

    def extract_href2(self, url):
        resp = requests.get(url)
        result = re.findall(
            r'\"docurl\":\"(http\w?://\w+\.163.com/\d{2}/\d{4}/\d{2}/\w+\.html)\"',
            resp.text)
        # print(result)
        self.href += result
        result = re.findall(
            r'\"docurl\":\"(http\w?://\w+\.163.com/\w+/\w+/\w+/\w+\.html)\"',
            resp.text)
        #print(result)
        result = re.findall(
            r'\"docurl\":\"(http\w?://\w+\.163.com/\w+/\w+/\w+\.html)\"',
            resp.text)
        #print(result)
        self.href += result
        result = re.findall(
            r'\"docurl\":\"(http\w?://www.163.com/dy/article/\w+\.html)\"',
            resp.text)
        self.href += result

    @log_with_return
    def extract_article(self, url):
        text = requests.get(url)
        html = etree.HTML(text.text)
        art = news(html)
        art.url = url
        return art

    @log_wo_return
    def record_article(self, art: news):
        insert_data = {
                # 'title': f"{art.title}",
                'url': f"{art.url}",
                'release_date': f"{art.date}",
                # 'content': f"{art.text}"
                }
        self.mysql.session.execute(
            formArticle.__table__.insert().prefix_with('IGNORE'),
            insert_data)
        self.mysql.session.commit()


class SinaNewsSpider(newsSpiderBase):
    def start_url(self, count=1):
        for i in range(count, count+10000):
            self.url_list.append(f"http://roll.finance.sina.com.cn/finance/zq1/index_{i}.shtml")

    def generate_url_list(self):
        """
        http://roll.finance.sina.com.cn/finance/zq1/index_1.shtml
        https://finance.sina.com.cn/stock/
        http://finance.sina.com.cn/stock/newstock/
        http://finance.sina.com.cn/stock/hkstock/
        https://finance.sina.com.cn/stock/usstock/
        http://finance.sina.com.cn/stock/kechuangban/
        http://finance.sina.com.cn/stock/quanshang/
        http://finance.sina.com.cn/stock/estate/
        https://finance.sina.com.cn/fund/
        https://finance.sina.com.cn/futuremarket/
        https://finance.sina.com.cn/forex/
        https://finance.sina.com.cn/nmetal/
        http://finance.sina.com.cn/bond/
        http://finance.sina.com.cn/money/
        http://finance.sina.com.cn/money/bank/
        http://finance.sina.com.cn/money/insurance/
        http://finance.sina.com.cn/trust/
        http://finance.sina.cn/esg/
        http://finance.sina.com.cn/meeting/
        http://finance.sina.com.cn/zt_d/20200727dp/
        https://finance.sina.cn/roll.d.html?rollCid=230808
        http://stock.finance.sina.com.cn/stock/go.php/vReport_List/kind/lastest/index.phtml
        http://finance.sina.com.cn/qizhi/
        http://finance.sina.com.cn/7x24/
        """
        url = "https://finance.sina.com.cn/stock/"
        return url

    def extract_href(self, url: str) -> list:
        resp = requests.get(url)
        if resp.status_code == 200:
            result = lxml.etree.HTML(resp.text)
            urls = result.xpath("//li/a/@href")
        else:
            urls = []
        result = []
        for url in urls:
            # if re.match(r'(http|https)://finance.sina.com.cn/(stock|roll|wm|dy)/\w+/\d{4}-\d{2}-\d{2}/doc-[0-9a-zA-Z]+.shtml', url):
            if re.match(r'(http|https)://finance.sina.com.cn/[a-zA-Z0-9_/]+/\d{4}-\d{2}-\d{2}/doc-[0-9a-zA-Z]+.shtml', url):
                result.append(url)
            elif re.match(r'(http|https)://finance.sina.com.cn/[a-zA-Z0-9_/]+/\d{8}/[0-9a-zA-Z]+.shtml', url):
                result.append(url)
            else:
                with open('/home/friederich/Documents/spider/failed', 'a') as f:
                    f.write(f"{url}\n")
        return result

    def record_url(self, url):
        """
        Insert url into table natural_language.news
        """
        sql = f"INSERT IGNORE into news (url) values ('{url}')"
        self.mysql.engine.execute(sql)

    def extract_article(self, url: str) -> news:
        """
        Extract article from finance@sina
        """
        resp = requests.get(url)
        html = etree.HTML(resp.text)
        sina_article = news(html)
        if resp.status_code == 200:
            html = lxml.etree.HTML(resp.text.encode('ISO-8859-1'))
            sina_article = news(html)
            self.record_article(sina_article)
        return sina_article

    def record_article(self, art):
        insert_data = {
                'url': f"{art.url}",
                'release_date': f"{art.date}",
                }
        self.mysql.session.execute(
            formArticle.__table__.insert().prefix_with('IGNORE'),
            insert_data)
        self.mysql.session.commit()


if __name__ == "__main__":
    from dev_global.env import SOFT_PATH
    header = mysqlHeader('stock', 'stock2020', 'corpus')
    event = neteaseFinanceSpider(header, SOFT_PATH)
    event.generate_url_list()
    print(len(event.url_list))
    i = 0
    for url in event.url_list:
        i += 1
        print(i, url)
        event.extract_href(url)
        event.extract_href2(url)
        print(len(event.href))
    for href in event.href:
        art = event.extract_article(href)
        event.record_article(art)
    """start_url = "https://news.163.com/uav/special/000189N0/uav_index.js?callback=data_callback"
    # start_url = "https://money.163.com/special/002557S6/newsdata_gp_index.js?callback=data_callback"
    start_url = "https://temp.163.com/special/00804KVA/cm_war.js?callback=data_callback"
    event.extract_href2(start_url)"""
