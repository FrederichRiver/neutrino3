import jieba
import jieba.analyse

text = open('/data1/file_data/corpus/0a1d1de122c53a708f9a18273f0852ff', 'r').read()
print(text)
div = jieba.cut_for_search(text)
print(div)
tfidf = jieba.analyse.extract_tags(text, topK=20, withWeight=False)
print(tfidf)