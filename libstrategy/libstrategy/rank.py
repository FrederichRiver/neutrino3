#!/usr/bin/python3

from libmysql_utils.mysql8 import mysqlBase
from dev_global.env import VIEWER_HEADER


class data_view_base(object):
    def __init__(self):
        self.mysql = mysqlBase(VIEWER_HEADER)

    def get_data(self):
        raise Exception

    def visualize(self):
        raise Exception


class profit_growth_rate(data_view_base):
    def get_data(self, stock_code):
        from datetime import date
        import pandas
        import copy
        result = self.mysql.condition_select(
            'income_statement','report_date,float_c40',f"char_stock_code='{stock_code}'")
        if not result.empty:
            result.columns = ['report_date', 'net_profit']
            result.set_index('report_date', inplace=True)
            #print(result)
            result2 = copy.deepcopy(result)
            for index, row in result2.iterrows():
                if index.month == 6:
                    index_key = date(index.year, 3, 31)
                    for col in result.columns:
                        try:
                            row[col] = row[col] - result.loc[index_key, col]
                        except Exception as e:
                            pass
                elif index.month == 9:
                    index_key = date(index.year, 6, 30)
                    for col in result.columns:
                        try:
                            row[col] = row[col] - result.loc[index_key, col]
                        except Exception as e:
                            pass
                elif index.month == 12:
                    index_key = date(index.year, 9, 30)
                    for col in result.columns:
                        try:
                            row[col] = row[col] - result.loc[index_key, col]
                        except Exception as e:
                            pass
            #x = pandas.concat([result,result2], axis=1 )
            #print(x)
            result2['last_period'] = result2['net_profit'].shift(4)
            result2['growth_rate'] = result2['net_profit']/result2['last_period'] - 1
            result2.dropna(axis=0, how='any', inplace=True)

            result2.drop(['net_profit','last_period'], axis=1, inplace=True)
            result2.columns = [f"{stock_code}"]
            return result2
        else:
            return pandas.DataFrame()

    def get_stock_list(self):
        result = self.mysql.condition_select('stock_manager', 'stock_code', "flag='t'")
        return list(result[0])


def profit_growth_analysis():
    import pandas
    # import xlwt
    from datetime import date
    from jupiter import calendar
    event = profit_growth_rate()
    stock_list = event.get_stock_list()
    profit_data = pandas.DataFrame()
    for stock in stock_list:
        df = event.get_data(stock)
        if not df.empty:
            profit_data = pandas.concat([profit_data, df], axis=1)
    result = profit_data.T
    trade_period = calendar.TradeDay(2020)
    result = result.loc[:,[trade_period.period(trade_period.today, 3-i) for i in range(3)]]
    result.dropna(axis=0, inplace=True)
    temp = result[[trade_period.period(trade_period.today, 3-i) for i in range(3)]]
    result['mean'] = temp.mean(axis=1)
    result = result.sort_values(by='mean',ascending=False)
    result = result.applymap(lambda x: format(x, '.2%'))

    result.insert(0, 'stock_name', result.index)
    for index,row in result.iterrows():
        stock_name = event.mysql.select_one('stock_manager', 'stock_name', f"stock_code='{index}'")
        row['stock_name'] = stock_name[0]
   
    
    result.to_excel('/home/friederich/Downloads/stock_data_3.xls')
    #print(result)


if __name__ == "__main__":
    profit_growth_analysis()
    