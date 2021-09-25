#!/usr/bin/python3
from transformers import BertConfig


# BERT_BASE_ZHCN_SIZE is the vocab size of bert_chinese_base.
BERT_ZH_VOCAB_SIZE = 21128
HIDDEN_SIZE = 768
MAX_EMBEDDING_LENS = 256
# num_labels defines the output dimension of BertModel.
bert_config = BertConfig(
    hidden_size=HIDDEN_SIZE,
    vocab_size=BERT_ZH_VOCAB_SIZE,
    num_labels=23,
    max_position_embeddings=MAX_EMBEDDING_LENS)
