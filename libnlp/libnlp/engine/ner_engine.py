#!/usr/bin/python38
import os
import torch
import torch.nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup
from ..model.model_config import bert_config
from ..engine.model_tool import (set_seed, SeqEntityScore, collate_fn)
from ..model.bert_model import BertCRFModel


class NEREngine(object):
    """
    NER Model for develop, training and testing.
    """
    def __init__(self, args: dict) -> None:
        self.ner_model = BertCRFModel(config=bert_config)
        self.dataloader = None
        self.optimizer = None
        self.scheduler = None
        self.data_path = '/home/fred/Documents/dev/bert_model/train_model/'
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
                with open('/home/fred/Documents/dev/bert_model/train_model/loss_monitor', 'a') as f:
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
        result = metric.result()
        metric.report(result)


    def predict(self, args: dict, labels: list):
        pred_output_dir = args.output_dir
        if not os.path.exists(pred_output_dir) and args.local_rank in [-1, 0]:
            os.makedirs(pred_output_dir)
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


class NERServer(object):
    """
    NER Model for production.
    """
    def __init__(self, args: dict) -> None:
        self.ner_model = BertCRFModel(config=bert_config)
        self.data_path = '/home/fred/Documents/dev/bert_model/output/'
        self.args = args
        self.label = []
        self._load_model()

    def _load_model(self):
        check_pt = torch.load(os.path.join(self.data_path, "BertCRFModel.pkl"))
        self.ner_model.load_state_dict(check_pt["state_dict"])

    def load_label(self):
        pass

    def _load_data(self, data):
        self.dataloader = DataLoader(dataset=data, batch_size=2, shuffle=False, collate_fn=collate_fn)

    def run(self, args: dict, labels: list):
        self.ner_model.eval()
        with torch.no_grad():
            inputs = {"input_ids": batch[0], "attention_mask": batch[1], 'input_lens': batch[4]}
            outputs = self.ner_model(**inputs)
            _, logits = outputs[:2]
            tags = self.ner_model.crf.decode(logits, inputs['attention_mask'])
        input_lens = inputs['input_lens'].numpy().tolist()
        tags = tags.squeeze(0).numpy().tolist()
        print(tags)
        

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
