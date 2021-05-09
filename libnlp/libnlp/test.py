#!/usr/bin/python38
import unittest
from libnlp.model.bert_model import BertCRFModel, CNerTokenizer


class BERT_Test(unittest.TestCase):
    def setUp(self):
        print("Test start.")

    def tearDown(self):
        print("Test finished.")

    # @unittest.skip('Skip')
    def test_bertcrfmodel(self):
        from .model.model_config import bert_config
        model = BertCRFModel(config=bert_config)
        print(model)

    # @unittest.skip('Skip')
    def test_classify(self):
        from .model.model_config import bert_config
        model = BertCRFModel(config=bert_config)
        model.eval()

    def test_token(self):
        tokenizer = CNerTokenizer.from_pretrained('bert-base-chinese')
        result = tokenizer.tokenize("分词测试")
        print(result)


if __name__ == "__main__":
    unittest.main()
