#!/usr/bin/python3

from libmysql_utils.header import LOCAL_HEADER, REMOTE_HEADER
from libbasemodel.database_manager import StockBase
from pandas import DataFrame
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft
import numpy as np
import math



s = StockBase(REMOTE_HEADER)
data = s.engine.execute(f"SELECT trade_date,close_price FROM SH000300").fetchall()
x = DataFrame(data)
x.columns = ['report_date','sh']
x.set_index('report_date')
n = 250
x['rate'] = x['sh'].diff(n) / x['sh'].shift(n)
# print(x.head(10))
# plt.plot(x.index, x['rate'])
# plt.show()
s = np.array(x['rate'].dropna())
y = fft(s[1:])
# 滤波
y1 = [i if i > 20 else 0 for i in y]
y2 = [i if i > 50 else 0 for i in y]
y3 = [i if i > 200 else 0 for i in y]
#plt.plot(y[:50])
#plt.show()
amp = y3[0]
print(len(y3))
z1 = ifft(y1)
z2 = ifft(y2)
z3 = ifft(y3)
plt.plot(s)
plt.plot(z1)
plt.plot(z2)
plt.plot(z3)
plt.show()
if len(y) // 2:
    print(len(y),1)
    half = int((len(y) + 1)/2)
else:
    print(len(y),0)
    half = int(len(y) / 2)
#print(half)
#print(y[half-1])
#print(y[half])
#print(y[half+1])
max = 0
max_id = 0
for j in range(10):
    for i in range(half):
        if max < y[i]:
            max = y[i]
            max_id = i
            y[i] = 0
    if max_id:
        print(f"{max_id}, {max},{len(y)/(5 * max_id)} days, {len(y)/(25 * max_id)} weeks, {len(y)/(110 * max_id)} month.")
    else:
        print(f"{max_id}, {max}")
    max_id = 0
    max = 0

d1 = s[:2000]
d2 = s[:3000]
d3 = s[:3500]

f1 = fft(d1)
f2 = fft(d2)
f3 = fft(d3)
for i in range(len(f1)):
    if abs(f1[i]) < 200:
        f1[i] = 0
for i in range(len(f2)):
    if abs(f2[i]) < 200:
        f2[i] = 0
for i in range(len(f3)):
    if abs(f3[i]) < 200:
        f3[i] = 0

x1 = ifft(f1)
x2 = ifft(f2)
x3 = ifft(f3)
N = len(f3)
print(N)
H = int(N/2)
a0 = f3[0] + f3[H]
dfs = 1/158
param = []
for i in range(H):
    if f3[i] != 0:
        A = 2 * math.sqrt((f3[i].real)**2 + (f3[i].imag)**2) / N
        phi = math.atan(f3[i].imag / f3[i].real)
        omg = dfs * (i + 1)
        param.append({"amp": A, "p": phi, "w": omg})
        print(f"{i},{A},{omg},{phi}")
def fourier(param, n):
    result = a0
    for item in param:
        t = item["amp"] * math.cos(6.28*n/N + item["p"])
        result += t
    return result
# x = np.linspace(1, 3800)
y = np.array([fourier(param, i) for i in range(1,3800)])

#plt.plot(s)
#plt.plot(x1)
#plt.plot(x2)
#plt.plot(x3)
plt.plot(y)
plt.show()
