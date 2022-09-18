#!/usr/bin/python38
from libmysql_utils.orm.form import formStockManager
from libspider.form_model import form_industry
from libspider.spider_model import EMSpider
from libspider.form_model import form_institution, form_researcher, form_stock_report
from libmysql_utils.mysql8 import mysqlBase, mysqlHeader
import json
from lxml import etree
from libspider.spider_model import DownloadSpider
import os


report_path = '/data1/file_data/report'

class StockResearchReport(EMSpider):
    # Stock research report url
    # url = "http://reportapi.eastmoney.com/report/list?cb=datatable1588407&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime=2019-04-03&endTime=2021-04-03&pageNo=1&fields=&qType=0&orgCode=&code=*&rcode=&p=1&pageNum=1&_=1617464725114"
    def get_url(self, idx: int, start_date: str, end_date: str):
        url = f"http://reportapi.eastmoney.com/report/list?cb=datatable1588407&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime={start_date}&endTime={end_date}&pageNo={idx}&fields=&qType=0&orgCode=&code=*&rcode=&p={idx}&pageNum={idx}&_=1617464725114"
        return url

    def read_from_file(self) -> list:
        with open(os.path.join(report_path, 'fatal_file3'), 'r') as f:
            result = f.readlines()
        return result

    def get_pdf_href(self, response):
        html = etree.HTML(response.text)
        href = html.xpath('//div[@class="report-infos"]//a/@href')
        return href[1]

    def resolve_prop(self, data: str):
        if data:
            result = int(data)
        else:
            result = None
        return result

    def resolve_float(self, data):
        if data:
            result = float(data)
        else:
            result = None
        return result

    def _resolve_industry(self, data: json):
        idx = data.get("indvInduCode")
        indu_name = data.get("indvInduName")
        indu_data = {"idx": idx, "industry_name": indu_name}
        return indu_data

    def _resolve_report(self, data: json):
        prefix = "http://data.eastmoney.com/report/zw_stock.jshtml?infocode="
        info_code = data.get('infoCode')
        title = self._get_title(data.get("title"))
        au_list = self._resolve_researcher(data)
        if len(au_list) > 1:
            au1 = au_list[0].get('idx')
            au2 = au_list[1].get('idx')
        elif len(au_list) > 0:
            au1 = au_list[0].get('idx')
            au2 = None
        else:
            au1 = None
            au2 = None
        ins = self._resolve_institution(data)
        stock_code = self._resolve_code(data)
        indu_code = data.get("indvInduCode")
        pub_date = data.get('publishDate')
        # http://data.eastmoney.com/report/zw_stock.jshtml?infocode=AP202104021480769165
        page_url = prefix + info_code
        resp = self.get(page_url)
        pdf_url = self.get_pdf_href(resp)
        file_type = self._resolve_file_type(pdf_url)
        eps1 = self.resolve_float(data.get('predictNextYearEps'))
        pe1 = self.resolve_float(data.get('predictNextYearPe'))
        eps2 = self.resolve_float(data.get('predictNextTwoYearEps'))
        pe2 = self.resolve_float(data.get('predictNextTwoYearPe'))
        proposal = self.resolve_prop(data.get('emRatingValue'))
        report_dict = {
            "info_code": info_code, "title": title,
            "stock_code": stock_code,
            "institution": ins.get('org_code'),
            "author_1": au1, "author_2": au2,
            "page_url": page_url, "pdf_url": pdf_url,
            "pre_eps_1y": eps1, "pre_pe_1y": pe1,
            "pre_eps_2y": eps2, "pre_pe_2y": pe2,
            "proposal": proposal, "file_type": file_type,
            "indu_code": indu_code, "publish_date": pub_date,
        }
        return report_dict


class StockResearchReportDownloader(DownloadSpider, mysqlBase):
    def __init__(self, path: str, header: mysqlHeader) -> None:
        DownloadSpider.__init__(self, path)
        mysqlBase.__init__(self, header)
        self.industry_list = self._get_industry_list()
        self.stock_list = self._get_stock_list()

    def _get_industry_list(self) -> dict:
        # 获取机构列表
        result = self.session.query(form_industry.idx, form_industry.industry_name).all()
        return dict(result)

    def _get_stock_list(self) -> dict:
        result = self.session.query(formStockManager.stock_code, formStockManager.stock_name).all()
        return dict(result)

    def _get_report_list(self):
        # 获取报告列表
        result = self.session.query(
            form_stock_report.title, form_stock_report.stock_code,
            form_stock_report.publish_date, form_stock_report.indu_code,
            form_stock_report.pdf_url, form_stock_report.file_type).filter(form_stock_report.flag == None).all()
        return result

    def _construct_path(self, stock_code: str, title: str, pub_date: str, indu_code: str, file_type: str):
        """
        item[1], item[0], date2String, item[3], item[5]
        """
        # 构造path
        indu_name = self.industry_list.get(indu_code)
        stock_name = self.stock_list.get(stock_code, '')
        file_path = os.path.join(self.Path, indu_name, f"{stock_code}-{stock_name}")
        title = title.replace('/', '-')
        if len(title) > 30:
            title = title[:30]
        file_name = f"{stock_code}-{stock_name}-{title}-{pub_date}.{file_type}"
        return file_path, file_name


