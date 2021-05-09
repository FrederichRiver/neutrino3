#!/usr/bin/python38
from libnlp.engine.ner_engine import NEREngine
from libnlp.dataset.cner import CNERProcessor, CluenerProcessor, DataEngine
from libnlp.model.model_config import train_config


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
    data_dir = '/home/friederich/Documents/bert_model/data/cner/'
    processor = CNERProcessor()
    label_list = processor.get_labels()
    examples = processor.get_train_sample(data_dir)
    # print(examples[0])
    data_engine = DataEngine()
    features = data_engine.convert_sample_to_feature(
        examples=examples, label_list=label_list, **feature_param)
    dataset = data_engine.feature_to_dataset(features)
    ner_engine = NEREngine(train_config)
    ner_engine._load_model()
    ner_engine._optim_config(ner_engine.args)
    ner_engine.scheduler = ner_engine._scheduler_config(ner_engine.args)
    ner_engine._config_dataloader(dataset)
    ner_engine.train(ner_engine.args)


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
    data_dir = '/home/friederich/Documents/bert_model/data/cner/'
    processor = CNERProcessor()
    label_list = processor.get_labels()
    examples = processor.get_train_sample(data_dir)
    # print(examples[0])
    data_engine = DataEngine()
    features = data_engine.convert_sample_to_feature(
        examples=examples, label_list=label_list, **feature_param)
    dataset = data_engine.feature_to_dataset(features)
    ner_engine = NEREngine(train_config)
    ner_engine._load_model()
    ner_engine._optim_config(ner_engine.args)
    ner_engine.scheduler = ner_engine._scheduler_config(ner_engine.args)
    ner_engine._config_dataloader(dataset)
    ner_engine.evalidation(ner_engine.args, label_list)


if __name__ == "__main__":
    Evaluate_bert_ner_model()
