#!/usr/bin/python38
from datetime import date
import os
import torch
import numpy as np
from torch.cuda import device
import torch.nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup, get_constant_schedule
from ..model.model_config import bert_config, MAX_EMBEDDING_LENS
from ..engine.model_tool import (set_seed, SeqEntityScore, collate_fn, get_entities)
from ..model.bert_model import BertCRFModel


class NEREngine(object):
    """
    NER Model for develop, training and testing.
    """
    def __init__(self, args: dict) -> None:
        self.ner_model = BertCRFModel(config=bert_config)
        self.dataloader = None
        self.testloader = None
        self.optimizer = None
        self.scheduler = None
        self.data_path = args.get('model_path')
        self.data_path = '/home/fred/Documents/dev/bert_model/train_model/'
        self.args = args

    def _config_dataloader(self, data, flag='train'):
        if flag == 'train':
            self.dataloader = DataLoader(dataset=data, batch_size=self.args["batch_size"], shuffle=True, collate_fn=collate_fn)
        elif flag == 'test':
            self.testloader = DataLoader(dataset=data, batch_size=self.args["batch_size"], shuffle=True, collate_fn=collate_fn)
        elif flag == 'valid':
            self.dataloader = DataLoader(dataset=data, batch_size=self.args["batch_size"], shuffle=True, collate_fn=collate_fn)
        else:
            raise dataloaderException('Not proper flag definition.')

    def _save_model(self, epoch: int, loss: float):
        model_file = os.path.join(self.data_path, "BertCRFModel.pkl")
        torch.save(
            {   
                'state_dict': self.ner_model.state_dict(),
                'epoch': epoch,
                'optimizer_state_dict': self.optimizer.state_dict(),
                'loss': loss,
            }, model_file)

    def _load_model(self):
        check_pt = torch.load(os.path.join(self.data_path, "BertCRFModel.pkl"))
        self.ner_model.load_state_dict(check_pt["state_dict"])
        # self.optimizer.load_state_dict(check_pt["optimizer_state_dict"])

    def _scheduler_config(self, args: dict):
        # warmup_steps < train_step
        args['warmup_steps'] = int(args["train_step"] * args['warmup_proportion'])

        self.scheduler = get_constant_schedule(self.optimizer)
        if os.path.isfile(os.path.join(args['model_path'], "scheduler.pt")):
            # Load in optimizer and scheduler states
            self.scheduler.load_state_dict(torch.load(os.path.join(args['model_path'], "scheduler.pt")))
        return self.scheduler

    def _optim_config(self, args: dict):
        # Prepare optimizer and schedule (linear warmup and decay)
        no_decay = ["bias", "LayerNorm.weight"]
        bert_param_optimizer = list(self.ner_model.bert.named_parameters())
        crf_param_optimizer = list(self.ner_model.crf.named_parameters())
        linear_param_optimizer = list(self.ner_model.classifier.named_parameters())
        optimizer_grouped_parameters = [
            #{'params': [p for n, p in bert_param_optimizer if not any(nd in n for nd in no_decay)],
            #    'weight_decay': args['weight_decay'], 'lr': args['learning_rate']},
            #{'params': [p for n, p in bert_param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0,
            #    'lr': args['learning_rate']},
            {'params': [p for n, p in crf_param_optimizer if not any(nd in n for nd in no_decay)],
                'weight_decay': args['weight_decay'], 'lr': args['crf_learning_rate']},
            {'params': [p for n, p in crf_param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0,
                'lr': args['crf_learning_rate']},
            {'params': [p for n, p in linear_param_optimizer if not any(nd in n for nd in no_decay)],
                'weight_decay': args['weight_decay'], 'lr': args['crf_learning_rate']},
            {'params': [p for n, p in linear_param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0,
                'lr': args['crf_learning_rate']}
        ]
        optimizer = AdamW(optimizer_grouped_parameters, lr=args['crf_learning_rate'], eps=args['adam_epsilon'])
        if os.path.isfile(os.path.join(args['model_path'], "optimizer.pt")):
            # Load in optimizer states
            optimizer.load_state_dict(torch.load(os.path.join(args['model_path'], "optimizer.pt")))
        self.optimizer = optimizer
        return optimizer

    def train(self, args: dict):
        device = torch.device('cuda:0')
        steps_trained_in_current_epoch = 0
        tr_loss = 0.0
        self.ner_model.train()
        set_seed(args['seed'])  # Added here for reproductibility (even between python 2 and 3)
        for step, batch in enumerate(self.dataloader):
            # Skip past any already trained steps if resuming training
            if steps_trained_in_current_epoch > 0:
                steps_trained_in_current_epoch -= 1
                continue
            # batch = tuple(t.to(device) for t in batch)
            inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[3], 'input_lens': batch[4]}
            inputs["token_type_ids"] = batch[2]
            # print(len(inputs['input_lens']))
            outputs = self.ner_model(**inputs)
            loss = outputs[0]  # model outputs are always tuple in pytorch-transformers (see doc)
            # self.ner_model.zero_grad()
            self.optimizer.zero_grad()
            loss.backward()
            tr_loss += loss.item()
            # if (step + 1) % args['gradient_accumulation_steps'] == 0:
            torch.nn.utils.clip_grad_norm_(self.ner_model.parameters(), args['max_grad_norm'])
            self.optimizer.step()
            with open('/home/fred/Documents/dev/bert_model/train_model/loss_monitor', 'a') as f:
                f.write(f"{loss.item()}\n")
            self.scheduler.step()  # Update learning rate schedule
        return tr_loss / len(self.dataloader)

    def test(self, args: dict):
        device = torch.device('cuda:0')
        global_step = 0
        steps_trained_in_current_epoch = 0
        test_loss = 0.0
        self.ner_model.eval()
        set_seed(args['seed'])  # Added here for reproductibility (even between python 2 and 3)
        for step, batch in enumerate(self.testloader):
            # Skip past any already trained steps if resuming training
            if steps_trained_in_current_epoch > 0:
                steps_trained_in_current_epoch -= 1
                continue
            # batch = tuple(t.to(device) for t in batch)
            inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[3], 'input_lens': batch[4]}
            inputs["token_type_ids"] = batch[2]
            # print(len(inputs['input_lens']))
            outputs = self.ner_model(**inputs)
            # break
            loss = outputs[0]  # model outputs are always tuple in pytorch-transformers (see doc)
            # self.ner_model.zero_grad()
            self.optimizer.zero_grad()
            test_loss += loss.item()
            # if (step + 1) % args['gradient_accumulation_steps'] == 0:
        return test_loss / len(self.testloader)

    def validation(self, args: dict):
        import datetime
        best_loss = np.inf
        train_loss = 0.0
        for i in range(int(args['num_train_epochs'])):
            t = datetime.datetime.now()
            time_str = t.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{time_str}: The {i + 1} step.")
            train_loss = self.train(args)
            test_loss = self.test(args)
            print(f"Train loss: {train_loss}, Valid loss: {test_loss}.")
            if test_loss < train_loss:
                self._save_model(i, train_loss)
                best_loss = test_loss
        self._save_model(0, train_loss)


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
        result = metric.result()
        metric.report(result)


