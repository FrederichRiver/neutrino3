#!/usr/bin/python38
from libspider.spider_model import HtmlSpider
import requests


class WorldBankReportSpider(HtmlSpider):
    total_page = 32052
    start_url = "https://openknowledge.worldbank.org/recent-submissions?offset=0"

    def resolve_page(self, html):
        report_url = html.xpath('//ul[@class="df-artifact-list list-unstyled"]/li/div/@data-href')
        print(report_url)


event = WorldBankReportSpider()
r = requests.get(event.start_url)
print(r)
# html = event.get_html(event.start_url)
# event.resolve_page(html)
