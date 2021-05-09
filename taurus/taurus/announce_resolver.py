#!/usr/bin/python38

import jieba
import re
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfpage import PDFPage

txtfile = '/home/friederich/Documents/test/Test2Pdf.txt'
pdffile = '/home/friederich/Documents/test/test.pdf'
fp = open(pdffile, 'rb')
p = PDFParser(fp)
doc = PDFDocument(p)
p.set_document(doc)
resm = PDFResourceManager()
laparam = LAParams()
device = PDFPageAggregator(resm, laparams=laparam)
interpreter = PDFPageInterpreter(resm, device)
for page in PDFPage.create_pages(doc):
    interpreter.process_page(page)
    layout = device.get_result()
    for x in layout:
        print(type(x))
print('end')
"""
with open(txtfile, 'r') as f:
    content = f.read()
# print(content)
seg = jieba.cut(content)
print('/'.join(seg))
"""