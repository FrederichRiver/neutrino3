#!/usr/bin/python38
from libspider.spider_model import EMSpider
from libspider.form_model import form_money_supply, form_ppi, form_cpi, form_gdp, form_pmi
from libutils.log import Log
from libmysql_utils.mysql8 import mysqlBase


class DataLoader(mysqlBase):
    @Log
    def record(self, data):
        self.session.merge(data)
        self.session.commit()


class CPIBot(EMSpider):
    """
    url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=datatable7266279&type=GJZB&sty=ZGZB&js=(%7Bdata%3A%5B(x)%5D%2Cpages%3A(pc)%7D)&p=1&ps=20&mkt=19&_=1616830305596"
    """
    data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery11230994022668721799_1616830305597&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=19&_=1616830305598"

    def map_value(self, v: list):
        data = {
            "report_date": f"{v[0]}", "current_month_nation": float(v[1]),
            "cumulate_nation": float(v[4]), "current_month_city": float(v[5]),
            "cumulate_city": float(v[8]), "current_month_country": float(v[9]),
            "cumulate_country": float(v[12])}
        result = form_cpi(**data)
        return result


class PPIBot(EMSpider):
    data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery1123028535293032132514_1616833814561&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=22&_=1616833814562"

    def map_value(self, v: list):
        data = {"report_date": f"{v[0]}", "current_month": float(v[1]), "cumulate": float(v[3])}
        result = form_ppi(**data)
        return result


class PMIBot(EMSpider):
    data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery1123017001035921084284_1616834447950&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=21&_=1616834447951"

    def map_value(self, v: list):
        data = {"report_date": f"{v[0]}", "manufacture": float(v[1]), "non_manufacture": float(v[3])}
        result = form_pmi(**data)
        return result


class GDPBot(EMSpider):
    data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery112304441260065840724_1616834805096&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=20&_=1616834805099"

    def map_value(self, v: list):
        data = {
            "report_date": f"{v[0]}", "total_gdp": float(v[1]), "agricuture": float(v[3]),
            "industry": float(v[5]),  "service": float(v[7]), }
        result = form_gdp(**data)
        return result


class MoneyBot(EMSpider):
    data_url = "http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?cb=jQuery112309693797280652459_1616835080694&type=GJZB&sty=ZGZB&js=(%5B(x)%5D)&p=1&ps=200&mkt=11&_=1616835080697"

    def map_value(self, v: list):
        data = {"report_date": f"{v[0]}", "m0": float(v[7]), "m1": float(v[4]), "m2": float(v[1])}
        result = form_money_supply(**data)
        return result


if __name__ == '__main__':
    from libmysql_utils.mysql8 import mysqlBase, mysqlHeader
    head = mysqlHeader('stock', 'stock2020', 'stock')
    downloader = DataLoader(head)
    event = CPIBot()
    response = event.get(event.data_url)
    data_list = event.resolve_data(response.text)
    form_data = event.map_value(data_list[0])
    downloader.record(form_data)

