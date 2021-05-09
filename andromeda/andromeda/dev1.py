#!/usr/bin/python38

import numpy as np
from libbasemodel.stock_model import StockBase
from libmysql_utils.mysql8 import LOCAL_HEADER
from hmmlearn.hmm import GaussianHMM
"""
for mean and variance of volatility in last 7 days,
stat 1 means amplitude is positive in the next 5 days,
stat 0 means amplitude is negative in the next 5 days.
"""
X = 7
Y = 5
stock_code = "SH600000"
event = StockBase(LOCAL_HEADER)
df = event.select_values(stock_code, 'amplitude,open_price,close_price,high_price,low_price')
df.columns = ['amplitude', 'open', 'close', 'high', 'low']
df['amplitude'] = 1 + 0.01 * df['amplitude'].copy()
df['log'] = df['amplitude'].apply(np.log)
df['close'] = df['close'].copy() / df['open']
df['high'] = df['high'].copy() / df['open']
df['low'] = df['low'].copy() / df['open']
df.dropna(axis=0, inplace=True)
print(df.head(5))
C = -100
train_data = df[:C]
test_data = df[C:]
X = np.column_stack([train_data['close'], train_data['high'], train_data['low'], train_data['log']])
Y = np.column_stack([test_data['close'], test_data['high'], test_data['low'], test_data['log']])
model = GaussianHMM(n_components=2, n_iter=1000)
model.fit(X)
h = model.predict(Y)
print(h)
import matplotlib.pyplot as plt
ax1 = plt.subplot(211)
ax1.plot(h)
ax2 = plt.subplot(212)
ax2.plot(test_data['close'])
plt.show()
