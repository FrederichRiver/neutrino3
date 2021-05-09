#!/usr/bin/python3

from hmmlearn.hmm import GaussianHMM
from numpy.core.fromnumeric import size
from venus.stock_base import StockEventBase
from dev_global.env import GLOBAL_HEADER
import numpy as np


event = StockEventBase(GLOBAL_HEADER)
df = event.mysql.select_values('SH600000', 'trade_date,close_price,amplitude,volume')
df.columns = ['trade_date', 'close', 'amp', 'volume']
# print(df.head(5))

close = np.array(df['close'])
diff = np.diff(df['close'])
amp = np.array(df['amp'])
vol = np.array(df['volume'])

A = np.column_stack([close[:500], vol[:500], amp[:500]])
B = np.column_stack([close[-500:], vol[-500:], amp[-500:]])
print(size(A))
print(size(diff[:500]))
model = GaussianHMM(n_components=2, covariance_type='full', n_iter=2000).fit([diff])
print(model.startprob_)
# print(model.transmat_)
# print(model.means_)
# print(model.covars_)
