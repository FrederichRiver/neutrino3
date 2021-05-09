#!/usr/bin/python38
import os


data_path = '/home/friederich/Dev/NER-BERT-pytorch/data/msra/val'
word_file = os.path.join(data_path, 'sentences.txt')
tag_file = os.path.join(data_path, 'tags.txt')
with open(word_file, 'r') as f1:
    result1 = f1.readlines()

with open(tag_file, 'r') as f2:
    result2 = f2.readlines()

with open(os.path.join(data_path, 'mrsa_train.txt'), 'w') as f:
    f.write('-DOCSTART-\n')
    for line1, line2 in zip(result1, result2):
        word1 = line1.split()
        word2 = line2.split()
        line = zip(word1, word2)
        for w, t in line:
            f.write(f"{w} {t}\n")
        f.write('\n')
