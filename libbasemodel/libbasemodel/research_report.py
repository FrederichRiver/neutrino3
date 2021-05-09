#!/usr/bin/python38
from libbasemodel.spider_model import EMSpider
import requests
import json
import re


class ResearchReport(EMSpider):
    start_url = "http://reportapi.eastmoney.com/report/list?cb=datatable8413582&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime=2019-03-28&endTime=2021-03-28&pageNo=1&fields=&qType=0&orgCode=&code=*&rcode=&p=1&pageNum=1&_=1616942458238"
    start_url = "http://reportapi.eastmoney.com/report/list?cb=datatable7981780&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime=2019-03-27&endTime=2021-03-27&pageNo=1&fields=&qType=0&orgCode=&code=*&rcode=&p=1&pageNum=1&_=1616837098193"
    s         = "http://reportapi.eastmoney.com/report/list?cb=datatable3015753&industryCode=*&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime=2019-03-28&endTime=2021-03-28&pageNo=1&fields=&qType=1&orgCode=&rcode=&p=1&pageNum=1&_=1616942825776"
    s1        = "http://reportapi.eastmoney.com/report/list?cb=datatable1868682&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime=2019-04-03&endTime=2021-04-03&pageNo=2&fields=&qType=0&orgCode=&code=*&rcode=&p=2&pageNum=2&_=1617464725113"
    """
    [\u4e00-\u9fa5]+
    """
    def get_data(self, idx: int):
        url = f"http://reportapi.eastmoney.com/report/list?cb=datatable798780&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime=2019-03-27&endTime=2021-03-27&pageNo={idx}&fields=&qType=0&orgCode=&code=*&rcode=&p={idx}&pageNum={idx}&_=1616837098193"
        resp = requests.get(url)
        if resp.status_code == 200:
            pattern = re.compile(r'datatable\d+\(([-+=a-zA-Z0-9\u4e00-\u9fa5\s\S]+)\)')
            j = re.findall(pattern, resp.text)
            result = json.loads(j[0])
            total_page = result.get("TotalPage")
            data = result.get("data")
        else:
            data = None
        return data

    report_url = "http://data.eastmoney.com/report/zw_industry.jshtml?infocode=AP202103261477147740"

    def get_res(self, url):
        import lxml
        resp = requests.get(url)
        html = lxml.etree.HTML(resp.text)
        href = html.xpath('//a[@class="pdf-link"]/@href')
        return href[0]

    def resolve_data(self, data: json):
        # print(data)
        info_code = data.get('infoCode')
        page_url = f"http://data.eastmoney.com/report/zw_industry.jshtml?infocode={info_code}"
        pdf_url = self.get_res(page_url)
        title = data.get('title')
        org_name = data.get('orgSName')
        researcher = data.get('researcher')
        publish_date = data.get('publishDate')
        stock_code = data.get('stockCode')
        indv_code = data.get('indvInduCode')
        # industry_code = data.get('industryCode')
        # emindustry_code = data.get('emIndustryCode')
        # industry_name = data.get('industryName')
        sql = (
            "REPLACE into research_report ("
            "title,org_name,page_url,pdf_url,indv_industry_code,stock_code,publish_date,researcher) "
            f"VALUES ('{title}','{org_name}','{page_url}','{pdf_url}',{indv_code},'{stock_code}','{publish_date}','{researcher}')")
        return sql

    def save_data(self, j: json):
        with open('/home/friederich/Dev/neutrino2/data/research_report.json', 'a') as f1:
            f1.write(json.dumps(j, indent=4, ensure_ascii=False) + ',\n')


class ResearchReport2(EMSpider):
    start_url = "http://reportapi.eastmoney.com/report/list?cb=datatable3015753&industryCode=*&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime=2019-03-28&endTime=2021-03-28&pageNo=1&fields=&qType=1&orgCode=&rcode=&p=1&pageNum=1&_=1616942825776"
    """
    [\u4e00-\u9fa5]+
    """
    def get_data(self, idx: int):
        url = f"http://reportapi.eastmoney.com/report/list?cb=datatable3015753&industryCode=*&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime=2019-03-28&endTime=2021-03-28&pageNo={idx}&fields=&qType=1&orgCode=&rcode=&p={idx}&pageNum={idx}&_=1616942825776"
        resp = requests.get(url)
        if resp.status_code == 200:
            pattern = re.compile(r'datatable\d+\(([-+=a-zA-Z0-9\u4e00-\u9fa5\s\S]+)\)')
            j = re.findall(pattern, resp.text)
            result = json.loads(j[0])
            total_page = result.get("TotalPage")
            data = result.get("data")
        else:
            data = None
        return data

    def get_res(self, url):
        import lxml
        resp = requests.get(url)
        html = lxml.etree.HTML(resp.text)
        href = html.xpath('//a[@class="pdf-link"]/@href')
        return href[0]

    def resolve_data(self, data: json):
        # print(data)
        info_code = data.get('infoCode')
        page_url = f"http://data.eastmoney.com/report/zw_industry.jshtml?infocode={info_code}"
        pdf_url = self.get_res(page_url)
        title = data.get('title')
        org_name = data.get('orgSName')
        researcher = data.get('researcher')
        publish_date = data.get('publishDate')
        # stock_code = data.get('stockCode')
        # indv_code = data.get('indvInduCode')
        industry_code = data.get('industryCode')
        emindustry_code = data.get('emIndustryCode')
        industry_name = data.get('industryName')
        sql = (
            "REPLACE into research_report2 ("
            "title,org_name,page_url,pdf_url,publish_date,researcher,industry_code,em_industry_code,industry_name) "
            f"VALUES ('{title}','{org_name}','{page_url}','{pdf_url}','{publish_date}','{researcher}',{industry_code},{emindustry_code}, '{industry_name}')")
        return sql


