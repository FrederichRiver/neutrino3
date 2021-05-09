#!/usr/bin/python38
# "http://data.eastmoney.com/report/industry.jshtml"

# from libspider.spider_model import EMSpider
from libspider.macro_report import MacroReport
from libspider.form_model import form_institution, form_researcher, form_industry_report, form_industry
import json
import os
from libspider.spider_model import DownloadSpider
from libmysql_utils.mysql8 import mysqlHeader, mysqlBase
from libbasemodel.form import formStockManager


class IndustryReport(MacroReport):
    def get_url(self, idx: int, start_date: str, end_date: str):
        url = f"http://reportapi.eastmoney.com/report/list?cb=datatable104208&industryCode=*&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime={start_date}&endTime={end_date}&pageNo={idx}&fields=&qType=1&orgCode=&rcode=&p={idx}&pageNum={idx}&_=1619105820175"
        return url

    def _resolve_industry(self, data: json):
        idx = data.get("industryCode")
        indu_name = data.get("industryName")
        indu_data = {"idx": idx, "industry_name": indu_name}
        return indu_data

    def _resolve_report(self, data: json):
        prefix = "http://data.eastmoney.com/report/zw_industry.jshtml?infocode="
        id = data.get('id')
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
        pub_date = data.get('publishDate')
        page_url = prefix + data.get("infoCode")
        indu_code = data.get("industryCode")
        resp = self.get(page_url)
        pdf_url = self.get_pdf_href(resp)
        file_type = self._resolve_file_type(pdf_url)
        report_dict = {
            "idx": id, "title": title, "institution": ins.get('org_code'), "author_1": au1,
            "author_2": au2, "page_url": page_url, "pdf_url": pdf_url,
            "publish_date": pub_date, "file_type": file_type, "indu_code": indu_code,
        }
        return report_dict


class IndustryReportDownloader(DownloadSpider, mysqlBase):
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
            form_industry_report.title, form_industry_report.institution,
            form_industry_report.publish_date, form_industry_report.indu_code,
            form_industry_report.pdf_url, form_industry_report.file_type).filter(form_industry_report.flag == None).all()
        return result

    def _construct_path(self, title: str, pub_date: str, indu_code: str, file_type: str):
        """
        item[0]: title, item[2]: date, item[3]: industry_code, item[5]
        """
        # 构造path
        indu_name = self.industry_list.get(indu_code)
        print(indu_name)
        file_path = os.path.join(self.Path, indu_name)
        title = title.replace('/', '-')
        file_name = f"{title}-{pub_date}.{file_type}"
        return file_path, file_name


def event_record_industry_report(delta: int):
    from libmysql_utils.mysql8 import mysqlBase, mysqlHeader
    from datetime import datetime
    from datetime import timedelta
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=delta)).strftime('%Y-%m-%d')
    head = mysqlHeader('stock', 'stock2020', 'stock')
    mysql = mysqlBase(head)
    event = IndustryReport()
    url = event.get_url(1, start_date, end_date)
    # print(url)
    page_response = event.get(url)
    if page_response.status_code == 200:
        total = event.get_total_page(page_response.text)
    else:
        total = 5
    print(f"Recording industry report, total {total} pages to be down.")
    for i in range(1, total + 1):
        print(f"Recording the {i} page.")
        url = event.get_url(i, start_date, end_date)
        with open('/home/friederich/Dev/neutrino2/data/record_url', 'a') as f:
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
                    report_dict = event._resolve_report(rep)
                    report = form_industry_report(**report_dict)
                    mysql.session.merge(report)
                    mysql.session.commit()
                except Exception as e:
                    with open('/home/friederich/Dev/neutrino2/data/fatal_file2', 'a') as f:
                        f.write(str(rep))
                        f.write('\n')
                    print(e)
        else:
            with open('/home/friederich/Dev/neutrino2/data/fatal_url', 'a') as f:
                f.write(url + '\n')


def event_save_industry_report(delta: int):
    head = mysqlHeader('stock', 'stock2020', 'stock')
    event = IndustryReportDownloader('/home/friederich/Documents/industry_report/', header=head)
    report_list = event._get_report_list()
    print(f"Total {len(report_list)} industry report to be down.")
    i = 0
    for report_item in report_list:
        i += 1
        print(f"Downloading the {i} industry report.")
        if i % 100 == 0:
            event.delay(300)
        pub_date = report_item[2].strftime('%Y-%m-%d')
        path, filename = event._construct_path(report_item[0], pub_date, report_item[3], report_item[5])
        # print(path)
        # print(filename)
        event.save_bin(report_item[4], path, filename)
        event.delay(delta)
        event.session.query(form_industry_report).filter(form_industry_report.pdf_url == report_item[4]).update({"flag": 'D'})
        event.session.commit()
