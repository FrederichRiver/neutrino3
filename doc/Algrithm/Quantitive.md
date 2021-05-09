# Quantitive Investment

## 先锋资产配置模型

1. 假定投资者长期投资，10年以上
2. 假定投资于美股市场
3. 假定市场有效，被动投资，不进行主动管理或收益增强
4. 假定不会产生超额收益Alpha
5. 人工划分投资者类型
6. 人工选定给定投资者类型下的大类资产配置权重
7. 人工确定大类资产下固定对应某个ETF
8. 对交易时间和短期交易价格不敏感
9. 年度调仓回顾

## Markowitz模型

预期收益： $$E(R_p)=\sum_iw_iE(R_i)$$
组合收益方差： $$\sigma_p^2=\sum_iw_i^2\sigma_i^2 + \sum_i\sum_{j \ne i}w_iw_j\sigma_i\sigma_j\rho_(ij)$$
组合波动率： $$\sigma_p=\sqrt {\sigma_p^2}$$

有效前沿的计算方法:
$$R-N(\mu, \sigma)$$
$$R=[r_1,r_2,\cdots,r_n]^T$$
$$w_{\lambda}=argmax\lbrace w^T\mu-\lambda w^T\sum w\rbrace$$
$$w=[w_1,w_2,\cdots,w_n]^T$$ 有$$w_i\ge0,i\in\lbrace1,\cdots,n\rbrace, \sum_i w_i=1$$
$$\lambda\in[0,+\infty)$$

参数估计方法一：历史样本估计
参数估计方法二：多因子模型APT方法
$$E(r_{i,T+1})=\epsilon_i+\sum_{j=1}^m\beta_{i,j}f_{i,j}$$
用CAPM模型$$E(r_{i,T+1})=r_f+\beta_i(r_M-r_f)+\epsilon_i$$
参数估计方法三：Bootstrapping
参数估计方法四：贝叶斯估计
先验估计：$$\mu|\Sigma ~ N(\mu,\frac{\Sigma}{\kappa})$$
后验分布：
Shrinkage: $$\Sigma^{shrinkage}=\lambda \Sigma^* +(1-\lambda)A$$
扩展：
* Mean-VaR 模型
* Mean-SemiDev
* MC Sampling
* RMT(Random Matrix Theory)
* Black-Litterman Model

## Black-Litterman Model

## Merrill Lynch Investment Clock

