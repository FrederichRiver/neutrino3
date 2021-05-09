#!/usr/bin/python38
import os
import torch
import torch.nn
import unittest
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup
from andromeda.model_config import bert_config
from andromeda.model_tool import (set_seed, SeqEntityScore)
from andromeda.model_tool import collate_fn
from .bert_model import BertCRFModel


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
        print("Test start.")

    def tearDown(self):
        print("Test finished.")

    @unittest.skip('Skip')
    def test_bertcrfmodel(self):
        from andromeda.model_config import bert_config
        model = BertCRFModel(config=bert_config)
        print(model)

    @unittest.skip('Skip')
    def test_classify(self):
        from andromeda.model_config import bert_config
        model = BertCRFModel(config=bert_config)
        model.eval()

    def test_token(self):
        tokenizer = CNerTokenizer.from_pretrained('bert-base-chinese')
        result = tokenizer.tokenize("分词测试")
        print(result)


if __name__ == "__main__":
    unittest.main()
