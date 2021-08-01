#!/usr/bin/python3

from libnlp.dataset.cner import DataEngine
from libstrategy.data_engine.data_engine import StockData
from libmysql_utils.header import GLOBAL_HEADER


Data = StockData(GLOBAL_HEADER, '1990-12-19', '2021-7-23')
data = Data._get_data('SH000001', '1990-12-19', '2021-7-23')
# print(data)

import numpy as np
from scipy.fftpack import fft, fftfreq
import matplotlib.pyplot as plt
from matplotlib.pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']   #显示中文
mpl.rcParams['axes.unicode_minus']=False       #显示负号



log_p = np.log(data['SH000001'])
#.rolling(20).mean())
log_diff_p = log_p.diff(21)
log_diff_p = log_diff_p.dropna()
#print(log_diff_p)
#print(diff_p)
#list_diff = diff_p.tolist()
#print(list_diff.index(max(list_diff)))
N = log_diff_p.shape[0]
print(N)
T = 354
w =  fftfreq(N, 1)[:N//2]
#print(w)
y = np.array(log_diff_p)
y1 = fft(y)
amp = 2/N * np.abs(y1[:N//2])

fig, ax = plt.subplots(figsize=(9,3))
ax.plot(amp)
#for a,b in zip(w[:30], amp[:30]):
#    print(168 * a,b)
plt.show()
