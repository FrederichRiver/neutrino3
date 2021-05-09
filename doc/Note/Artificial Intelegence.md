# 人工智能

[toc]

## 第一部分：机器学习基础

### 第一章：自然语言处理概述

* 自然语言处理的现状与前景
* 自然语言处理应用
* 自然语言处理经典任务

### 第二章：数据结构与算法基础

* 时间复杂度、空间复杂度
* 动态规划
* 贪心算法
* 各种排序算法

### 第三章：分类与逻辑回归

* 逻辑回归
* 最大似然估计
* 优化与梯度下降法
* 随机梯度下降法

### 第四章：模型泛化与调参

* 理解过拟合、防止过拟合
* L1与L2正则
* 交叉验证
* 正则与MAP估计

### 第五章：机器学习框架

#### 5.1 Pytorch


## 第二部分：自然语言处理

### 第五章：文本预处理与表示

* 各类分词算法
* 词的标准化
* 拼写纠错、停用词
* 独热编码表示
* tf-idf与相似度
* 分布式表示与词向量
* 词向量可视化与评估

### 第六章：词向量技术

* 独热编码的优缺点
* 分布式表示的优点
* 静态词向量与动态词向量
* SkipGram与CBOW
* SkipGram详解
* Negative  Sampling

### 第七章：语言模型

* 语言模型的作用
* 马尔科夫假设
* UniGram, BiGram, NGram模型
* 语言模型的评估
* 语言模型的平滑技术

## 第三部分：序列模型

### 第八章：隐马尔科夫模型

* HMM的应用
* HMM的Inference
* 维特比算法
* 前向、后向算法
* HMM的参数估计详解

### 第九章：条件随机场

* 有向图与无向图
* 生成模型与判别模型
* 从HMM与MEMM
* MEMM中的标签偏置
* Log-Linear模型介绍
* 从Log-Linear到LinearCRF
* LinearCRF的参数估计

## 第四部分：深度学习与预训练

### 第十章：深度学习基础

* 理解神经网络
* 各种常见的激活函数
* 反向传播算法
* 浅层模型与深度模型对比
* 深度学习中的层次表示
* 深度学习中的过拟合

### 第十一章：RNN与LSTM

* 从HMM到RNN模型
* RNN中的梯度问题
* 梯度消失与LSTM
* LSTM到GRU
* 双向LSTM
* 双向深度LSTM
* LSTM模型的缺点

### 第十二章：Seq2Seq模型与注意力机制

Seq2Seq模型

Greedy Decoding

Beam Search

长依赖所存在的问题

#### 12.1 注意力机制

##### 12.1.1传统的编码器-解码器框架的挑战

首先，编码器必须将所有输入信息压缩成一个固定长度的向量ht，然后将其传递给解码器。使用一个固定长度的向量压缩长而详细的输入序列可能会导致信息丢失 [Cho et al., 2014a]。

其次，它无法对输入和输出序列之间的对齐进行建模，这是结构化输出任务（如翻译或汇总）的一个重要方面[Young et al., 2018]。从直觉上看，在sequence-to-sequence的任务中，我们期望输出的token受到输入序列的某个部分影响很大。然而，解码器缺乏任何机制在生成每个输出tokens时选择性地关注相关的输入tokens。

##### 12.1.2 注意力机制

注意模型旨在通过允许解码器访问整个编码的输入序列（h1，h2，…，ht）来减轻这些挑战。其核心思想是在输入序列上引入注意权重α，以优先考虑存在相关信息的位置集，以生成下一个输出token。

##### 12.1.3 四种注意力模型：


| Category | Type |
| - | - |
| Number of sequences | distingctive，co-attention，**self-attention** |
| Number of abstraction levels | single-level, multi-level |
| Number of positions | soft/global, hard, local |
| Number of representations | multi-representations, multi-dimensions |

##### 12.1.4 Multi-Head Self-Attention：

在每个子层中使用self-attention来关联token及其在相同输入序列中的位置。这种注意力机制被称为multi-head，因为几个注意力层是平行堆叠的，对相同输入序列进行不同的线性变换。这有助于模型捕获输入的各个方面并提高其表达能力。

### 第十三章：动态词向量与ELMo技术

* 基于上下文的词向量技术
* 图像识别中的层次表示
* 文本领域中的层次表示
* ELMo模型
* ELMo的预训练与测试
* ELMo的优缺点

### 第十四章：自注意力机制与Transformer

Transformer概述

理解自注意力机制

self-attension的计算方法

三个矩阵：Q（query）、K（key）、V（value）

$Q=XW^q$

$K=XW^k$

$V=XW^v$

位置信息的编码

理解Encoder和Decoder区别

理解Transformer的训练与预测

Transformer的缺点

### 第十五章：BERT与ALBERT

##### 15.1 自编码介绍

##### 15.2 Transformer Encoder

##### 15.3 Masked语言模型

##### 15.4 BERT模型

##### 15.5 BERT的不同训练方式

1. 随机mask一定词汇，让BERT去预测。使用[MASK]。
2. 上下文猜测。使用（[CLS] A sentence [SEP] B sentence）格式分隔两句话。

##### 15.6 ALBERT

### 第十六章：BERT的其它变种

* RoBERTa模型
* SpanBERT模型
* FinBERT模型
* 引入先验知识
* K-BERT
* KG-BERT## 第五部分：信息抽取与知识图谱篇

## 第五部分：信息抽取与知识图谱

### 第十七章：GPT与XLNet

* Transformer Encoder回顾
* GPT-1, GPT-2,  GPT-3
* ELMo的缺点
* 语言模型下同时考虑上下文
* Permutation LM
* 双流自注意力机制

### 第十八章：命名识别与实体消歧

* 信息抽取的应用和关键技术
* 命名实体识别
* NER识别常用技术
* 实体统一技术
* 实体消歧技术
* 指代消解

### 第十九章：关系抽取

* 关系抽取的应用
* 基于规则的方法
* 基于监督学习的方法
* Bootstrap方法
* Distant Supervision方法

### 第二十章：句法分析

* 句法分析的应用
* CFG介绍
* 从CFG到PCFG
* 评估语法树
* 寻找最好的语法树
* CKY算法

### 第二十一章：依存文法分析

* 从语法分析到依存文法分析
* 依存文法分析的应用
* 基于图算法的依存文法分析
* 基于Transition-based的依存文法分析
* 依存文法的应用案例

### 第二十二章：知识图谱

* 知识图谱的重要性
* 知识图谱中的实体与关系
* 非结构化数据与构造知识图谱
* 知识图谱设计
* 图算法的应用

## 第六部分：模型压缩与图神经网络

### 第二十三章：模型的压缩

* 模型压缩重要性
* 常见的模型压缩总览
* 基于矩阵分解的压缩技术
* 基于蒸馏的压缩技术
* 基于贝叶斯模型的压缩技术
* 模型的量化

### 第二十四章：基于图的学习

* 图的表示
* 图与知识图谱
* 关于图的常见算法
* Deepwalk和Node2vec
* TransE图嵌入算法
* DSNE图嵌入算法

### 第二十五章：图神经网络

* 卷积神经网络回顾
* 在图中设计卷积操作
* 图中的信息传递
* 图卷积神经网络
* 图卷积神经网络的经典应用

### 第二十六章：GraphSage与GAT

* 从GCN到GraphSAge
* 注意力机制回归
* GAT模型详解
* GAT与GCN比较
* 对于异构数据的处理

### 第二十七章：图神经网络的其它应用

* Node Classification
* Graph Classification
* Link Prediction
* 社区挖掘
* 推荐系统
