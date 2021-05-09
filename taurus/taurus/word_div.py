#!/usr/bin/python38
from polaris.mysql8 import NLP_HEADER, mysqlBase
import jieba
import pyhanlp


class NLPBase(mysqlBase):
    def __init__(self, header) -> None:
        super(NLPBase, self).__init__(header)


class PreOperator(mysqlBase):
    def __init__(self, header) -> None:
        super(PreOperator, self).__init__(header)
        self.article_path = '/home/friederich/Downloads/news/'

    def _get_text_from_article(self, idx: str) -> str:
        """
        Query file name from natural_language.article,
        then get the content of file.
        """
        filehash = self.select_one('article', 'content', 'idx=138100')
        filename = self.article_path + filehash[0]
        with open(filename, 'r') as f:
            result = f.read()
        return result


class WordDiv(object):
    def __init__(self, method='bert') -> None:
        pass

class nlp(NLPBase):
    def __init__(self, header):
        super(nlp, self).__init__(header)

    def get_text(self):
        result = self.select_one('article', 'content', 'idx=138100')
        with open('/home/friederich/Downloads/tmp/text', 'w') as f:
            f.write(result[0])

    def read_text(self):
        with open('/home/friederich/Downloads/tmp/text', 'r') as f:
            result = f.read()
        return result

    def process_text(self, content: str):
        result = jieba.cut(content)
        print('|'.join(result))
        return result

    def posseg(self, content: str):
        import jieba.posseg as psg
        result = psg.cut(content)
        # print(' '.join([f"{w}/{t}" for w, t in result]))
        print(type(result))

    def get_stopword(self):
        stopword_dict = '/home/friederich/Documents/dict/stopwords.txt'
        swd = [line.strip() for line in open(stopword_dict, 'r').readlines()]
        print(swd)

    def test(self, content):
        import nltk
        token = nltk.word_tokenize(content, language='')
        print(token)
        tagged = nltk.pos_tag(token)
        print(tagged)
        entity = nltk.chunk.ne_chunk(tagged)
        print(entity)

    def hanlp_test(self, content):
        analyser = pyhanlp.PerceptronLexicalAnalyzer()
        segs = analyser.analyze(content)
        # print(segs)
        CRFNewSegment = pyhanlp.HanLP.newSegment('crf')
        term_list = CRFNewSegment.seg(content)
        # print(term_list)
        segment = pyhanlp.HanLP.newSegment().enableNameRecognize(True)
        term_list = segment.seg(content)
        print(term_list)


if __name__ == "__main__":
    event = nlp(NLP_HEADER)
    content = event.read_text()
    # token = event.posseg(content)
    # event.get_stopword()
    event.hanlp_test(content)