class ResearchReport(EMSpider):
    """
    Macro research report url
    url = "http://reportapi.eastmoney.com/report/jg?cb=datatable4023011&pageSize=50&beginTime=2019-03-29&endTime=2021-03-29&pageNo=1&fields=&qType=3&orgCode=&author=&p=1&pageNum=1&_=1617026025191"
    """
    def get_data(self, idx: int):
        url = f"http://reportapi.eastmoney.com/report/list?cb=datatable798780&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime=2019-03-27&endTime=2021-03-27&pageNo={idx}&fields=&qType=0&orgCode=&code=*&rcode=&p={idx}&pageNum={idx}&_=1616837098193"
        resp = requests.get(url)
        if resp.status_code == 200:
            pattern = re.compile(r'datatable\d+\(([-+=a-zA-Z0-9\u4e00-\u9fa5\s\S]+)\)')
            j = re.findall(pattern, resp.text)
            result = json.loads(j[0])
            total_page = result.get("TotalPage")
            data = result.get("data")
        else:
            data = None
        return data

    report_url = "http://data.eastmoney.com/report/zw_industry.jshtml?infocode=AP202103261477147740"

    def get_res(self, url):
        import lxml
        resp = requests.get(url)
        html = lxml.etree.HTML(resp.text)
        href = html.xpath('//a[@class="pdf-link"]/@href')
        return href[0]

    def resolve_data(self, data: json):
        # print(data)
        info_code = data.get('infoCode')
        page_url = f"http://data.eastmoney.com/report/zw_industry.jshtml?infocode={info_code}"
        pdf_url = self.get_res(page_url)
        title = data.get('title')
        org_name = data.get('orgSName')
        researcher = data.get('researcher')
        publish_date = data.get('publishDate')
        stock_code = data.get('stockCode')
        indv_code = data.get('indvInduCode')
        # industry_code = data.get('industryCode')
        # emindustry_code = data.get('emIndustryCode')
        # industry_name = data.get('industryName')
        sql = (
            "REPLACE into research_report ("
            "title,org_name,page_url,pdf_url,indv_industry_code,stock_code,publish_date,researcher) "
            f"VALUES ('{title}','{org_name}','{page_url}','{pdf_url}',{indv_code},'{stock_code}','{publish_date}','{researcher}')")
        return sql

    def save_data(self, j: json):
        with open('/home/friederich/Dev/neutrino2/data/research_report.json', 'a') as f1:
            f1.write(json.dumps(j, indent=4, ensure_ascii=False) + ',\n')



if __name__ == '__main__':
    import time
    from libmysql_utils.mysql8 import mysqlBase, mysqlHeader
    head = mysqlHeader('stock', 'stock2020', 'corpus')
    mysql = mysqlBase(head)
    event = ResearchReport()
    # event.get_data(1)
    for i in range(1, 1227):
        print(i)
        # time.sleep(30)
        data = event.get_data(i)
        if data:
            for line in data:
                event.save_data(line)
                #sql = event.resolve_data(line)
                #mysql.exec(sql)

    """start_url = "http://reportapi.eastmoney.com/report/list?cb=datatable798780&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime=2019-03-27&endTime=2021-03-27&pageNo=1&fields=&qType=0&orgCode=&code=*&rcode=&p=1&pageNum=1&_=1616837098193"
    resp = requests.get(start_url)
    # pattern = re.compile(r'datatable\d+\(([[.\u4e00-\u9fa5]+])\)')
    pattern = re.compile(r'datatable\d+\(([-+=a-zA-Z0-9\u4e00-\u9fa5\s\S]+)\)')
    test = "你好%90+=*@!#$%^&*())阿布"
    result = re.findall(pattern, resp.text)
    print(result)"""
