# Andromeda

Named Entity Recognition

## NER

### 3 main class

1. Entity  
2. Time  
3. Number  

### 7 subclass

1. Person Name  
2. Orgnazition Name  
3. Location Name  
4. Time  
5. Date  
6. Money  
7. Percent  

## BERT命名实体识别

### BERT配置BertConfig

BertModel的配置通过以下几个途径实现：
1. config
2. 装饰器
3. 装饰器2

### BERT分词BertTokenizer

Torch下的BertTokenizer通过以下方法从transformers当中引入应用。此处采用bert-base-chinese预训练模型用于中文分词。

```python
from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese', config=bert_config)
```

BertTokenizer包含4个API

#### 1. **build_inputs_with_special_tokens**

```python
build_inputs_with_special_tokens(token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> list[int]
```

* 单句序列: [CLS] X [SEP]  
* 双句子序列: [CLS] A [SEP] B [SEP]  

#### 2. **create_token_type_ids_from_sequences**

```python
create_token_type_ids_from_sequences(token_ids_0: List[int], token_ids_1: Optional[List[int]] = None) -> list[int]
```

在句子对任务中建立mask形式如下。在Q&A等任务中，用于区分前后句子。

```
0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1
| first sequence    | second sequence |
```

#### 3. **get_special_tokens_mask**

```python
get_special_tokens_mask(oken_ids_0: List[int], token_ids_1: Optional[List[int]] = None, already_has_special_tokens: bool = False) -> list[int]
```

当使用prepare_for_model方法时，将特殊token遮盖为1，常规的序列token遮罩为0。

#### 4. **save_vocabulary**

```python
save_vocabulary(vocab_path: str)
```

**BertTokenizer**本身返回一个dict,包括input_ids, input_type_ids, attention_mask。

## BertForTokenClassification

BertForTokenClassification的输出：  

BertModel -> BertForTokenClassification

BertForTokenClassification->output = (logits, BertModel->output[2:])
BertModel->output = (encoder_output[0], pooled_output, encoder_output[1:])
pooled_output = pooler(encoder_output[0])
encoder_output = BertEncoder->output
BertEncoder->output = (hidden state, (all hidden states), (all attention states) )

## Scheduler 学习率
transformers.get_linear_scheduler_with_warmup
warmup机制，学习率先增加，再减小

## gradient_accumulation_steps机制
