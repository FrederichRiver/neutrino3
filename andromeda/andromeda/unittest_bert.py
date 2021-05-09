#!/usr/bin/python38
import unittest
import data
from torch.utils.data import DataLoader
from andromeda.model_tool import collate_fn
from torch import tensor

label_list = [
    "X",
    'B-CONT', 'B-EDU', 'B-LOC', 'B-NAME', 'B-ORG',
    'B-PRO', 'B-RACE', 'B-TITLE', 'I-CONT', 'I-EDU',
    'I-LOC', 'I-NAME', 'I-ORG', 'I-PRO', 'I-RACE',
    'I-TITLE', 'O', 'S-NAME', 'S-ORG', 'S-RACE',
    "[START]", "[END]"]

label_index = [i for i in range(len(label_list))]


class BERT_Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skip('pass')
    def test_tokenizer(self):
        from andromeda.model import CNerTokenizer
        from andromeda.model_config import bert_config
        tokenizer = CNerTokenizer.from_pretrained('bert-base-chinese', config=bert_config, bos_token='[BOS]', eos_token='[EOS]')
        content = "Test words. 测试文字。"
        result = tokenizer.tokenize(content)
        print(result)

    @unittest.skip('pass')
    def test_bertcrfmodel(self):
        from andromeda.model import BertCRFModel
        from andromeda.model_config import bert_config
        model = BertCRFModel(config=bert_config)
        feature_param = {
            "max_seq_length": 20,
            "cls_token": "[CLS]",
            "cls_token_segment_id": 1,
            "sep_token": "[SEP]",
            "pad_token": 0,
            "pad_token_segment_id": 0,
            "sequence_a_segment_id": 0,
            "mask_padding_with_zero": True
        }
        data_dir = '/home/friederich/Documents/bert_model/data/cner/'
        processor = data.DataEngine()
        label_list = processor.get_labels()
        examples = processor.get_train_examples(data_dir)
        # print(examples[0])
        features = processor.convert_examples_to_features(examples=examples,
                                                label_list=label_list,
                                                **feature_param
                                                )
        train_dataset = processor.feature_to_dataset(features)
        train_dataloader = DataLoader(train_dataset, shuffle=False, collate_fn=collate_fn, batch_size=1)
        model.train()
        for step, batch in enumerate(train_dataloader):
            # batch = tuple(t.to(args['device']) for t in batch)
            # inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[3], 'input_lens': batch[4]}
            inputs = {"input_ids": batch[0], "attention_mask": batch[1], 'input_lens': batch[4]}
            inputs["token_type_ids"] = batch[2]
            outputs = model(**inputs)
            logits = outputs[0]
            tags = model.crf.decode(logits, inputs['attention_mask'])
            tags  = tags.squeeze(0).cpu().numpy().tolist()
            print(inputs["input_ids"])
            print(batch[3].squeeze(0).numpy().tolist())
            print(tags)
            break

    def test_load_model(self):


if __name__ == "__main__":
    unittest.main()
