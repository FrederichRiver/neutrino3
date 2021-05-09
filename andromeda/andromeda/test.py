#!/usr/bin/python38
import torch
import torch.nn
import logging
import os
import unittest
from torch.optim import AdamW
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.dataset import Dataset
from transformers import get_linear_schedule_with_warmup
from andromeda.model_config import bert_config, train_config
from pathlib import Path
from andromeda.model.bert_model import BertCRFModel, CNerTokenizer
from andromeda.model_tool import (
    CNERProcessor, InputExample, InputFeatures, set_seed, SeqEntityScore,
    NerFeature)
from andromeda.model_tool import collate_fn
from andromeda.data.data_tool import DataEngine



logger = logging.getLogger(__name__)


def convert_examples_to_features(
            examples: list, label_list: list, tokenizer,
            max_seq_length=768, cls_token="[CLS]",
            cls_token_segment_id=1, sep_token="[SEP]", pad_token=0,
            pad_token_segment_id=0, sequence_a_segment_id=0, mask_padding_with_zero=True):
    """
    Loads a data file into a list of `InputBatch`s\n
    The patten of token is like [CLS] + A + [SEP] + B + [SEP] for BERT.\n
    cls_token_segment_id: define the segment id associated to the CLS token (0 for BERT, 2 for XLNet)
    """
    # Convert label_list into a dict like {label: i}
    label_map = {label: i for i, label in enumerate(label_list)}
    features = []
    # Account for [CLS] and [SEP] with "- 2".
    special_tokens_count = 2
    for (ex_index, example) in enumerate(examples):
        # convert example into features list.
        # if ex_index % 10000 == 0:
        #    logger.info("Writing example %d of %d", ex_index, len(examples))
        tokens = tokenizer.tokenize(example.text_a)
        label_ids = [label_map[x] for x in example.labels]
        # Cut the tokens if tokens is longer than max_seq_length.
        if len(tokens) > max_seq_length - special_tokens_count:
            tokens = tokens[: (max_seq_length - special_tokens_count)]
            label_ids = label_ids[: (max_seq_length - special_tokens_count)]
        # The convention in BERT is:
        # (a) For sequence pairs:
        #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
        #  type_ids:   0   0  0    0    0     0       0   0   1  1  1  1   1   1
        # (b) For single sequences:
        #  tokens:   [CLS] the dog is hairy . [SEP]
        #  type_ids:   0   0   0   0  0     0   0
        #
        # Where "type_ids" are used to indicate whether this is the first
        # sequence or the second sequence. The embedding vectors for `type=0` and
        # `type=1` were learned during pre-training and are added to the wordpiece
        # embedding vector (and position vector). This is not *strictly* necessary
        # since the [SEP] token unambiguously separates the sequences, but it makes
        # it easier for the model to learn the concept of sequences.
        #
        # For classification tasks, the first vector (corresponding to [CLS]) is
        # used as as the "sentence vector". Note that this only makes sense because
        # the entire model is fine-tuned.
        tokens += [sep_token]
        label_ids += [label_map['O']]  # Here O is the letter O.
        segment_ids = [sequence_a_segment_id] * len(tokens)
        # Add [CLS] to the head of token list.
        tokens = [cls_token] + tokens
        label_ids = [label_map['O']] + label_ids
        segment_ids = [cls_token_segment_id] + segment_ids
        # Code for adding [CLS] token ENDs here.
        input_ids = tokenizer.convert_tokens_to_ids(tokens)
        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)
        input_len = len(label_ids)
        # Zero-pad up to the sequence length.
        padding_length = max_seq_length - len(input_ids)
        # Pad on right.
        input_ids += [pad_token] * padding_length
        input_mask += [0 if mask_padding_with_zero else 1] * padding_length
        segment_ids += [pad_token_segment_id] * padding_length
        label_ids += [pad_token] * padding_length
        # """
        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length
        assert len(label_ids) == max_seq_length
        # """
        features.append(InputFeatures(input_ids=input_ids, input_mask=input_mask, input_len=input_len, segment_ids=segment_ids, label_ids=label_ids))
    return features  # features is a list of InputFeatures


