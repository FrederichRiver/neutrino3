#!/usr/bin/python3
from venus.stock_base import StockEventBase


class Stratagy(StockEventBase):
    def get_close_price_data(self, stock_code):
        df = self.mysql.select_values('SH000300', 'trade_date,close_price')
        # data cleaning
        df.columns = ['trade_date', 'close_price']
        pd.to_datetime(df['trade_date'], format=TIME_FMT)
        df.set_index('trade_date', inplace=True)
        # data constructing
        df['shift'] = df['close_price'].shift(1)
        df['amplitude'] = df['close_price'] / df['shift']
        df['ln_amplitude'] = np.log(df['amplitude'])
        df.dropna(inplace=True)
        return df

    def baseline(self):
        import pandas as pd
        import math
        import numpy as np
        from dev_global.env import TIME_FMT
        df = self.mysql.select_values('SH000300', 'trade_date,close_price')
        # data cleaning
        df.columns = ['trade_date', 'close_price']
        pd.to_datetime(df['trade_date'], format=TIME_FMT)
        df.set_index('trade_date', inplace=True)
        # data constructing
        df['shift'] = df['close_price'].shift(1)
        df['amplitude'] = df['close_price'] / df['shift']
        df['ln_amplitude'] = np.log(df['amplitude'])
        df.dropna(inplace=True)
        # print(df.head(5))
        # plot
        input_df = df['ln_amplitude'][-200:]
        import statsmodels.tsa.api as smt
        acf = smt.stattools.acf(input_df, nlags=40)
        pacf = smt.stattools.pacf(input_df, nlags=40)
        acf_pacf_plot(input_df, lags=40)
        from statsmodels.stats.diagnostic import unitroot_adf
        result = unitroot_adf(input_df)
        print(result[1])

    def baseline_view(self):
        import pandas as pd
        import math
        from dev_global.env import TIME_FMT
        df = self.mysql.select_values(
            'SH000300',
            'trade_date,open_price,close_price,highest_price,lowest_price')
        # data cleaning
        df.columns = ['trade_date', 'open', 'close', 'high', 'low']
        pd.to_datetime(df['trade_date'], format=TIME_FMT)
        df.set_index('trade_date', inplace=True)
        # data constructing
        print(df.head(5))
        # plot
        plt = self.kplot(df[-50:])
        plt.show()

    def series_plot(self, df):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(df)
        ax.set_title('Shanghai 300 stocks', fontsize=18)
        ax.set_xlabel('date')
        ax.set_ylabel('index')
        return plt

    def kplot(self, df):
        import matplotlib.pyplot as plt
        from mpl_finance import candlestick_ochl as kplot
        from matplotlib.dates import date2num
        from datetime import timedelta
        fig, ax = plt.subplots()
        plt.xticks(rotation=45)
        plt.yticks()
        ax.xaxis_date()
        data_list = []
        for dt, row in df.iterrows():
            t = date2num(dt)
            op, cl, high, low = row[:4]
            # print(dt, row[:4])
            data = (t, op, cl, high, low)
            data_list.append(data)
        try:
            kplot(
                ax, data_list,
                width=1.0, colorup='r', colordown='green', alpha=0.75)
        except Exception as e:
            pass
            # print(e)
        # plt.show()
        return plt

    def ar(self, df, p=1):
        pass

    def garch(self, df, m=1, s=1):
        pass


def acf_pacf_plot(data, lags=None):
    import pandas as pd
    import matplotlib.pyplot as plt
    import statsmodels.tsa.api as smt
    # 判断是否为pandas的Series格式数据
    if not isinstance(data, pd.Series):
        data = pd.Series(data)
    # 设定画面风格，这里设置为'bmh', colspan=2
    with plt.style.context('bmh'):
        fig = plt.figure(figsize=(10, 8))
        # 设置子图
        layout = (3, 1)
        ts_ax = plt.subplot2grid(layout, (0, 0))
        acf_ax = plt.subplot2grid(layout, (1, 0))
        pacf_ax = plt.subplot2grid(layout, (2, 0))
        data.plot(ax=ts_ax)
        ts_ax.set_title('时间序列图')
        smt.graphics.plot_acf(data, lags=lags, ax=acf_ax, alpha=0.5)
        acf_ax.set_title('自相关系数')
        smt.graphics.plot_pacf(data, lags=lags, ax=pacf_ax, alpha=0.5)
        pacf_ax.set_title('偏自相关系数')
        plt.tight_layout()
        plt.show()
    return


class timeSeries(object):
    def __init__(self, df):
        import pandas
        self.df = pandas.DataFrame()
        if isinstance(df, pandas.core.series.Series):
            self.df['x'] = df
        else:
            raise TypeError

    def ar_fit(self, df, p):
        """
        Fit input df -> dataframe using AR model.
        """
        df = self.df
        import numpy as np
        for i in range(p):
            df[f"x{-i-1}"] = df['x'].shift(i+1)
        # print(self.df.head(5))
        df.dropna(how='any', inplace=True)
        b = df['x']
        # print(b)
        A = df.drop('x', axis=1)
        # print(A)
        b = np.array(b)
        A = np.array(A)
        M = np.linalg.inv(A.T.dot(A))
        N = M.dot(A.T)
        a = N.dot(b)
        for i in range(p):
            print(a[i])
        return a, df

    def ar(self, df, a, p):
        df['y'] = 0
        for i in range(p):
            df['y'] += a[i] * df[f"x-{i+1}"]
        df['e'] = df['x'] - df['y']
        # print(df.head(20))
        return df

    def hypo_analysis(self, e, m=15):
        import statsmodels.tsa.api as smt
        from statsmodels.stats.diagnostic import unitroot_adf
        acf = smt.stattools.acf(ts.df['e'], nlags=m)
        pacf = smt.stattools.pacf(ts.df['e'], nlags=m)
        acf_pacf_plot(ts.df['e'], lags=m)

    def test_plot(self, x):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x)
        ax.set_title('Shanghai 300 stocks', fontsize=18)
        ax.set_xlabel('date')
        ax.set_ylabel('index')
        plt.show()

    def _get_best_model(self, TS):
        import statsmodels.tsa.api as smt
        import numpy as np
        best_aic = np.inf
        best_order = None
        best_mdl = None

        pq_rng = range(5)
        d_rng = range(2)
        for i in pq_rng:
            for d in d_rng:
                for j in pq_rng:
                    try:
                        tmp_mdl = smt.ARIMA(TS, order=(i, d, j)).fit(
                            method='mle', trend='c', disp=-1
                        )
                        tmp_aic = tmp_mdl.aic
                        if tmp_aic < best_aic:
                            best_aic = tmp_aic
                            best_order = (i, d, j)
                            best_mdl = tmp_mdl
                    except Exception:
                        continue
        # print('aic: {:6.5f} | order: {}'.format(best_aic, best_order))
        return best_aic, best_order, best_mdl


