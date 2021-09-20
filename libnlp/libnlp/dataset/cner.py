#!/usr/bin/python38
import copy
import csv
import json
import os
import torch
from libnlp.model.bert_model import CNerTokenizer
from torch.utils.data import TensorDataset
from libnlp.model.model_config import MAX_EMBEDDING_LENS


ner_label = ["X", 'B-CONT', 'B-EDU', 'B-LOC', 'B-NAME', 'B-ORG', 'B-PRO', 'B-RACE', 'B-TITLE',
                'I-CONT', 'I-EDU', 'I-LOC', 'I-NAME', 'I-ORG', 'I-PRO', 'I-RACE', 'I-TITLE',
                'O', 'S-NAME', 'S-ORG', 'S-RACE']

class InputSample(object):
    """A single training/test example for token classification."""
    def __init__(self, guid: str, text_a: list, labels: list = None):
        """
        Args:
        >guid: Unique id for the example.\n
        >text_a: list. The words of the sequence.\n
        >labels: (Optional) list. The labels for each word of the sequence. This should be
            specified for train and dev examples, but not for test examples.
        """
        self.guid = guid
        self.text_a = text_a
        if labels:
            self.labels = labels
        else:
            self.labels = []

    def __repr__(self):
        return str(self.to_json_string())

    def to_dict(self):
        """Serializes this instance to a Python dictionary."""
        output = copy.deepcopy(self.__dict__)
        return output

    def to_json_string(self):
        """Serializes this instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


class NerFeature(object):
    def __init__(self, input_ids: list, input_mask: list, input_len: int, segment_ids: list):
        """
        Args:\n
        >input_ids: list, a list of tokens from tokenizer.\n
        >input_mask: list of int, mask equals to one if the token is from sentence,
                        else equals zero means the token is a padding token.\n
        >segment_ids: \n
        >label_ids: \n
        >input_len: int, it is the real size of input_ids without padding tokens. \n
        """
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.input_len = input_len

    def __repr__(self):
        return str(self.to_json_string())

    def to_dict(self):
        """Serializes this instance to a Python dictionary."""
        output = copy.deepcopy(self.__dict__)
        return output

    def to_json_string(self):
        """Serializes this instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


