#!/usr/bin/python38
import requests
import os
import re
import json
import time
import psutil
from lxml import etree

report_path = '/data1/file_data/report'

class SpiderBase(object):
    """
    Basic class
    """
    def __init__(self) -> None:
        self._http_header = {}
        fatal_file = os.path.join(report_path, 'fatal_file')
        if os.path.exists(fatal_file):
            self.FATAL = open(fatal_file, 'a')
        else:
            raise FileNotFoundError(f"{fatal_file} is not found.")

    def get(self, url: str):
        """
        Return http response.
        """
        response = requests.get(url, headers=self._http_header)
        if response.status_code == 200:
            return response
        else:
            self._fatal_url(url)
            return None

    def _fatal_url(self, url: str):
        self.FATAL.write(url + '\n')

    def delay(self, delta: int):
        time.sleep(delta)

    def _freememery(self) -> float:
        r = psutil.virtual_memory()
        return r.percent

    def _freecpu(self):
        pass


class DownloadSpider(SpiderBase):
    def __init__(self, path: str) -> None:
        super(DownloadSpider, self).__init__()
        self.Path = path

    def save_bin(self, url: str, path: str, file_name: str):
        result = self.get(url)
        if not os.path.exists(path):
            os.makedirs(path)
        full_name = path + '/' + file_name
        if result:
            with open(full_name, 'wb') as f:
                f.write(result.content)

    def save_text(self, url: str, path: str, file_name: str):
        result = self.get(url)
        if not os.path.exists(path):
            os.makedirs(path)
        full_name = path + '/' + file_name
        if result:
            with open(full_name, 'w') as f:
                f.write(result.text)


class HtmlSpider(SpiderBase):
    def get_html(self, url: str):
        result = self.get(url)
        if result:
            html = etree.HTML(result.text)
        else:
            html = None
        return html

    def get_href(self, html):
        html.xpath('//a/@href')


class EMSpider(SpiderBase):
    def resolve_data(self, text: str):
        pattern = re.compile(r'"([0-9\-\.,]+)"')
        dataline = pattern.findall(text)
        result = []
        for line in dataline:
            # v: list tpye [v1, v2, v3 ...]
            v = re.split(',', line)
            result.append(v)
        return result

    def get_data(self, text: str):
        # resolve data from jquery response
        pattern = re.compile(r'datatable\d+\(([-+=a-zA-Z0-9\u4e00-\u9fa5\s\S]+)\)')
        j = re.findall(pattern, text)
        result = json.loads(j[0])
        data = result.get("data")
        return data

    def get_total_page(self, text: str) -> int:
        pattern = re.compile(r'datatable\d+\(([-+=a-zA-Z0-9\u4e00-\u9fa5\s\S]+)\)')
        j = re.findall(pattern, text)
        result = json.loads(j[0])
        total_page = result.get("TotalPage")
        return total_page

    def _resolve_file_type(self, url: str) -> str:
        result = url.split('.')
        return result[-1]

    def _resolve_researcher(self, data: json) -> list:
        author_list = data.get("author")
        result = []
        pattern = re.compile(r'(\d+).([-+=a-zA-Z0-9\u4e00-\u9fa5\s\S]+)')
        for au in author_list:
            au_match = re.match(pattern, au)
            if au_match:
                author = {"idx": au_match.group(1), "name": au_match.group(2)}
                result.append(author)
        return result

    def _resolve_institution(self, data: json) -> dict:
        inst_name = data.get("orgName")
        inst_code = data.get("orgCode")
        inst_short = data.get("orgSName")
        inst_data = {"org_name": inst_name, "org_code": inst_code, "short_name": inst_short}
        return inst_data

    def _resolve_code(self, data: json) -> str:
        if data.get("market") == 'SHENZHEN':
            prefix = 'SZ'
        elif data.get("market") == 'SHANGHAI':
            prefix = 'SH'
        else:
            prefix = ''
        code = prefix + f'{data.get("stockCode")}'
        return code

    def _resolve_industry(self, data: json) -> dict:
        indu_code = data.get("industryCode")
        indu_name = data.get("industryName")
        indu_data = { "industryCode": indu_code, "industryName": indu_name}
        return indu_data

    def _get_title(self, text: str) -> str:
        text = text.replace('?', '')
        text = text.replace('"', '')
        text = text.replace('/', '-')
        text = text.replace(':', '：')
        if len(text) > 90:
            text = text[:90]
        return text


if __name__ == '__main__':
    pass
