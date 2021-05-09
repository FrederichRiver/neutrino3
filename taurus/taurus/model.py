#! /usr/bin/env python3
import re
from sqlalchemy import Column, String, Integer, Date, Text
from sqlalchemy.ext.declarative import declarative_base
import lxml.etree


__version__ = 2


article_base = declarative_base()


class spider(object):
    def __init__(self):
        self.start_url = None

    def fetch_start_url(self, url):
        if re.match(r'(https?)://.', url):
            self.start_url = url
        else:
            raise UrlFormatError

    def query_url(self, url):
        # query whether url exists.
        return True


class UrlFormatError(BaseException):
    pass


class formArticle(article_base):
    __tablename__ = 'article'
    idx = Column(Integer)
    title = Column(String(50), primary_key=True)
    url = Column(String(50))
    author = Column(String(20))
    release_date = Column(Date)
    source = Column(String(20))
    filehash = Column(String(20))
    content = Column(Text)


class ArticleBase(object):
    def __init__(self):
        self.j_dict = {}

    @property
    def title(self) -> str:
        return self.j_dict['title']

    @property
    def author(self) -> str:
        return self.j_dict['author']

    @property
    def release_date(self):
        return self.j_dict['date']

    @property
    def source(self) -> str:
        return self.j_dict['source']

    @property
    def url(self) -> str:
        return self.j_dict['url']

    @url.setter
    def url(self, value):
        self.j_dict['url'] = value

    @property
    def content(self):
        return self.j_dict['content']

    def _get_title(self, input_content):
        raise NotImplementedError

    def _get_author(self, input_content):
        raise NotImplementedError

    def _get_date(self, input_content):
        raise NotImplementedError

    def _get_source(self, input_content):
        raise NotImplementedError

    def _get_content(self, input_content):
        raise NotImplementedError


class article(object):
    """
    Netease article model.
    """
    def __init__(self):
        self.title = ""
        self.author = ""
        self.content = ""
        self.date = None
        self.source = ""
        self.url = ""

    def _get_date(self, html):
        if not isinstance(html, lxml.etree._Element):
            raise TypeError('html type error')
        date_string = html.xpath("//div[@class='post_time_source']/text()")
        for s in date_string:
            result = re.search(r'\d{4}\-\d{2}\-\d{2}', s)
            if result:
                return result[0]
        return None

    def _get_title(self, html):
        if not isinstance(html, lxml.etree._Element):
            raise TypeError('html type error')
        title = html.xpath("//div/h1/text()")
        if title:
            title = title[0]
        return title

    def _get_source(self, html: lxml.etree._Element):
        if not isinstance(html, lxml.etree._Element):
            raise TypeError('html type error')
        source = html.xpath("//div[@class='ep-source cDGray']/span[@class='left']/text()")
        if source:
            result = re.split(r'：', source[0])
            return result[1]
        else:
            return None

    def _get_author(self, html):
        if not isinstance(html, lxml.etree._Element):
            raise TypeError('html type error')
        author = html.xpath("//span[@class='ep-editor']/text()")
        if author:
            result = re.split(r'：', author[0])
            return result[1]
        else:
            return None

    def _text_clean(self, text: list):
        content = ''
        for line in text:
            result = line.xpath(
                "./text()"
                "|.//*[name(.)='font' or name(.)='b' or name(.)='a']/text()")
            for subline in result:
                content += subline
        # remove space
        content.replace(' ', '')
        content.replace('\content', '')
        content.replace('\n', '')
        # remove \content \n etc.
        return content


class SinaArticle(object):
    """
    Sina article model.
    """
    def __init__(self):
        self.title = ""
        self.author = ""
        self.content = ""
        self.date = None
        self.source = ""
        self.url = ""

    def _get_date(self, html):
        if not isinstance(html, lxml.etree._Element):
            raise TypeError('html type error')
        date_string = html.xpath("//div[@class='date-source']/span/text()")
        for s in date_string:
            result = re.search(r'(\d{4})\w(\d{2})\w(\d{2})', s)
            if result:
                return f"{result.group(1)}-{result.group(2)}-{result.group(3)}"
        return None

    def _get_title(self, html):
        if not isinstance(html, lxml.etree._Element):
            raise TypeError('html type error')
        title = html.xpath("//h1/text()")
        if title:
            title = title[0]
        return title

    def _get_source(self, html: lxml.etree._Element):
        if not isinstance(html, lxml.etree._Element):
            raise TypeError('html type error')
        source = html.xpath("//div[@class='date-source']/a[@class='source ent-source']/text()")
        if source:
            result = source[0]
            return result
        else:
            return None

    def _get_author(self, html):
        if not isinstance(html, lxml.etree._Element):
            raise TypeError('html type error')
        author = html.xpath("//p[@class='article-editor']/text()")
        if author:
            result = re.split(r'：', author[0])
            return result[1]
        else:
            return None

    def _text_clean(self, content_text: list):
        content = ''
        for line in content_text:
            content += line
        # remove space
        # remove \content \n etc.
        return content


if __name__ == "__main__":
    import requests
    url = "https://finance.sina.com.cn/stock/roll/2020-08-29/doc-iivhvpwy3687766.shtml"
    resp = requests.get(url)
    sina_article = SinaArticle()
    html = lxml.etree.HTML(resp.text.encode('ISO-8859-1'))
    title = sina_article._get_title(html)
    print(title)
    author = sina_article._get_author(html)
    print(author)
    release_date = sina_article._get_date(html)
    print(release_date)
    source = sina_article._get_source(html)
    print(source)
    content_text = html.xpath("//div[@class='article']/p//text()")
    content = sina_article._text_clean(content_text)
    print(content)
