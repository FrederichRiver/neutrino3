#!/usr/bin/python3
import pandas as pd
import re
import lxml
import pandas
from libbasemodel.stock_model import StockBase
from mars.log_manager import log_wo_return
# from venus.stock_base import StockEventBase


class EventCompany(StockBase):
    def get_html_table(self, url, attr=''):
        # get html table from url.
        # Return a string like table object.
        # attr: [@class='table_bg001 border_box limit_scale scr_table']
        # //table[contains(@id,'historyTable')]
        html = self.get_html_object(url, HttpHeader=self.httpHeader)
        table_list = html.xpath(f"//table{attr}")
        result = []
        if table_list:
            for table in table_list:
                df = lxml.etree.tostring(table).decode()
                result.append(df)
        return result

    @log_wo_return
    def record_company_infomation(self, stock_code):
        url = f"http://quotes.money.163.com/f10/gszl_{stock_code[2:]}.html#01f02"
        table_list = self.get_html_table(url, attr="[@class='table_bg001 border_box limit_sale table_details']")
        t = pd.read_html(table_list[0])[0]
        insert_sql = (
            "INSERT IGNORE INTO company_info ("
            "stock_code, company_name, english_name, legal_representative, address,"
            "chairman, secratery, main_business, business_scope, introduction) "
            "VALUES ( "
            f"'{stock_code}','{t.iloc[2, 1]}','{t.iloc[3, 1]}',"
            f"'{t.iloc[6, 1]}','{t.iloc[1, 3]}','{t.iloc[4, 3]}','{t.iloc[5, 3]}',"
            f"'{t.iloc[9, 1]}','{t.iloc[10, 1]}','{t.iloc[11, 1]}')"
        )
        self.engine.execute(insert_sql)

    @log_wo_return
    def record_stock_structure(self, stock_code):
        url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructureHistory/stockid/{stock_code[2:]}/stocktype/TotalStock.phtml"
        table_list = self.get_html_table(url, attr="[contains(@id,'historyTable')]")
        if table_list:
            for table in table_list:
                df = self._resolve_stock_structure_table(table)
                self._update_stock_structure(stock_code, df)

    def _resolve_stock_structure_table(self, table) -> pandas.DataFrame:
        df = pd.read_html(table)
        # print(df)
        if df:
            df[0].columns = ['change_date', 'total_stock']
            result = df[0]
            result['total_stock'] = df[0]['total_stock'].apply(filter_str2float)
            result['change_date'] = pandas.to_datetime(result['change_date'])
            return result
        else:
            return pandas.DataFrame()

    def _update_stock_structure(self, stock_code, df: pandas.DataFrame):
        TAB_COMP_STOCK_STRUC = 'company_stock_structure'
        # value = {}
        if not df.empty:
            for index, row in df.iterrows():
                sql = (
                    f"INSERT IGNORE into {TAB_COMP_STOCK_STRUC} ("
                    f"stock_code,report_date,total_stock) "
                    f"VALUES ('{stock_code}','{row['change_date']}',{row['total_stock']})")
                # print(sql)
                self.engine.execute(sql)


def filter_str2float(x):
    result = re.match(r'(\d+)', x)
    if result:
        return 10000 * float(result[1])
    else:
        return 0


if __name__ == "__main__":
    from libmysql_utils.mysql8 import mysqlHeader
    header = mysqlHeader(acc='stock', pw='stock2020', db='stock')
    event = EventCompany(header)
    event.record_stock_structure('SH600000')
