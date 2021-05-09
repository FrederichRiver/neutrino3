# Kalman Filter

## Propability Graph Model

## Dynamic Model

```mermaid
graph LR
    A --> B
    B --> C

```

转移概率(transition propability)
发射概率(emission propability)
初始状态概率(initial propability)

||$P(x_t$ &#124;$x_{t-1})$|$P(y_t$ &#124; $x_t)$|$P(x_1)$|
|:-|--|--|--|
|Discrete Dynamic Model</br>**Hidden Markov Model**|$A_{x_{t-1},x_t}$|B|$\pi$|
|**Kalman Filter**</br>Linear,Gaussian|$N(Ax_t+B,Q)$|$N(Hx_t+C,R)$|$N(\mu,\epsilon)$|
|**Paritial Filter**</br>Non-linear, Non-Gaussian|$f(x_{t-1})$|$g(y_{t})$|$f_0(x_1)$|

$x_t=Ax_{t-1}+B+w$  其中  $w \sim N(0, Q)$
$y_t=Cx_t+D+v$  其中  $v \sim N(0,R)$

$$
\begin{aligned}
P(x_t|y_1,...,y_t) &\propto P(x_t,y_1,...,y_t)\\
&\propto P(y_t|x_t,y_1,...,y_{t-1}) \times P(x_t|y_1,...,y_{t-1})\\
&=P(y_t|x_t) \times P(x_t|y_1,...,y_{t-1})\\
&=P(y_t|x_t) \times \int_{x_{t-1}} {P(x_t,x_{t-1}|y_1,...,y_{t-1})}{dx_{t-1}}\\
&\propto P(y_t|x_t) \times \int_{x_{t-1}} {P(x_t|x_{t-1},y_1,...,y_{t-1})P(x_{t-1}|y_1,...y_{t-1})}{dx_{t-1}}
\end{aligned}
$$

$$
N(\hat{\mu_t}, \hat{\Sigma_t})
$$
