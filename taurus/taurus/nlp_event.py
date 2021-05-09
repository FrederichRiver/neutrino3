#!/usr/bin/python3

__version__ = 3
__all__ = ['event_download_netease_news', 'event_record_announce_url', ]


def event_download_netease_news():
    from libmysql_utils.mysql8 import mysqlHeader
    from dev_global.env import SOFT_PATH
    from taurus.news_downloader import neteaseNewsSpider
    header = mysqlHeader('stock', 'stock2020', 'natural_language')
    event = neteaseNewsSpider(header, SOFT_PATH)
    event.generate_url_list()
    for url in event.url_list:
        event.extract_href(url)
    event.save_process()
    # hfile = SOFT_PATH + 'config/HREF_LIST'
    # event.load_href_file(hfile)
    for url in event.href:
        art = event.extract_article(url)
        event.record_article(art)


def event_record_announce_url():
    from polaris.mysql8 import mysqlHeader, GLOBAL_HEADER
    from venus.stock_base import StockEventBase
    from taurus.announcement import cninfoAnnounce
    event_stock_list = StockEventBase(GLOBAL_HEADER)
    stock_list = event_stock_list.get_all_stock_list()
    mysql_header = mysqlHeader('stock', 'stock2020', 'natural_language')
    event = cninfoAnnounce(mysql_header)
    event._set_param()
    for stock in stock_list:
        event.run(stock)


def event_record_sina_news_url():
    from taurus.news_downloader import SinaNewsSpider
    from polaris.mysql8 import NLP_HEADER
    import time
    import random
    # NLP_HEADER = mysqlHeader('stock', 'stock2020', 'natural_language')
    event = SinaNewsSpider(NLP_HEADER, '')
    i = 49444
    event.start_url(i)
    for url in event.url_list:
        hrefs = event.extract_href(url)
        for href in hrefs:
            # print(href)
            try:
                event.record_url(href)
            except Exception:
                pass
        time.sleep(random.randint(5, 10))
        with open('/home/friederich/Documents/spider/count', 'a') as f:
            f.write(f"Page: <{str(i)}> contains {len(hrefs)} urls.\n")
        i += 1


def event_download_news(n):
    from mars.network import delay
    from polaris.mysql8 import mysqlHeader
    from taurus.news_downloader import newsSpider
    header = mysqlHeader('stock', 'stock2020', 'natural_language')
    event = newsSpider(header)
    url_list = event.get_url_list()
    for url in url_list[:n]:
        try:
            event.save_page(url)
            delay(5)
        except Exception as e:
            print(url)
            print(e)


if __name__ == "__main__":
    # event_download_news(15000)
    event_record_sina_news_url()