def event_download_stock_report(delta: int):
    from libmysql_utils.mysql8 import mysqlBase, mysqlHeader
    from datetime import datetime
    from datetime import timedelta
    report_path = '/data1/file_data/report'
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=delta)).strftime('%Y-%m-%d')
    head = mysqlHeader('stock', 'stock2020', 'stock')
    mysql = mysqlBase(head)
    event = StockResearchReport()
    url = event.get_url(1, start_date, end_date)
    page_response = event.get(url)
    if page_response.status_code == 200:
        total = event.get_total_page(page_response.text)
    else:
        total = 5
    print(f"Recording stock research report, total {total} pages to be down.")
    for i in range(1, total + 1):
        if i % 30 == 0:
            print(f"Recording the {i} page.")
        url = event.get_url(i, start_date, end_date)
        with open(os.path.join(report_path, 'record_url'), 'a') as f:
            f.write(url + '\n')
        main_response = event.get(url)
        if main_response.status_code == 200:
            data = event.get_data(main_response.text)
            for rep in data:
                try:
                    au_list = event._resolve_researcher(rep)
                    for au in au_list:
                        author = form_researcher(**au)
                        mysql.session.merge(author)
                    inst_dict = event._resolve_institution(rep)
                    inst = form_institution(**inst_dict)
                    mysql.session.merge(inst)
                    indu_data = event._resolve_industry(rep)
                    indu = form_industry(**indu_data)
                    mysql.session.merge(indu)
                    mysql.session.commit()
                    report_dict = event._resolve_report(rep)
                    report = form_stock_report(**report_dict)
                    mysql.session.merge(report)
                    mysql.session.commit()
                except Exception as e:
                    with open(os.path.join(report_path, 'fatal_stock_report'), 'a') as f:
                        f.write(str(rep))
                        f.write('\n')
                    print(e)
        else:
            with open(os.path.join(report_path, 'fatal_url'), 'a') as f:
                f.write(url + '\n')


def event_from_file():
    from libmysql_utils.mysql8 import mysqlBase, mysqlHeader
    head = mysqlHeader('stock', 'stock2020', 'stock')
    mysql = mysqlBase(head)
    event = StockResearchReport()
    data_list = event.read_from_file()
    i = 0
    for data in data_list[i:]:
        print(i)
        i += 1
        json_data = json.loads(data)
        try:
            au_list = event._resolve_researcher(json_data)
            for au in au_list:
                author = form_researcher(**au)
                mysql.session.merge(author)
            inst_dict = event._resolve_institution(json_data)
            inst = form_institution(**inst_dict)
            mysql.session.merge(inst)
            report_dict = event._resolve_report(json_data)
            report = form_stock_report(**report_dict)
            mysql.session.merge(report)
            mysql.session.commit()
        except Exception as e:
            print(e)
            with open(os.path.join(report_path, 'fatal_file4'), 'a') as f:
                f.write(str(json_data))
                f.write('\n')


def event_save_stock_report(delta: int):
    head = mysqlHeader('stock', 'stock2020', 'stock')
    event = StockResearchReportDownloader(os.path.join(report_path, 'stock_report'), header=head)
    report_list = event._get_report_list()
    print(f"Total {len(report_list)} stock reports to be down.")
    i = 0
    for report_item in report_list:
        i += 1
        if i % 100 == 0:    
            print(f"Downloading the {i} stock research report.")
            event.delay(300)
        pub_date = report_item[2].strftime('%Y-%m-%d')
        path, filename = event._construct_path(report_item[1], report_item[0], pub_date, report_item[3], report_item[5])
        event.save_bin(report_item[4], path, filename)
        event.delay(delta)
        event.session.query(form_stock_report).filter(form_stock_report.pdf_url == report_item[4]).update({"flag": 'D'})
        event.session.commit()


if __name__ == '__main__':
    # event_from_website()
    event_save_stock_report()
