#!/usr/bin/python38
import pandas as pd
from venus.stock_base import StockEventBase
from jupiter.utils import data_clean, set_date_as_index


class financeBase(StockEventBase):
    def get_finance_value(self, stock_code, table_name, value_name, value_alias):
        """
        General query function
        """
        df = self.mysql.condition_select(
            table_name, f"report_period,{value_name}",
            f"stock_code='{stock_code}'")
        result = pd.DataFrame.from_dict(df)
        result.columns = ['date', value_alias]
        result = data_clean(result)
        result = set_date_as_index(result)
        return result

    def get_total_asset(self, stock_code):
        """
        return total asset.
        """
        result = self.get_finance_value(
            stock_code,
            'balance_sheet', 'r1_assets', 'total_asset')
        return result

    def get_total_liability(self, stock_code):
        """
        return total liability.
        """
        result = self.get_finance_value(
            stock_code,
            'balance_sheet', 'r4_liability', 'total_liability')
        return result

    def get_current_liability(self, stock_code):
        """
        return total liability.
        """
        result = self.get_finance_value(
            stock_code,
            'balance_sheet', 'r4_1_current_liability', 'current')
        return result

    def get_long_term_liability(self, stock_code):
        """
        return total liability.
        """
        result = self.get_finance_value(
            stock_code,
            'balance_sheet', 'r4_2_long_term_liability', 'long_term')
        return result

    def get_debt_2_asset_ratio(self, stock_code):
        """
        Composite function debt/asset
        """
        df1 = self.get_total_asset(stock_code)
        df2 = self.get_total_liability(stock_code)
        result = pd.concat([df1, df2], axis=1)
        return result

    def total_liability(self, stock_code):
        current = self.get_current_liability(stock_code)
        long_term = self.get_long_term_liability(stock_code)
        liability = current + long_term
        print(liability)


class financeReportBase(StockEventBase):
    def test(self):
        pass


if __name__ == "__main__":
    from libmysql_utils.mysql8 import GLOBAL_HEADER
    event = financeBase(GLOBAL_HEADER)
    df = event.get_total_asset("SH601818")
    df = event.get_debt_2_asset_ratio("SH601818")
    event.total_liability("SH601818")
    print(df)
