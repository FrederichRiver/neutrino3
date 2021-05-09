
# 知识建模

## 知识表示

### 基于语义网的知识表示框架

+ RDF和RDFS  
+ OWL和OWL2 Fragments  
+ SPARQL查询语言  
+ Json-LD、RDFa、HTML5 MicroData

### 典型知识库项目的知识表示

### 基于本体工具（Protege）的知识建模

### 知识分类

+ 常识性知识、领域性知识  
+ 事实性知识、过程性知识、控制知识  
+ 确定性知识、不确定性知识  
+ 逻辑性知识、形象性知识  

### 知识表示方式

+ 一阶谓词逻辑 First-Order Logic
Horn逻辑
描述逻辑
概念、关系、个体、描述逻辑的知识库O:=<TBox, ABox>
+ 产生式规则 Production Rule  
+ 框架 Framework  
框架名
槽名Slot
+ 语义网络 Semantic Network  
节点
+ 逻辑程序 Logic Programming  
+ 缺省逻辑 Default Logic  
+ 模态逻辑 Modal Logic  

### 基于语义网的知识表示框架

+ Use RDF as data format  
+ Use URIs as names fo things  
+ Use HTTP URIs so that people can look up those names  
+ When someone looks up a URI, provide useful information(RDF, HTML, etc.)using content negotiation  
+ Include links to other URIs so that related things can be discovered  

### RDF(Resource Description Framework)

三元组: Triple (Subject, Predicate, Object)  
三元组与图模型 (Vertex, Edge, Vertex)  
URL:  domain:name  
RDF与XML
RDF的空白节点
RDF Schema (RDFS)
ontology

## 知识抽取

+ 知识抽取任务定义
+ 面向结构化数据的知识抽取
+ 面向半结构化数据的知识抽取
+ 基于百科数据的知识抽取

### 知识抽取任务定义

#### MCU定义

+ 命名实体识别Named Entity Recognition, NER  
+ 术语抽取  
+ 关系抽取  
+ 事件抽取  
+ 共指消岐 Co-reference Resolution, CR  

#### ACE定义

+ 实体检测与识别 Entity Detection And Recognition, EDR  
+ 数值检测与识别 Value Detection And Recognition, VAL  
+ 时间表达检测与识别 Time Detection And Recognition, TERN  
+ 关系检测与识别 Relation Detection And Recognition, RDR  
+ 事件检测与识别 Event Detection And Recognition, VDR  

#### KBP定义(Knowledge Base Population)

+ 实体发现与链接（Entity Discovery and Linking, EDL）  
+ 槽填充(Slot Filling, SF)  
+ 事件抽取 Event
+ 信念和情感 Belief and Sentiment, BeSt
+ 端到端冷启动知识构建

#### 实体识别

+ HMM方法，有向图模型
+ CRF方法，无向图模型
+ LSTM+CRF方法

### 事件抽取

+ 事件描述 Event Mention  
+ 事件触发 Event Trigger  
+ 事件元素 Event Argument  
+ 元素角色 Argument Role  

#### 事件抽取的Pipline方法

+ 事件触发分类器 Trigger Classifier
+ 元素分类器 Argument Classifier
+ 元素角色分类器 Role Classifier
+ 属性分类器 Attribute Classifier
+ 可报告性分类器 Reportable-Event Classifier

#### 面向结构化数据的知识抽取R2RML

#### Web网页知识抽取-包装器
