#!/usr/bin/python3
from libnlp.engine.ner_engine import NEREngine, NERServer
from libnlp.dataset.cner import CNERProcessor, CluenerProcessor, DataEngine, ner_label, MSRAProcessor
from libnlp.model.model_config import MAX_EMBEDDING_LENS
from libnlp.model.bert_model import Data_Dir
import torch
from transformers.models.bert.configuration_bert import BertConfig
from libnlp.engine.model_tool import (set_seed, SeqEntityScore, collate_fn, get_entities)


train_config = {
    # The name of the task to train selected in the list.
    "task_name": None,
    "model_type": None,
    # Directory manage
    "data_dir": '/home/fred/Documents/dev/bert_model/data/cner/',
    "model_path": '/home/fred/Documents/dev/bert_model/train_model/',
    "output_dir": '/home/fred/Documents/dev/bert_model/output',
    "cache_dir": '/home/fred/Documents/dev/bert_model/cache/',
    # "data_dir": '/home/fred/bert_model/data/cner/',
    # "model_name_or_path": '/home/fred/bert_model/output/',
    # "output_dir": '/home/fred/bert_model/output/',
    # "cache_dir": '/home/fred/bert_model/cache/',
    "batch_size": 40,
    "markup": 'bio',
    "loss_type": 'ce',
    "config_name": "",
    "tokenizer_name": "",
    "train_max_seq_length": 128,
    "eval_max_seq_length": MAX_EMBEDDING_LENS,
    "do_train": True,
    "do_eval": True,
    "do_predict": True,
    "evaluate_during_training": True,
    # "do_lower_case": True,
    "do_adv": True,
    "adv_epsilon": 1.0,
    "adv_name": 'word_embeddings',
    # GPU calculation
    "n_gpu": 0,
    "per_gpu_train_batch_size": 8,
    "per_gpu_eval_batch_size": 8,
    # learning rate management
    "gradient_accumulation_steps": 1,
    "learning_rate": 1e-5,
    "crf_learning_rate": 2e-4,
    "weight_decay": 0.01,
    "adam_epsilon": 1e-8,
    "max_grad_norm": 1.0,
    "num_train_epochs": 3,
    "max_steps": -1,
    "warmup_proportion": 0.1,
    "logging_steps": 50,
    "save_steps": 30,
    "train_step": 20,
    "eval_all_checkpoints": True,
    "predict_checkpoints": 0,
    "cuda": False,
    "overwrite_cache_dir": True,
    "overwrite_output_dir": True,
    "seed": 42,
    "local_rank": "",
    "server_ip": "127.0.0.1",
    "server_port": ""
}


def Train_bert_ner_model():
    """
    Using CNER dataset to train BERT-CRF model.
    """
    feature_param = {
        "max_seq_length": 100,
        "cls_token": "[CLS]",
        "cls_token_segment_id": 1,
        "sep_token": "[SEP]",
        "pad_token": 0,
        "pad_token_segment_id": 0,
        "sequence_a_segment_id": 0,
        "mask_padding_with_zero": True
    }
    # data_dir = '/home/friederich/Documents/bert_model/data/cner/'
    # processor = CNERProcessor()
    processor = MSRAProcessor()
    label_list = processor.get_labels()
    train_examples = processor.get_train_sample(Data_Dir)
    test_examples = processor.get_test_sample(Data_Dir)
    # print(examples[0])
    data_engine = DataEngine()
    train_features = data_engine.convert_sample_to_feature(
        examples=train_examples, label_list=label_list, **feature_param)
    train_dataset = data_engine.feature_to_dataset(train_features)
    test_features = data_engine.convert_sample_to_feature(
        examples=test_examples, label_list=label_list, **feature_param)
    test_dataset = data_engine.feature_to_dataset(test_features)
    ner_engine = NEREngine(train_config)
    """
    if torch.cuda.is_available():
        device = torch.device('cuda:0')
        print(device)
        ner_engine.ner_model.to(device)
    """
    ner_engine._load_model()
    ner_engine._optim_config(ner_engine.args)
    ner_engine.scheduler = ner_engine._scheduler_config(ner_engine.args)
    ner_engine._config_dataloader(train_dataset, 'train')
    ner_engine._config_dataloader(test_dataset, 'test')
    ner_engine.validation(train_config)


