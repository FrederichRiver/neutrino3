#!/usr/bin/python3
import pandas as pd
from venus.stock_base import StockEventBase


class markov_stratagy(StockEventBase):
    # def __init__(self, header):
    #    super(StockEventBase, markov_stratagy).__init__(header)

    def run(self):
        import matplotlib.pyplot as plt
        stock_list = self.get_all_stock_list()
        result = []
        for stock_code in stock_list[:150]:
            amp = self.mysql.select_values(stock_code, 'amplitude')
            if not amp.empty:
                amp = amp[0].tolist()
                # print(amp)
                for i in range(len(amp)-2):
                    if amp[i] > 9:
                        # result.append(amp[i+1] + amp[i+2] + amp[i+3])
                        result.append(amp[i+1])
        result_df = pd.Series(result)
        stat = result_df.std()
        print(stat)
        print(result_df.describe())
        result_df.plot.hist()
        plt.show()


if __name__ == "__main__":
    from dev_global.env import GLOBAL_HEADER
    event = markov_stratagy(GLOBAL_HEADER)
    event.run()
