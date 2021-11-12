#!/usr/bin/python3

from libmysql_utils.header import LOCAL_HEADER
from libbasemodel.database_manager import StockBase
from pandas import DataFrame
import matplotlib.pyplot as plt
from scipy.fft import fft
import numpy as np
import math



s = StockBase(LOCAL_HEADER)
data = s.engine.execute(f"SELECT current_month FROM ppi").fetchall()
x = DataFrame(data)
x.columns = ['ppi']

# plt.show()
t = np.linspace(0, 5000, 182)
x = np.array(x['ppi'])
plt.plot(t, x)
y = fft(x)
print(y)
# y = [i if i > 50 else 0 for i in y]
z = 0
for j in range(len(y)):
    z += np.cos(6.28* j * t / 182) * y[j]
z = z / 182
plt.plot(t, z)
plt.show()