class NERServer(object):
    """
    NER Model for production.
    """
    def __init__(self, args: dict) -> None:
        self.ner_model = BertCRFModel(config=bert_config)
        self.data_path = '/home/fred/Documents/dev/bert_model/train_model/'
        self.args = args
        self.label = []
        self._load_model()

    def _load_model(self):
        check_pt = torch.load(os.path.join(self.data_path, "BertCRFModel.pkl"))
        self.ner_model.load_state_dict(check_pt["state_dict"])

    def load_label(self, label: list):
        self.label = label

    def _load_data(self, data):
        self.dataloader = DataLoader(dataset=data, batch_size=2, shuffle=False, collate_fn=collate_fn)

    def run(self, data):
        self.ner_model.eval()
        with torch.no_grad():
            inputs = {"input_ids": data[0], "attention_mask": data[1], 'labels': None, 'input_lens': data[3]}
            outputs = self.ner_model(**inputs)
            logits = outputs[0]
            tags = self.ner_model.crf.decode(logits, inputs['attention_mask'])
        input_lens = inputs['input_lens'].numpy().tolist()
        tags = tags.squeeze(0).numpy().tolist()
        preds = tags[0][1:-1]  # [CLS]XXXX[SEP]
        print(preds)
        label_entities = get_entities(preds, self.label, 'bio')
        print(label_entities)


class dataloaderException(Exception):
    pass


class NerLabel(object):
    def __init__(self, file_path: str) -> None:
        self._label = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self._label = f.read().splitlines()
        else:
            raise FileExistsError(f"{file_path} does not exists.")

    @property
    def label(self):
        return self._label


class ReadText(object):
    def __init__(self, file_path: str) -> None:
        with open(file_path, 'r') as f:
            content = f.read().splitlines()
        while '' in content:
            content.remove('')
        print(content)
        for i in range(len(content)):
            if len(content[i]) > 10:
                content[i] = content[i][:10]
        print(content)


if __name__ == '__main__':
    event = ReadText('/home/friederich/Dev/neutrino2/data/news.txt')