def init_logger(log_file=None, log_file_level=logging.NOTSET):
    '''
    Example:
        >>> init_logger(log_file)
        >>> logger.info("abc'")
    '''
    if isinstance(log_file, Path):
        log_file = str(log_file)
    log_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                                   datefmt='%m/%d/%Y %H:%M:%S')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.handlers = [console_handler]
    if log_file and log_file != '':
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_file_level)
        # file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    return logger


def load_and_cache(args: dict, tokenizer) -> TensorDataset:
    """
    For CNER dataset.\n
    Return: (input_ids, attention_mask, segment_ids, labels_ids, lens)
    """
    # Load data features from cache or dataset file
    feature_param = {
        "max_seq_length": 512,
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
    examples = processor.get_train_examples(args['data_dir'])
    features = convert_examples_to_features(examples=examples,
                                            tokenizer=tokenizer,
                                            label_list=label_list,
                                            **feature_param
                                            )
    # Convert to Tensors and build dataset
    all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
    all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
    all_segment_ids = torch.tensor([f.segment_ids for f in features], dtype=torch.long)
    all_label_ids = torch.tensor([f.label_ids for f in features], dtype=torch.long)
    all_lens = torch.tensor([f.input_len for f in features], dtype=torch.long)
    dataset = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_lens, all_label_ids)
    return dataset


"""
def ner_test():
    import time
    # if not os.path.exists(args['output_dir']):
    #    os.mkdir(args['output_dir'])
    # args['output_dir'] = args['output_dir'] + '{}'.format(args.model_type)
    time_ = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    # init_logger(log_file=train_config["output_dir"] + f'/model-type-task-name-{time_}.log')
    processor = CNERProcessor()
    label_list = processor.get_labels()
    var_id2label = {i: label for i, label in enumerate(label_list)}
    var_label2id = {label: i for i, label in enumerate(label_list)}
    num_labels = len(label_list)
    # 'bert': (BertConfig, BertCrfForNer, CNerTokenizer)
    tokenizer = CNerTokenizer.from_pretrained('bert-base-chinese', config=bert_config, cache_dir=train_config['cache_dir'], bos_token='[BOS]', eos_token='[EOS]')
    bert_model = BertCRFModel(config=bert_config)
    train_dataset = load_and_cache(train_config, tokenizer)
    # train_sampler = RandomSampler(train_dataset)
    train_dataloader = DataLoader(train_dataset, shuffle=True, collate_fn=collate_fn, batch_size=1)
    global_step, tr_loss = train(train_config, bert_model, train_dataloader, train_dataset, tokenizer)
"""


