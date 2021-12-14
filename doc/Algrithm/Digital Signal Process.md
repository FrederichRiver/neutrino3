# Digital Signal Process

## Mind Graph

## Dilichlet条件

## Laplace Transform

因为傅立叶变换必须满足Dilichlet条件，因此对于不满足绝对可积条件的函数，乘以一个快速衰减的函数，从而满足绝对可积条件。进一步可以采用傅立叶变换进行变换。

$$\lim_{x\rightarrow+\infty}f(x)e^{-\sigma x}=0,\sigma\in \Bbb R$$
为了保证$e^{-\sigma x}$一直衰减，我们把x定义到正半轴，这样可以用傅立叶变换为：
$$F(\omega)=\int^{+\infty}_{0} f(t)e^{-\sigma t} e^{-i\omega t}dt=\int^{+\infty}_{0} f(t)e^{-(\sigma + i\omega )t}dt$$

如果假设$s=\sigma + \omega$，得到拉普拉斯变换如下：
$$F(\omega)=\int^{+\infty}_{0} f(t)e^{-st}dt$$