class InputFeature(object):
    """A single set of features of data."""
    def __init__(self, input_ids: list, input_mask: list, input_len: int, segment_ids: list, label_ids: list):
        """
        Args:\n
        >input_ids: list, a list of tokens from tokenizer.\n
        >input_mask: list of int, mask equals to one if the token is from sentence,
                        else equals zero means the token is a padding token.\n
        >segment_ids: \n
        >label_ids: \n
        >input_len: int, it is the real size of input_ids without padding tokens. \n
        """
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_ids = label_ids
        self.input_len = input_len

    def __repr__(self):
        return str(self.to_json_string())

    def to_dict(self):
        """Serializes this instance to a Python dictionary."""
        output = copy.deepcopy(self.__dict__)
        return output

    def to_json_string(self):
        """Serializes this instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


class DataProcessor(object):
    """Base class for data converters for sequence classification data sets."""
    def get_train_sample(self, data_dir):
        """Gets a collection of `InputExample`s for the train set."""
        raise NotImplementedError()

    def get_dev_sample(self, data_dir):
        """Gets a collection of `InputExample`s for the dev set."""
        raise NotImplementedError()

    def get_labels(self):
        """
        Gets the list of labels for this data set.\n
        Return a list of string labels like ['B', ..., 'X', 'O']
        """
        raise NotImplementedError()

    @classmethod
    def _read_csv(cls, input_file: str, quotechar=None) -> list:
        """Reads a tab separated value file."""
        with open(input_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter="\t", quotechar=quotechar)
            lines = []
            for line in reader:
                lines.append(line)
            return lines

    @classmethod
    def _read_text(cls, input_file: str) -> list:
        """
        Text file should start with string '-DOCSTART-' or
        section with empty line or enter symbol.
        """
        lines = []
        with open(input_file, 'r') as f:
            words = []
            labels = []
            for line in f:
                # Reading lines
                if line.startswith("-DOCSTART-") or line == "" or line == "\n":
                    # Recognite spliter.
                    if words:
                        # Pop words and labels into lines.
                        lines.append({"words": words, "labels": labels})
                        # Release lists.
                        words = []
                        labels = []
                else:
                    splits = line.split(" ")
                    words.append(splits[0])
                    if len(splits) > 1:
                        labels.append(splits[-1].replace("\n", ""))
                    else:
                        # Examples could have no label for mode = "test"
                        labels.append("O")
            if words:
                lines.append({"words": words, "labels": labels})
        return lines

    @classmethod
    def _read_json(cls, input_file) -> list:
        lines = []
        with open(input_file, 'r') as f:
            for line in f:
                line = json.loads(line.strip())
                text = line['text']
                label_entities = line.get('label', None)
                words = list(text)
                labels = ['O'] * len(words)
                if label_entities is not None:
                    for key, value in label_entities.items():
                        for sub_name, sub_index in value.items():
                            for start_index, end_index in sub_index:
                                assert ''.join(words[start_index:end_index+1]) == sub_name
                                if start_index == end_index:
                                    labels[start_index] = 'S-'+key
                                else:
                                    labels[start_index] = 'B-'+key
                                    labels[start_index+1:end_index+1] = ['I-'+key]*(len(sub_name)-1)
                lines.append({"words": words, "labels": labels})
        return lines


class CNERProcessor(DataProcessor):
    """Processor for 'CNER' dataset."""

    def get_train_sample(self, data_dir):
        """data_dir is the data path w/o '/'."""
        return self._create_example(self._read_text(os.path.join(data_dir, "train.char.bmes")), "train")

    def get_dev_sample(self, data_dir):
        """data_dir is the data path w/o '/'."""
        return self._create_example(self._read_text(os.path.join(data_dir, "dev.char.bmes")), "dev")

    def get_test_sample(self, data_dir):
        """data_dir is the data path w/o '/'."""
        return self._create_example(self._read_text(os.path.join(data_dir, "test.char.bmes")), "test")

    def get_labels(self):
        """See base class."""
        return ["X", 'B-CONT', 'B-EDU', 'B-LOC', 'B-NAME', 'B-ORG', 'B-PRO', 'B-RACE', 'B-TITLE',
                'I-CONT', 'I-EDU', 'I-LOC', 'I-NAME', 'I-ORG', 'I-PRO', 'I-RACE', 'I-TITLE',
                'O', 'S-NAME', 'S-ORG', 'S-RACE', "[START]", "[END]"]

    def _create_example(self, lines, set_type):
        """Creates examples for the training and dev sets."""
        examples = []
        for (i, line) in enumerate(lines):
            guid = f"{set_type}-{i}"
            text_a = line['words']
            # BIOS
            labels = []
            for x in line['labels']:
                if 'M-' in x:
                    labels.append(x.replace('M-', 'I-'))
                elif 'E-' in x:
                    labels.append(x.replace('E-', 'I-'))
                else:
                    labels.append(x)
            examples.append(InputSample(guid=guid, text_a=text_a, labels=labels))
        return examples


class CluenerProcessor(DataProcessor):
    """Processor for the chinese ner data set."""

    def get_train_sample(self, data_dir):
        """See base class."""
        return self._create_example(self._read_json(os.path.join(data_dir, "train.json")), "train")

    def get_dev_sample(self, data_dir):
        """See base class."""
        return self._create_example(self._read_json(os.path.join(data_dir, "dev.json")), "dev")

    def get_test_sample(self, data_dir):
        """See base class."""
        return self._create_example(self._read_json(os.path.join(data_dir, "test.json")), "test")

    def get_labels(self):
        """See base class."""
        return ["X", "B-address", "B-book", "B-company", 'B-game', 'B-government', 'B-movie', 'B-name',
                'B-organization', 'B-position', 'B-scene', "I-address",
                "I-book", "I-company", 'I-game', 'I-government', 'I-movie', 'I-name',
                'I-organization', 'I-position', 'I-scene',
                "S-address", "S-book", "S-company", 'S-game', 'S-government', 'S-movie',
                'S-name', 'S-organization', 'S-position',
                'S-scene', 'O', "[START]", "[END]"]

    def _create_example(self, lines, set_type):
        """Creates examples for the training and dev sets."""
        examples = []
        for (i, line) in enumerate(lines):
            guid = "%s-%s" % (set_type, i)
            text_a = line['words']
            # BIOS
            labels = line['labels']
            examples.append(InputSample(guid=guid, text_a=text_a, labels=labels))
        return examples


class DataEngine(object):
    """
    Provide data for training and validation.
    """
    def __init__(self) -> None:
        self.tokenizer = CNerTokenizer.from_pretrained('bert-base-chinese')
        # self.position_embedding = PositionalEncoding(512, 512)

    def convert_sample_to_feature(self, examples: list, label_list: list, max_seq_length=768, cls_token="[CLS]", cls_token_segment_id=1, sep_token="[SEP]", pad_token=0, pad_token_segment_id=0, sequence_a_segment_id=0, mask_padding_with_zero=True):
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
            # convert example into feature.
            f = self._sample_to_feature(
                example, label_map=label_map, max_seq_length=max_seq_length, cls_token=cls_token,
                cls_token_segment_id=cls_token_segment_id, sep_token=sep_token, pad_token=pad_token,
                pad_token_segment_id=pad_token_segment_id, sequence_a_segment_id=sequence_a_segment_id,
                mask_padding_with_zero=mask_padding_with_zero, special_tokens_count=special_tokens_count)
            features.append(f)
        return features  # features is a list of InputFeatures

    def _sample_to_feature(
            self, example: InputSample, label_map: dict,
            max_seq_length=768, cls_token="[CLS]", cls_token_segment_id=1,
            sep_token="[SEP]", pad_token=0, pad_token_segment_id=0,
            sequence_a_segment_id=0, mask_padding_with_zero=True,
            special_tokens_count=2):
        """
        Loads a data file into a list of `InputBatch`s\n
        The patten of token is like [CLS] + A + [SEP] + B + [SEP] for BERT.\n
        cls_token_segment_id: define the segment id associated to the CLS token (0 for BERT, 2 for XLNet)
        """
        # Account for [CLS] and [SEP] with "- 2".
        # convert example into features list.
        # if ex_index % 10000 == 0:
        #    logger.info("Writing example %d of %d", ex_index, len(examples))
        tokens = self.tokenizer.tokenize(example.text_a)
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
        input_ids = self.tokenizer.convert_tokens_to_ids(tokens)
        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)
        # input_mask = [i + 1 for i in range(len(input_ids))]
        input_len = len(label_ids)
        # Zero-pad up to the sequence length.
        padding_length = max_seq_length - len(input_ids)
        # Pad on right.
        input_ids += [pad_token] * padding_length
        input_mask += [0 if mask_padding_with_zero else 1] * padding_length
        segment_ids += [pad_token_segment_id] * padding_length
        label_ids += [pad_token] * padding_length
        # """
        # assert len(input_ids) == max_seq_length
        # assert len(input_mask) == max_seq_length
        # assert len(segment_ids) == max_seq_length
        # assert len(label_ids) == max_seq_length
        # """
        feature = InputFeature(input_ids=input_ids, input_mask=input_mask, input_len=input_len, segment_ids=segment_ids, label_ids=label_ids)
        return feature  # features is a list of InputFeatures

    def feature_to_dataset(self, features: list) -> TensorDataset:
        all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
        all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
        all_segment_ids = torch.tensor([f.segment_ids for f in features], dtype=torch.long)
        all_label_ids = torch.tensor([f.label_ids for f in features], dtype=torch.long)
        all_lens = torch.tensor([f.input_len for f in features], dtype=torch.long)
        dataset = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_label_ids, all_lens)
        return dataset


    def covert_str_to_feature(self, input_text: str):
        max_seq_length=MAX_EMBEDDING_LENS
        cls_token="[CLS]"
        cls_token_segment_id=1
        sep_token="[SEP]"
        pad_token=0
        pad_token_segment_id=0
        sequence_a_segment_id=0
        mask_padding_with_zero=True
        special_tokens_count=2

        tokens = self.tokenizer.tokenize(input_text)
        label_ids = []
        # Cut the tokens if tokens is longer than max_seq_length.
        if len(tokens) > max_seq_length - special_tokens_count:
            tokens = tokens[: (max_seq_length - special_tokens_count)]
        tokens += [sep_token]
        segment_ids = [sequence_a_segment_id] * len(tokens)
        # Add [CLS] to the head of token list.
        tokens = [cls_token] + tokens
        segment_ids = [cls_token_segment_id] + segment_ids
        # Code for adding [CLS] token ENDs here.
        input_ids = self.tokenizer.convert_tokens_to_ids(tokens)
        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)
        input_len = len(input_ids)
        # Zero-pad up to the sequence length.
        padding_length = max_seq_length - len(input_ids)
        # Pad on right.
        input_ids += [pad_token] * padding_length
        input_mask += [0 if mask_padding_with_zero else 1] * padding_length
        segment_ids += [pad_token_segment_id] * padding_length
        # """
        # assert len(input_ids) == max_seq_length
        # assert len(input_mask) == max_seq_length
        # assert len(segment_ids) == max_seq_length
        # assert len(label_ids) == max_seq_length
        # """
        f = InputFeature(input_ids=input_ids, input_mask=input_mask, input_len=input_len, segment_ids=segment_ids, label_ids=None)
        all_input_ids = torch.tensor([f.input_ids], dtype=torch.long)
        all_input_mask = torch.tensor([f.input_mask], dtype=torch.long)
        all_segment_ids = torch.tensor([f.segment_ids], dtype=torch.long)
        all_lens = torch.tensor([f.input_len], dtype=torch.long)
        return all_input_ids, all_input_mask, all_segment_ids, all_lens
