#!/usr/bin/python38
from andromeda.model import NEREngine
from andromeda.data.data_tool import DataEngine
from andromeda.model_config import train_config


def Train_bert_ner_model():
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
    processor = DataEngine()
    label_list = processor.get_labels()
    examples = processor.get_train_examples(data_dir)
    # print(examples[0])
    features = processor.convert_examples_to_features(
        examples=examples, label_list=label_list, **feature_param)
    dataset = processor.feature_to_dataset(features)
    eng = NEREngine(train_config)
    eng._load_model()
    eng._optim_config(eng.args)
    eng.scheduler = eng._scheduler_config(eng.args)
    eng._config_dataloader(dataset)
    eng.train(eng.args)


if __name__ == "__main__":
    Train_bert_ner_model()
