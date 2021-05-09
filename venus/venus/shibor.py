#!/usr/bin/python38
import pandas as pd
from venus.stock_base2 import StockBase
from dev_global.env import TIME_FMT
from mars.log_manager import log_decorator2


class EventShibor(StockBase):
    """
    API : @get_shibor_data(df), df is shibor data.
    """
    def get_shibor_url(self, year):
        url = (
            f"http://www.shibor.org/shibor/web/html/"
            f"downLoad.html?nameNew=Historical_Shibor_Data_{year}.xls"
            f"&downLoadPath=data&nameOld=1{year}.xls"
            f"&shiborSrc=http://www.shibor.org/shibor/")
        return url

    def get_last_update(self):
        release_date = self.select_values('shibor', 'release_date')
        if not release_date.empty:
            d = list(release_date[0])
            result_date = pd.Timestamp(d[-1])
        else:
            result_date = pd.Timestamp('2004-01-01')
        return result_date

    @log_decorator2
    def get_shibor_data(self, df: pd.DataFrame):
        if not df.empty:
            df.columns = [
                    'release_date', 'overnight', '1W', '2W',
                    '1M', '3M', '6M', '9M', '1Y']
            df['release_date'] = pd.to_datetime(df['release_date'], format=TIME_FMT)
            # get the last update date
            last_update = self.get_last_update()
            # filter the datetime already updated.
            df = df[df['release_date'] > last_update]
            # print(df)
            for index, row in df.iterrows():
                sql = (
                        f"INSERT IGNORE INTO shibor "
                        f"(release_date,overnight,1W,2W,1M,3M,6M,9M,1Y) "
                        f"VALUES ("
                        f"'{row['release_date']}',{row['overnight']},"
                        f"{row['1W']},{row['2W']},{row['1M']},{row['3M']},"
                        f"{row['6M']},{row['9M']},{row['1Y']})"
                    )
                self.engine.execute(sql)


if __name__ == '__main__':
    pass
