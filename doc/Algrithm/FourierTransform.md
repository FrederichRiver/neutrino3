# 傅立叶变换 Fourier Transform

## 傅立叶级数

### 以$2\pi$为周期的函数的傅立叶级数

对于一个以$2\pi$为周期的函数，可以表达为傅立叶级数的形式：
$$
f(t)=\frac{a_0}{2}+\sum^{\infty}_{n=1}[a_n cos(n\omega t)+b_n sin(n\omega t)]
$$
其中：
$$a_n = \frac {1}{\pi} \int^{\pi}_{-\pi} f(t)cos(kt)dt$$
$$b_n = \frac {1}{\pi} \int^{\pi}_{-\pi} f(t)sin(kt)dt$$

### 以2T为周期的函数的傅立叶级数

对于一个以2T为周期的函数，可以表达为傅立叶级数的形式：
$$
f(t)=\frac{a_0}{2}+\sum^{\infty}_{n=1}[a_n cos(\frac{n\pi t}{T})+b_n sin(\frac{n\pi t}{T})]
$$
其中：
$$a_n = \frac {1}{T} \int^{T}_{-T} f(t)cos(\frac{n\pi t}{T})dt$$
$$b_n = \frac {1}{T} \int^{T}_{-T} f(t)sin(\frac{n\pi t}{T})dt$$

### 傅立叶级数的复数形式

利用欧拉公式$e^{ix}=cosx+isinx$

$$
f(t)=\frac{a_0}{2}+\sum^{\infty}_{n=1} {[(a_n-ib_n)e^{i(\frac{n\pi t}{T})}+(a_n+ib_n)e^{-i(\frac{n\pi t}{T})}]}
$$
令：
$$C_0=\frac{a_0}{2},C_n=\frac{a_n-ib_n}{2},C_{-n}=\frac{a_{-n}+ib_{-n}}{2}$$
有：
$$
f(t)=\sum^{+\infty}_{-\infty}{C_ne^{-i\frac{n\pi t}{T}}}
$$
$$C_n=\int^{T}_{-T}{f(x)e^{-i\frac{n\pi x}{T}}dx}$$

### 傅立叶变换

对于傅立叶级数的复数形式，令$\omega=\frac{2\pi}{N}$,$\omega_x=n\omega$

则傅立叶级数可以转换为：
$$
\begin{equation}\begin{split}
f(t)&=\frac{1}{2T}\sum^{+\infty}_{-\infty}(\int^T_{-T}{f(t)e^{-in\omega t}dt})e^{-in\omega t} \\
&=\frac{1}{2T}\sum^{+\infty}_{-\infty}F(\omega_x)e^{-i\omega_x t} \\
&=\frac{N}{4\pi T}\sum^{+\infty}_{-\infty}F(\omega_x)e^{-i\omega_x t} \frac{2\pi}{N} \\
&=\frac{N}{4\pi T}\int^{+\infty}_{-\infty}F(\omega_x)e^{-i\omega_x t}d\omega_x
\end{split}\end{equation}
$$
其中$$F(\omega_x)=\int^{T}_{-T}f(t)e^{-i\omega_x t}dt$$
为$f(t)$的傅立叶变换。

## 离散傅立叶变换DFT

对傅立叶变换进行离散化，积分变为求和。令：
$$\omega_x=\frac{2\pi}{N}n$$
得到：
$$
\begin{equation}\begin{split}
f(t)&=\frac{N}{4\pi T}\sum^{+\infty}_{-\infty}[F(\omega_x)e^{-i\omega_x t}\frac{2\pi}{N}] \\
&=\frac{1}{2T}\sum^{N}_{n=0}[F(n)e^{-i(\frac{2\pi n}{N}t)}] \\
&=\sum^{N}_{n=0}[\frac{1}{N}F(n)e^{-i(\frac{2\pi n}{N}t)}] \\
\end{split}\end{equation}
$$

下式为离散傅立叶变换DFT：
$$
f(t)=\sum^{N}_{n=0}[\frac{1}{N}F(n)e^{-i(\frac{2\pi n}{N}t)}]
$$
其中$F(n)$可以表示为离散傅立叶逆变换iDFT：
$$F(n)=\sum^{N}_{t=0}f(t)e^{-i(\frac{2\pi n}{N})t}$$

### 离散傅立叶变换的矩阵形式

离散傅立叶变换可以表达为矩阵形式：
$$
\begin{bmatrix}
f(1)\\f(2)\\\vdots\\f(N)
\end{bmatrix}
\begin{bmatrix}
W^{1}_{1}&W^{1}_{2}&\cdots&W^{1}_{N}\\
W^{2}_{1}&W^{2}_{2}&\cdots&W^{2}_{N}\\
\vdots&\vdots&\ddots&\vdots\\
W^{N}_{1}&W^{N}_{2}&\cdots&W^{N}_{N}\\
\end{bmatrix}=
\begin{bmatrix}
F(1)\\F(2)\\\vdots\\F(N)
\end{bmatrix}
$$
其中$$W^{n}_{t}=e^{-i(\frac{2\pi n}{N})t}$$

### 离散傅立叶变换的参数含义

* $F(n)$为实部，表示直流分量，虚部相加为零。
* $a_0$与各直流分量相加和表示信号强度。
* 在$k_c$点的频率分量，其频率为$2\pi k_c f_s/N=2\pi f$。其中$X[k_c]$代表频率为$f=k_c f_s/N$的频率分量。$f_s$为采样频率，$k_c$为第$k_c$个点，$f$为真实频率。

例：以PPI采购经理指数为例，以月频为1Hz。其发布为月频，采样周期为1M，采样频率为1Hz。样本为N=158个点。
则真实频率为$f=n\times1/158=6.3n \times 10^{-3}$Hz
分别是：
|n|频率(Hz)|月数|
|:-:|:-:|:-:|
|1|0.0063|158|
|2|0.0126|79|
|3|0.0189|52.7|
|4|0.0252|38.5|
|6|0.0378|26.3|
|8|0.0504|19.3|
|16|0.1012|9.9|
|32|0.2024|4.9|
|64|0.4048|2.5|
|128|0.8096|1.2|
|158|1|1|

