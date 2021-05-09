#!/usr/bin/python38
import copy
import json
import torch
from torch.utils.data import TensorDataset
from libnlp.dataset.cner import InputSample


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


def collate_to_tuple(batch: tuple) -> tuple:
    """
    batch should be a list of (sequence, target, length) tuples...
    Returns a padded tensor of sequences sorted from longest to shortest,
    """
    all_input_ids, all_attention_mask, all_token_type_ids, all_lens = map(torch.stack, zip(*batch))
    # max_len = max(all_lens).item()
    max_len = 768
    all_input_ids = all_input_ids[:, :max_len]
    all_attention_mask = all_attention_mask[:, :max_len]
    all_token_type_ids = all_token_type_ids[:, :max_len]
    # all_labels = all_labels[:, :max_len]
    #      batch[0]      batch[1]             batch[2]           batch[3]
    return all_input_ids, all_attention_mask, all_token_type_ids, all_lens


def example_to_feature(
        tokenizer, example: InputSample, label_map: dict,
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
    dataset = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_lens, all_label_ids)
    return dataset
