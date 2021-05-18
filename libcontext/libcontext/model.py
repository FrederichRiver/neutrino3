#!/usr/bin/python38
import hashlib
import lxml
import re
import requests
from lxml import etree
from libmysql_utils.mysql8 import mysqlHeader, mysqlBase
from sqlalchemy import Column, String, Integer, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from libutils.log import Log


__version__ = 2


article_base = declarative_base()


class spider(object):
    def __init__(self):
        self.start_url = None

    def fetch_start_url(self, url):
        if re.match(r'(https?)://.', url):
            self.start_url = url
        else:
            raise Exception

    def query_url(self, url):
        # query whether url exists.
        return True


class formArticle(article_base):
    __tablename__ = 'news'
    idx = Column(Integer)
    title = Column(String(50), primary_key=True)
    url = Column(String(50))
    release_date = Column(Date)
    source = Column(String(10))
    content = Column(Text)
    keyword = Column(Text)


class news(object):
    def __init__(self, html: lxml.etree._Element):
        if not isinstance(html, lxml.etree._Element):
            raise TypeError('Article is not a lxml.etree._Element object.')
        self._html = html
        if self._html:
            self._title = ""
            self._get_title()
            self._author = ""
            self._content = ""
            self._get_text()
            self._date = ""
            self._get_date()
            self._source = ""
            self.url = ""

    def __str__(self):
        return f"《{self.title}》:{self.author}:{self.date}"

    @Log
    def _get_date(self):
        """
        eld version:
        date_string = self._html.xpath("//div[@class='post_time_source']/text()")
        """
        date_string = self._html.xpath("//div[@class='post_info']/text()")
        for s in date_string:
            result = re.search(r'\d{4}\-\d{2}\-\d{2}', s)
            if result:
                self._date = result.group()
                break
            else:
                self._date = ''

    @property
    def date(self) -> str:
        return self._date

    @Log
    def _get_title(self):
        result = self._html.xpath("//div/h1/text()")
        if result:
            self._title = result[0]
        else:
            self._title = ""

    @property
    def title(self) -> str:
        return self._title

    @property
    def source(self):
        article_source = self._html.xpath("//div[@class='ep-source cDGray']/span[@class='left']/text()")
        if article_source:
            result = re.split(r'：', article_source[0])
            self._source = result[1]
        else:
            self._source = ""
        return self._source

    @property
    def author(self):
        article_author = self._html.xpath("//span[@class='ep-editor']/text()")
        if article_author:
            result = re.split(r'：', article_author[0])
            self._author = result[1]
        else:
            self._author = ""
        return self._author

    @Log
    def _get_text(self):
        """
        elder version:
        _text = self._html.xpath("//div[@class='post_text']/p")
        """
        _text = self._html.xpath("//div[@class='post_body']/p")
        for line in _text:
            result = line.xpath(
                "./text()"
                "|.//*[name(.)='font' or name(.)='b' or name(.)='a']/text()")
            for subline in result:
                self._content += subline
        # remove space
        self._content.replace(' ', '')
        self._content.replace('\content', '')
        self._content.replace('\n', '')
        # remove \content \n etc.

    @property
    def text(self) -> str:
        return self._content


if __name__ == "__main__":
    url = "https://money.163.com/21/0302/19/G43UHG4S00259DLP.html"
    text = requests.get(url)
    h = etree.HTML(text.text)
    art = article(h)
    art.url = url
    print("url", art.url)
    print("title", art.title)
    print("date", art.date)
    # print("text", art.text)
