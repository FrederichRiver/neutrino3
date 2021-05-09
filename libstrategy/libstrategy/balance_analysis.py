#!/usr/bin/python3
from venus.stock_base import StockEventBase

__all__ = ['event_balance_analysis',]

class balanceAnalysis(StockEventBase):
    def __init__(self, header):
        super(balanceAnalysis, self).__init__(header)
        #self.stock_code = stock_code

    def update_roe(self, stock_code):
        """
        income statement: float_c41, net profit
        balance sheet: float_assets, float_liability
        """
        import pandas
        from dev_global.env import TIME_FMT
        result = self.mysql.condition_select(
            'balance_sheet', 'report_date,float_assets,float_liability', f"char_stock_code='{stock_code}'"
        )
        result2 = self.mysql.condition_select(
            'income_statement', 'report_date,float_c41', f"char_stock_code='{stock_code}'"
        )
        if (not result.empty) and (not result2.empty):
            result.columns = ['report_date','total_asset', 'total_liability']
            result['equity'] = result['total_asset'] - result['total_liability']
            result['report_date'] = pandas.to_datetime(result['report_date'], format=TIME_FMT)
            result.set_index('report_date', inplace=True)
            result2.columns = ['report_date', 'net_profit']
            result2['report_date'] = pandas.to_datetime(result2['report_date'], format=TIME_FMT)
            result2.set_index('report_date', inplace=True)
            df = pandas.concat([result,result2], axis=1)
            df.dropna(axis=0, inplace=True)
            df['roe'] = df['net_profit'] / df['equity']
            for index, row in df.iterrows():
                sql = (
                    f"INSERT IGNORE into finance_perspective ("
                    "char_stock_code,report_date,float_roe)"
                    f"VALUES ('{stock_code}','{index}', {row['roe']})"
                )
                self.mysql.engine.execute(sql)

    def update_leverage(self, stock_code):
        import pandas
        from dev_global.env import TIME_FMT
        result = self.mysql.condition_select(
            'balance_sheet', 'report_date,float_assets,float_liability', f"char_stock_code='{stock_code}'"
        )
        if not result.empty:
            result.columns = ['report_date','total_asset', 'total_liability']
            result['leverage'] = result['total_liability'] / result['total_asset'] 
            result['report_date'] = pandas.to_datetime(result['report_date'], format=TIME_FMT)
            result.set_index('report_date', inplace=True)
            result.dropna(axis=0, inplace=True)
            check = self.mysql.condition_select(
                'finance_perspective', 'report_date,char_stock_code', f"char_stock_code='{stock_code}'" 
            )
            #print(check)
            if not check.empty:
                check.columns = ['report_date', 'stock_code']
                check['check'] = 'u'
                check['report_date'] = pandas.to_datetime(check['report_date'], format=TIME_FMT)
                check.set_index('report_date', inplace=True)
                df = pandas.concat([result, check], axis=1)
            else:
                df = result
                df['check'] = 'i'
            #print(df)
            for index, row in df.iterrows():
                if row['check'] == 'i':
                    sql = (
                        f"INSERT IGNORE into finance_perspective ("
                        "char_stock_code,report_date,float_leverage)"
                        f"VALUES ('{stock_code}','{index}', {row['leverage']})"
                    )
                else:
                    sql = (
                        f"UPDATE finance_perspective set "
                        f"float_leverage={row['leverage']} "
                        f"WHERE (char_stock_code='{stock_code}') and (report_date='{index}')"
                    )
                self.mysql.engine.execute(sql)

    @property
    def total_asset(self):
        pass

def event_balance_analysis():
    from dev_global.env import GLOBAL_HEADER
    from saturn.balance_analysis import balanceAnalysis
    from jupiter.utils import ERROR
    event = balanceAnalysis(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock in stock_list:
        try:
            event.update_roe(stock)
            event.update_leverage(stock)    
        except Exception as e:
            ERROR(e)


if __name__ == "__main__":
    from dev_global.env import GLOBAL_HEADER
    event = balanceAnalysis(GLOBAL_HEADER)
    stock_list = event.get_all_stock_list()
    for stock in stock_list[:50]:
        event.update_leverage(stock)