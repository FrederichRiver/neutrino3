#!/usr/bin/python38

# http://reportapi.eastmoney.com/report/jg?cb=datatable3558439&pageSize=50&beginTime=2019-04-23&endTime=2021-04-23&pageNo=1&fields=&qType=2&orgCode=&author=&p=1&pageNum=1&_=1619179741299
# from libspider.spider_model import EMSpider
from libspider.macro_report import MacroReport
from libspider.form_model import form_institution, form_researcher, form_strategy_report
import json
import os
from libspider.spider_model import DownloadSpider
from libmysql_utils.mysql8 import mysqlBase, mysqlHeader


class StrategyReport(MacroReport):
    def get_url(self, idx: int, start_date: str, end_date: str):
        url = f"http://reportapi.eastmoney.com/report/jg?cb=datatable3558439&pageSize=50&beginTime={start_date}&endTime={end_date}&pageNo={idx}&fields=&qType=2&orgCode=&author=&p={idx}&pageNum={idx}&_=1619179741299"
        return url

    def _resolve_report(self, data: json):
        prefix = "http://data.eastmoney.com/report/zw_strategy.jshtml?encodeUrl="
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
        page_url = prefix + data.get("encodeUrl")
        resp = self.get(page_url)
        pdf_url = self.get_pdf_href(resp)
        file_type = self._resolve_file_type(pdf_url)
        report_dict = {
            "idx": id, "title": title, "institution": ins.get('org_code'), "author_1": au1,
            "author_2": au2, "page_url": page_url, "pdf_url": pdf_url,
            "publish_date": pub_date, "file_type": file_type,
        }
        return report_dict


class StrategyReportDownloader(DownloadSpider, mysqlBase):
    def __init__(self, path: str, header: mysqlHeader) -> None:
        DownloadSpider.__init__(self, path)
        mysqlBase.__init__(self, header)
        self.institution_list = self._get_institution_list()

    def _get_institution_list(self):
        result = self.session.query(form_institution.org_code, form_institution.org_name).all()
        return dict(result)

    def _get_report_list(self):
        # 获取报告列表
        result = self.session.query(
            form_strategy_report.title, form_strategy_report.institution, form_strategy_report.publish_date,
            form_strategy_report.pdf_url, form_strategy_report.file_type).filter(form_strategy_report.flag == None).all()
        return result

    def len_of_report(self, report_list) -> int:
        return len(report_list)

    def _construct_url(self):
        # 构造url
        pass

    def _construct_path(self, org_code: str, title: str, pub_date: str, file_type: str):
        # item[0]: title, item[1]: org, item[2]: date, item[3]: url, item[4]: type
        org = self.institution_list.get(org_code)
        file_path = os.path.join(self.Path, org)
        title = title.replace('/', '-')
        file_name = f"{title}-{pub_date}.{file_type}"
        return file_path, file_name


def event_record_strategy_report(delta: int):
    from libmysql_utils.mysql8 import mysqlBase, mysqlHeader
    from datetime import datetime
    from datetime import timedelta
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=delta)).strftime('%Y-%m-%d')
    head = mysqlHeader('stock', 'stock2020', 'stock')
    mysql = mysqlBase(head)
    event = StrategyReport()
    url = event.get_url(1, start_date, end_date)
    # print(url)
    page_response = event.get(url)
    if page_response.status_code == 200:
        total = event.get_total_page(page_response.text)
    else:
        total = 5
    print(f"Recording strategy research report, total {total} pages to be down.")
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
                    report = form_strategy_report(**report_dict)
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


def event_save_strategy_report(delta: int):
    head = mysqlHeader('stock', 'stock2020', 'stock')
    event = StrategyReportDownloader('/home/friederich/Documents/strategy_report', header=head)
    report_list = event._get_report_list()
    length = event.len_of_report(report_list)
    print(f"Total {len(report_list)} strategy reports to be down.")
    i = 0
    for report_item in report_list:
        i += 1
        print(f"Downloading the {i} strategy report.")
        pub_date = report_item[2].strftime('%Y-%m-%d')
        path, filename = event._construct_path(report_item[1], report_item[0], pub_date, report_item[4])
        event.save_bin(report_item[3], path, filename)
        event.delay(delta)
        event.session.query(form_strategy_report).filter(form_strategy_report.pdf_url == report_item[3]).update({"flag": 'D'})
        event.session.commit()


# event_from_website()
# event_save_strategy_report()
