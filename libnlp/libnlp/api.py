#!/usr/bin/python3
from libnlp.engine.ner_engine import NEREngine
from libnlp.dataset.cner import CNERProcessor, CluenerProcessor, DataEngine
from libnlp.model.model_config import train_config
from libnlp.model.bert_model import Data_Dir
import torch
from transformers.models.bert.configuration_bert import BertConfig


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
    processor = CNERProcessor()
    label_list = processor.get_labels()
    examples = processor.get_train_sample(Data_Dir)
    # print(examples[0])
    data_engine = DataEngine()
    features = data_engine.convert_sample_to_feature(
        examples=examples, label_list=label_list, **feature_param)
    dataset = data_engine.feature_to_dataset(features)
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
    processor = CNERProcessor()
    label_list = processor.get_labels()
    examples = processor.get_test_sample(Data_Dir)
    # print(examples[0])
    data_engine = DataEngine()
    features = data_engine.convert_sample_to_feature(
        examples=examples, label_list=label_list, **feature_param)
    dataset = data_engine.feature_to_dataset(features)
    ner_engine = NEREngine(train_config)
    ner_engine._load_model()
    ner_engine._optim_config(ner_engine.args)
    ner_engine.scheduler = ner_engine._scheduler_config(ner_engine.args)
    ner_engine._config_dataloader(dataset, flag='test')
    ner_engine.evalidation(ner_engine.args, label_list)


def Predict_bert_ner_model(config: BertConfig):
    pred_output_dir = config.get("output_dir")
    test_dataset = load_and_cache_examples(args, args.task_name, tokenizer, data_type='test')
    # Note that DistributedSampler samples randomly
    test_sampler = SequentialSampler(test_dataset) if args.local_rank == -1 else DistributedSampler(test_dataset)
    test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=1, collate_fn=collate_fn)
    # Eval!
    logger.info("***** Running prediction %s *****", prefix)
    logger.info("  Num examples = %d", len(test_dataset))
    logger.info("  Batch size = %d", 1)
    results = []
    output_predict_file = os.path.join(pred_output_dir, prefix, "test_prediction.json")
    pbar = ProgressBar(n_total=len(test_dataloader), desc="Predicting")

    if isinstance(model, nn.DataParallel):
        model = model.module
    for step, batch in enumerate(test_dataloader):
        model.eval()
        batch = tuple(t.to(args.device) for t in batch)
        with torch.no_grad():
            inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": None}
            if args.model_type != "distilbert":
                # XLM and RoBERTa don"t use segment_ids
                inputs["token_type_ids"] = (batch[2] if args.model_type in ["bert", "xlnet"] else None)
            outputs = model(**inputs)
            logits = outputs[0]
            tags = model.crf.decode(logits, inputs['attention_mask'])
            tags  = tags.squeeze(0).cpu().numpy().tolist()
        preds = tags[0][1:-1]  # [CLS]XXXX[SEP]
        label_entities = get_entities(preds, args.id2label, args.markup)
        json_d = {}
        json_d['id'] = step
        json_d['tag_seq'] = " ".join([args.id2label[x] for x in preds])
        json_d['entities'] = label_entities
        results.append(json_d)
        pbar(step)
    logger.info("\n")
    with open(output_predict_file, "w") as writer:
        for record in results:
            writer.write(json.dumps(record) + '\n')
    if args.task_name == 'cluener':
        output_submit_file = os.path.join(pred_output_dir, prefix, "test_submit.json")
        test_text = []
        with open(os.path.join(args.data_dir,"test.json"), 'r') as fr:
            for line in fr:
                test_text.append(json.loads(line))
        test_submit = []
        for x, y in zip(test_text, results):
            json_d = {}
            json_d['id'] = x['id']
            json_d['label'] = {}
            entities = y['entities']
            words = list(x['text'])
            if len(entities) != 0:
                for subject in entities:
                    tag = subject[0]
                    start = subject[1]
                    end = subject[2]
                    word = "".join(words[start:end + 1])
                    if tag in json_d['label']:
                        if word in json_d['label'][tag]:
                            json_d['label'][tag][word].append([start, end])
                        else:
                            json_d['label'][tag][word] = [[start, end]]
                    else:
                        json_d['label'][tag] = {}
                        json_d['label'][tag][word] = [[start, end]]
            test_submit.append(json_d)
        json_to_text(output_submit_file,test_submit)


if __name__ == "__main__":
    Evaluate_bert_ner_model()
    # Train_bert_ner_model()
