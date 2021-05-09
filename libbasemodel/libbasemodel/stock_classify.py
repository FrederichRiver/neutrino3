#!/usr/bin/python3
from libbasemodel.stock_model import StockBase
import datetime


class StockClassify(StockBase):
    """
    API: @flag_quit_stock(stock_code)\n
         @flag_stock_type(stock_code, flag_type)\n
    """
    def flag_quit_stock(self, stock_code):
        df = self.select_values(stock_code, 'trade_date')
        if not df.empty:
            # result is DataFrame, 0 is the first column.
            df = list(df[0])
            delta = datetime.date.today() - df[-1]
            if delta.days > 150:
                return True
            else:
                return False
        else:
            return False

    def flag_stock_type(self, stock_code: str, flag_type: str):
        """
        stock: flag_type -> t\n
        index: flag_type -> i\n
        b stock: flag_type -> b\n
        hk stock: flag_type -> h\n
        fund: flag_type -> f\n
        """
        from libbasemodel.form import formStockManager
        result = self.session.query(
            formStockManager.stock_code,
            formStockManager.flag
            ).filter_by(stock_code=stock_code)
        if result:
            result.update(
                {"flag": flag_type}
            )
            self.session.commit()
        return 1


if __name__ == "__main__":
    pass
