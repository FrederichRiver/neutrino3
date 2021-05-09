#!/usr/bin/python38

import jieba.analyse
from libcontext.model import formArticle
from libmysql_utils.mysql8 import mysqlBase, mysqlHeader


class NLPBase(mysqlBase):
    def __init__(self, header: mysqlHeader):
        super(NLPBase, self).__init__(header)


class NewsBase(NLPBase):
    def news_title(self, idx: int) -> str:
        result = self.session.query(formArticle.title).filter_by(idx=idx).one()
        if result:
            title = result[0]
        else:
            title = ""
        return title

    def news_text(self, idx: int):
        result = self.session.query(formArticle.content).filter_by(idx=idx).one()
        if result:
            content = result[0]
        else:
            content = ""
        return content

    def news_idx(self):
        result = self.session.query(formArticle.idx).filter(formArticle.keyword.is_(None)).all()
        idx_list = [i[0] for i in result]
        return idx_list

    def update_keyword(self, idx: int, text: str):
        tags = jieba.analyse.extract_tags(text, topK=10)
        kw = ','.join(tags)
        self.session.query(formArticle).filter_by(idx=idx).update({"keyword": kw})
        self.session.commit()

    def all_news(self):
        result = self.session.query(formArticle).all()
        return result


if __name__ == '__main__':
    nlp_head = mysqlHeader('stock', 'stock2020', 'natural_language')
    event = NewsBase(nlp_head)
    idx_list = event.news_idx()
    for idx in idx_list:
        title = event.news_title(idx)
        print(title)
        text = event.news_text(idx)
        if text:
            event.update_keyword(idx, text)