def Evaluate_bert_ner_model():
    """
    Using CNER dataset to train BERT-CRF model.
    """
    feature_param = {
        "max_seq_length": 100,
        "cls_token": "[CLS]",
        "cls_token_segment_id": 1,
        "sep_token": "[SEP]",
        "pad_token": 0,
        "pad_token_segment_id": 0,
        "sequence_a_segment_id": 0,
        "mask_padding_with_zero": True
    }
    processor = CNERProcessor()
    label_list = processor.get_labels()
    examples = processor.get_dev_sample(Data_Dir)
    # print(examples[0])
    data_engine = DataEngine()
    features = data_engine.convert_sample_to_feature(
        examples=examples, label_list=label_list, **feature_param)
    dataset = data_engine.feature_to_dataset(features)
    ner_engine = NEREngine(train_config)
    ner_engine._load_model()
    ner_engine._optim_config(ner_engine.args)
    ner_engine.scheduler = ner_engine._scheduler_config(ner_engine.args)
    ner_engine._config_dataloader(dataset, flag='valid')
    ner_engine.evalidation(ner_engine.args, label_list)


def Run_bert_ner_model():
    """
    Using CNER dataset to train BERT-CRF model.
    """
    feature_param = {
        "max_seq_length": 100,
        "cls_token": "[CLS]",
        "cls_token_segment_id": 1,
        "sep_token": "[SEP]",
        "pad_token": 0,
        "pad_token_segment_id": 0,
        "sequence_a_segment_id": 0,
        "mask_padding_with_zero": True
    }
    processor = CNERProcessor()
    label_list = processor.get_labels()
    examples = processor.get_test_sample(Data_Dir)
    # print(examples[0])
    data_engine = DataEngine()
    features = data_engine.convert_sample_to_feature(
        examples=examples, label_list=label_list, **feature_param)
    ner_engine = NERServer(train_config)
    ner_engine._load_model()
    ner_engine.load_label(label_list)
    t = '北京天文馆高级工程师 寇文：在阴历十四（20日）的晚上，月亮看起来也是非常圆的，到了十五（21日）的晚上，虽然离月亮最圆已经过了十几个小时，但靠肉眼很难看出区别。'
    t = '1911年，是中国农历辛亥年。这一年发生的辛亥革命推翻了清朝政府，结束了在中国延续几千年的君主专制制度，成为里程碑式的历史事件。今年10月9日，纪念辛亥革命110周年大会隆重举行，习近平总书记在会上发表重要讲话，深刻阐述了辛亥革命110年来的历史启示。'
    # t = '北京天文馆高级工程师喜欢吃月饼，他在吉利汽车公司工作'
    data = data_engine.covert_str_to_feature(t)
    preds = ner_engine.run(data)
    # tokens = data_engine.tokenizer.convert_ids_to_tokens(preds)
    for i in range(len(preds)):
        label = label_list[preds[i]]
        if label != 'X' and label != 'O':
            print(f"{t[i]},{label}")
    label_entities = get_entities(preds, ner_engine.label, 'bio')
    print(label_entities)


def Test():
    """
    Using CNER dataset to train BERT-CRF model.
    """
    feature_param = {
        "max_seq_length": 100,
        "cls_token": "[CLS]",
        "cls_token_segment_id": 1,
        "sep_token": "[SEP]",
        "pad_token": 0,
        "pad_token_segment_id": 0,
        "sequence_a_segment_id": 0,
        "mask_padding_with_zero": True
    }
    # data_dir = '/home/friederich/Documents/bert_model/data/cner/'
    # processor = CNERProcessor()
    processor = MSRAProcessor()
    label_list = processor.get_labels()
    train_examples = processor.get_train_sample(Data_Dir)
    test_examples = processor.get_test_sample(Data_Dir)
    # print(examples[0])
    data_engine = DataEngine()
    train_features = data_engine.convert_sample_to_feature(
        examples=train_examples, label_list=label_list, **feature_param)
    train_dataset = data_engine.feature_to_dataset(train_features)
    ner_engine = NEREngine(train_config)
    """
    if torch.cuda.is_available():
        device = torch.device('cuda:0')
        print(device)
        ner_engine.ner_model.to(device)
    """
    ner_engine._load_model()
    ner_engine._optim_config(ner_engine.args)
    ner_engine.scheduler = ner_engine._scheduler_config(ner_engine.args)
    ner_engine._config_dataloader(train_dataset, 'train')
    for step, batch in enumerate(data_engine.dataloader):
        print(batch[0])

if __name__ == "__main__":
    # Evaluate_bert_ner_model()
    # Train_bert_ner_model()
    # Run_bert_ner_model()
    Test()