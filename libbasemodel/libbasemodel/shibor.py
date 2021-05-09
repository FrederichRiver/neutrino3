#!/usr/bin/python38
import pandas as pd
import re
from libmysql_utils.mysql8 import mysqlHeader
from libbasemodel.stock_model import StockBase
from dev_global.env import TIME_FMT
from mars.log_manager import log_wo_return


class ShiborData(StockBase):
    """
    API : @get_shibor_data(df), df is shibor data.
    """
    def __init__(self, header: mysqlHeader) -> None:
        super(ShiborData, self).__init__(header)
        self._last_update_date = pd.Timestamp('2004-01-01')
        self._url = ""

    @property
    def last_update_date(self):
        release_date = self.select_values('shibor', 'release_date')
        if not release_date.empty:
            d = list(release_date[0])
            result_date = pd.Timestamp(d[-1])
        else:
            result_date = pd.Timestamp('2004-01-01')
        self._last_update_date = result_date

    @property
    def shibor_url(self):
        return self._url

    @shibor_url.setter
    def shibor_url(self, month: str):
        """
        Usage: self.shibor_url = month in format of 'yyyy-mm'
        """
        y, m = re.split('-', month)
        self._url = (
            f"http://www.shibor.org/shibor/web/html/"
            f"downLoad.html?nameNew=Historical_Shibor_Data_{y}_{m}.xls"
            f"&nameOld=Shibor%CA%FD%BE%DD{y}_{m}.xls"
            f"&shiborSrc=http%3A%2F%2Fwww.shibor.org%2Fshibor%2F&downLoadPath=data")

    @log_wo_return
    def get_shibor_data(self, df: pd.DataFrame):
        if not df.empty:
            df.columns = [
                    'release_date', 'overnight', 'one_week', 'two_week',
                    'one_month', 'three_month', 'six_month', 'nine_month', 'one_year']
            df['release_date'] = pd.to_datetime(df['release_date'], format=TIME_FMT)
            # filter the datetime already updated.
            for _, row in df.iterrows():
                sql = (
                        f"INSERT IGNORE INTO shibor "
                        f"(release_date,overnight,one_week,two_week,one_month,three_month,six_month,nine_month,one_year) "
                        f"VALUES ("
                        f"'{row['release_date']}',{row['overnight']},"
                        f"{row['one_week']},{row['two_week']},{row['one_month']},{row['three_month']},"
                        f"{row['six_month']},{row['nine_month']},{row['one_year']})"
                    )
                self.engine.execute(sql)

    @classmethod
    def month_list(cls, from_date='2006-10', to_date=None):
        """
        Generate month list for url.
        """
        from datetime import datetime
        month_list = []
        if from_date:
            y1, m1 = re.split('-', from_date)
        if not to_date:
            to_date = datetime.now()
            y2 = to_date.year
            m2 = to_date.month
        else:
            y2, m2 = re.split('-', to_date)
        m = int(m1)
        for y in range(int(y1), int(y2)):
            while m < 13:
                month_list.append(f"{y}-{m}")
                m += 1
            m = 1
        for m in range(1, int(m2)+1):
            month_list.append(f"{y2}-{m}")
        return month_list

    @property
    def current_month(self):
        """
        Return current month in format 2021-2
        """
        import datetime
        to_date = datetime.datetime.now()
        y = to_date.year
        m = to_date.month
        return f"{y}-{m}"


if __name__ == '__main__':
    """import pandas
    from libmysql_utils.mysql8 import GLOBAL_HEADER
    event = ShiborData(GLOBAL_HEADER)
    year_list = range(2006, pandas.Timestamp.today().year + 1)
    year = 2021
    event.shibor_url = f"{year}-2"
    df = event.get_excel_object(event.shibor_url)
    event.get_shibor_data(df)"""
    # service_get_shibor()