class NEREngine(object):
    """
    NER Model for develop, training and testing.
    """
    def __init__(self, args: dict) -> None:
        self.ner_model = BertCRFModel(config=bert_config)
        self.dataloader = None
        self.optimizer = None
        self.scheduler = None
        self.data_path = '/home/friederich/Documents/bert_model/output/'
        self.args = args

    def _config_dataloader(self, data, flag='train'):
        if flag == 'train':
            self.dataloader = DataLoader(dataset=data, batch_size=self.args["batch_size"], shuffle=True, collate_fn=collate_fn)
        elif flag == 'test':
            self.dataloader = DataLoader(dataset=data, batch_size=self.args["batch_size"], shuffle=True, collate_fn=collate_fn)
        else:
            raise dataloaderException('Not proper flag definition.')

    def _save_model(self):
        model_file = os.path.join(self.data_path, "BertCRFModel.pkl")
        torch.save({'state_dict': self.ner_model.state_dict()}, model_file)

    def _load_model(self):
        check_pt = torch.load(os.path.join(self.data_path, "BertCRFModel.pkl"))
        self.ner_model.load_state_dict(check_pt["state_dict"])

    def _scheduler_config(self, args: dict):
        # warmup_steps < train_step
        args['warmup_steps'] = int(args["train_step"] * args['warmup_proportion'])

        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer, num_warmup_steps=args['warmup_steps'],
            num_training_steps=args["train_step"])
        if os.path.isfile(os.path.join(args['model_name_or_path'], "scheduler.pt")):
            # Load in optimizer and scheduler states
            self.scheduler.load_state_dict(torch.load(os.path.join(args['model_name_or_path'], "scheduler.pt")))
        return self.scheduler

    def _optim_config(self, args: dict):
        # Prepare optimizer and schedule (linear warmup and decay)
        no_decay = ["bias", "LayerNorm.weight"]
        bert_param_optimizer = list(self.ner_model.bert.named_parameters())
        crf_param_optimizer = list(self.ner_model.crf.named_parameters())
        linear_param_optimizer = list(self.ner_model.classifier.named_parameters())
        optimizer_grouped_parameters = [
            {'params': [p for n, p in bert_param_optimizer if not any(nd in n for nd in no_decay)],
                'weight_decay': args['weight_decay'], 'lr': args['learning_rate']},
            {'params': [p for n, p in bert_param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0,
                'lr': args['learning_rate']},
            {'params': [p for n, p in crf_param_optimizer if not any(nd in n for nd in no_decay)],
                'weight_decay': args['weight_decay'], 'lr': args['crf_learning_rate']},
            {'params': [p for n, p in crf_param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0,
                'lr': args['crf_learning_rate']},
            {'params': [p for n, p in linear_param_optimizer if not any(nd in n for nd in no_decay)],
                'weight_decay': args['weight_decay'], 'lr': args['crf_learning_rate']},
            {'params': [p for n, p in linear_param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0,
                'lr': args['crf_learning_rate']}
        ]
        optimizer = AdamW(optimizer_grouped_parameters, lr=args['learning_rate'], eps=args['adam_epsilon'])
        if os.path.isfile(os.path.join(args['model_name_or_path'], "optimizer.pt")):
            # Load in optimizer states
            optimizer.load_state_dict(torch.load(os.path.join(args['model_name_or_path'], "optimizer.pt")))
        self.optimizer = optimizer
        return optimizer

    def train(self, args: dict):
        global_step = 0
        steps_trained_in_current_epoch = 0
        tr_loss = 0.0
        self.ner_model.train()
        set_seed(args['seed'])  # Added here for reproductibility (even between python 2 and 3)
        for _ in range(int(args['num_train_epochs'])):
            for step, batch in enumerate(self.dataloader):
                # Skip past any already trained steps if resuming training
                if steps_trained_in_current_epoch > 0:
                    steps_trained_in_current_epoch -= 1
                    continue
                # batch = tuple(t.to(args['device']) for t in batch)
                inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[3], 'input_lens': batch[4]}
                inputs["token_type_ids"] = batch[2]
                # print(len(inputs['input_lens']))
                outputs = self.ner_model(**inputs)
                # break
                loss = outputs[0]  # model outputs are always tuple in pytorch-transformers (see doc)
                # self.ner_model.zero_grad()
                self.optimizer.zero_grad()
                loss.backward()
                tr_loss += loss.item()
                # if (step + 1) % args['gradient_accumulation_steps'] == 0:
                torch.nn.utils.clip_grad_norm_(self.ner_model.parameters(), args['max_grad_norm'])
                self.optimizer.step()
                with open('/home/friederich/Documents/bert_model/output/loss_monitor', 'a') as f:
                    f.write(f"{loss.item()}\n")
                global_step += 1
                if (step + 1) % 100 == 0:
                    self._save_model()
            self.scheduler.step()  # Update learning rate schedule   

    def evalidation(self, args: dict, labels: list):
        metric = SeqEntityScore(labels, markup='bios')
        # Eval!
        eval_loss = 0.0
        nb_eval_steps = 0
        self.ner_model.eval()
        for step, batch in enumerate(self.dataloader):
            with torch.no_grad():
                inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[3], 'input_lens': batch[4]}
                outputs = self.ner_model(**inputs)
                tmp_eval_loss, logits = outputs[:2]
                tags = self.ner_model.crf.decode(logits, inputs['attention_mask'])
            eval_loss += tmp_eval_loss.item()
            nb_eval_steps += 1
            out_label_ids = inputs['labels'].numpy().tolist()
            input_lens = inputs['input_lens'].numpy().tolist()
            tags = tags.squeeze(0).numpy().tolist()
            for i, label in enumerate(out_label_ids):
                temp_1 = []
                temp_2 = []
                for j, m in enumerate(label):
                    if j == 0:
                        continue
                    elif j == input_lens[i] - 1:
                        metric.update(pred_paths=[temp_2], label_paths=[temp_1])
                        break
                    else:
                        temp_1.append(labels[out_label_ids[i][j]])
                        temp_2.append(labels[tags[i][j]])
        eval_loss = eval_loss / nb_eval_steps
        eval_info, entity_info = metric.result()
        results = {f'{key}': value for key, value in eval_info.items()}
        results['loss'] = eval_loss
        print("***** Eval results *****")
        info = "-".join([f' {key}: {value:.4f} ' for key, value in results.items()])
        print("***** Entity results *****")
        for key in sorted(entity_info.keys()):
            print("******* %s results ********" % key)
            info = "-".join([f' {key}: {value:.4f} ' for key, value in entity_info[key].items()])
            print(info)


class NERServer(object):
    """
    NER Model for production.
    """
    def __init__(self, args: dict) -> None:
        self.ner_model = BertCRFModel(config=bert_config)
        self.data_path = '/home/friederich/Documents/bert_model/output/'
        self.args = args
        self._load_model()

    def _load_model(self):
        check_pt = torch.load(os.path.join(self.data_path, "BertCRFModel.pkl"))
        self.ner_model.load_state_dict(check_pt["state_dict"])

    def _load_data(self, data):
        self.dataloader = DataLoader(dataset=data, batch_size=2, shuffle=False, collate_fn=collate_fn)

    def run(self, args: dict, labels: list):
        self.ner_model.eval()
        for step, batch in enumerate(self.dataloader):
            with torch.no_grad():
                inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[3], 'input_lens': batch[4]}
                outputs = self.ner_model(**inputs)
                tmp_eval_loss, logits = outputs[:2]
                tags = self.ner_model.crf.decode(logits, inputs['attention_mask'])
            out_label_ids = inputs['labels'].numpy().tolist()
            input_lens = inputs['input_lens'].numpy().tolist()
            tags = tags.squeeze(0).numpy().tolist()
            print(tags)
            for i, label in enumerate(out_label_ids):
                temp_1 = []
                temp_2 = []
                for j, m in enumerate(label):
                    if j == 0:
                        continue
                    elif j == input_lens[i] - 1:
                        break
                    else:
                        temp_1.append(labels[out_label_ids[i][j]])
                        temp_2.append(labels[tags[i][j]])