def ar_process():
    from dev_global.env import GLOBAL_HEADER
    # event = Stratagy(GLOBAL_HEADER)
    # event.baseline()
    # event.baseline_view()
    import pandas as pd
    import math
    import numpy as np
    from dev_global.env import TIME_FMT
    event = StockEventBase(GLOBAL_HEADER)
    df = event.mysql.select_values('SH000300', 'trade_date, amplitude')
    # data cleaning
    df.columns = ['trade_date', 'amplitude']
    pd.to_datetime(df['trade_date'], format=TIME_FMT)
    df.set_index('trade_date', inplace=True)
    # data constructing
    df['ln_amplitude'] = np.log(df['amplitude'])
    df.dropna(inplace=True)
    df = df[-90:]
    ts = timeSeries(df['ln_amplitude'])
    n = 4
    m = 10
    a, x = ts.ar_fit(df['ln_amplitude'], n)
    result = ts.ar(x, a, n)
    predic = pd.DataFrame()
    predic['x'] = result['x']
    predic['y'] = result['y']
    ts.test_plot(predic)
    ts.hypo_analysis(result['e'])


def tsplot(y, lags=None, figsize=(10, 8), style='bmh'):
    import statsmodels.tsa.api as smt
    import matplotlib.pyplot as plt
    import statsmodels.api as sm
    import scipy.stats as scs
    if not isinstance(y, pd.Series):
        y = pd.Series(y)
    with plt.style.context(style):
        fig = plt.figure(figsize=figsize)
        # mpl.rcParams['font.family'] = 'Ubuntu Mono'
        layout = (3, 2)
        ts_ax = plt.subplot2grid(layout, (0, 0), colspan=2)
        acf_ax = plt.subplot2grid(layout, (1, 0))
        pacf_ax = plt.subplot2grid(layout, (1, 1))
        qq_ax = plt.subplot2grid(layout, (2, 0))
        pp_ax = plt.subplot2grid(layout, (2, 1))

        y.plot(ax=ts_ax)
        ts_ax.set_title('Time Series Analysis Plots')
        smt.graphics.plot_acf(y, lags=lags, ax=acf_ax, alpha=0.5)
        smt.graphics.plot_pacf(y, lags=lags, ax=pacf_ax, alpha=0.5)
        sm.qqplot(y, line='s', ax=qq_ax)
        qq_ax.set_title('QQ Plot')
        scs.probplot(y, sparams=(y.mean(), y.std()), plot=pp_ax)

        plt.tight_layout()
        # fig.show()
    return fig


if __name__ == "__main__":
    from dev_global.env import GLOBAL_HEADER
    from arch import arch_model
    event = Stratagy(GLOBAL_HEADER)
    event.baseline()
    event.baseline_view()
    """
    import pandas as pd
    import math
    import numpy as np
    from dev_global.env import TIME_FMT
    import datetime
    event = StockEventBase(GLOBAL_HEADER)
    df = event.mysql.select_values('SH600000', 'trade_date, amplitude')
    # data cleaning
    df.columns = ['trade_date', 'amplitude']
    pd.to_datetime(df['trade_date'], format=TIME_FMT)
    df.set_index('trade_date', inplace=True)
    # data constructing
    df['ln_amplitude'] = np.log(df['amplitude']+1)
    df.dropna(inplace=True)
    input_df = df[-120:-1]
    base_line = df[-90:]
    ts = timeSeries(input_df['ln_amplitude'])
    # print(ts.df)
    # Notice I've selected a specific time period to run this analysis
    # res_tup = ts._get_best_model(ts.df)
    # p=1, o=1, q=2
    # p = res_tup[1][0]
    # o = res_tup[1][1]
    # q = res_tup[1][2]
    # print(p, o, q)
    # am = arch_model(input_df['ln_amplitude'], p=1, o=1, q=2, dist='StudentsT')
    am = arch_model(ts.df, p=1, o=1, q=2, dist='StudentsT')
    res = am.fit(update_freq=5, disp='off')
    # fig = tsplot(res.resid, lags=30)
    # fig.show()
    result = res.forecast(params=None, horizon=1)
    plot_df = base_line['ln_amplitude']
    temp_result = result.variance
    temp_result = temp_result.dropna()
    print(ts.df)
    print(plot_df.tail(10))
    print(temp_result)
    """
    """
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(plot_df)
    ax.set_title('Shanghai 300 stocks', fontsize=18)
    ax.set_xlabel('date')
    ax.set_ylabel('index')
    plt.show()
    while 1:
        pass
    """