class dataloaderException(Exception):
    pass


class BERT_Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skip('pass')
    def test_save_model(self):
        eng = NEREngine(train_config)
        eng._save_model()
        eng._load_model()

    @unittest.skip("pass")
    def test_train_model(self):
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

    @unittest.skip("pass")
    def test_evalue_model(self):
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
        examples = processor.get_dev_examples(data_dir)
        features = processor.convert_examples_to_features(
            examples=examples, label_list=label_list, **feature_param)
        dataset = processor.feature_to_dataset(features)
        eng = NEREngine(train_config)
        eng._load_model()
        eng._optim_config(eng.args)
        eng.scheduler = eng._scheduler_config(eng.args)
        eng._config_dataloader(dataset)
        eng.evalidation(eng.args, label_list)

    #@unittest.skip("pass")
    def test_run_model(self):
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
        data_file = '/home/friederich/Documents/bert_model/data/test_article'
        processor = DataEngine()
        label_list = processor.get_labels()
        print(label_list)
        content = ''
        with open(data_file, 'r') as f:
            while True:
                line = f.readline()
                if line:
                    content += line
                else:
                    break
        content = content.replace('\n', '')
        article = content.split('。')
        example = InputExample('guid-1', article[0])
        label_map = {label: i for i, label in enumerate(label_list)}
        print(label_map)
        feature = []
        # Account for [CLS] and [SEP] with "- 2".
        feature = processor.example_to_feature(
            example=example, label_map=label_map, **feature_param)
        inputs = {
            "input_ids": torch.tensor(feature.input_ids),
            "attention_mask": torch.tensor(feature.input_mask),
            'input_lens': torch.tensor(feature.input_len)
        }
        print(inputs["input_ids"].size())
        print(inputs["attention_mask"].size())
        print(inputs["input_lens"].size())

        eng = NEREngine(train_config)
        eng._load_model()
        eng.ner_model.eval()
        outputs = eng.ner_model.forward(**inputs)
        print(outputs)


if __name__ == "__main__":
    # unittest.main()
    from andromeda.data import cner
    print(cner.TEST_VALUE)
