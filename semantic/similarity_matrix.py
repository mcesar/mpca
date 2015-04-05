#!/usr/local/bin/python3

import os
import sys
import logging
from gensim import corpora, models, similarities
import argparse
import filesystem

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", default=".")
parser.add_argument("-d", "--destination", default=".")
parser.add_argument("-g", "--granularity", default="coarse")
args = parser.parse_args()

filepaths = filesystem.find(args.source,'*')

if args.granularity == 'coarse':
	entity_types = ['CL','IN']
else:
	entity_types = ['MT','FE','CN']

entities_paths = []
for path in filepaths:
	if path.endswith('.c'):
		continue
	arr = path.split('/')
	if len(arr) < 2: 
		continue
	entity_type = arr[-2:-1][0]
	if not entity_type in entity_types: 
		continue
	entities_paths.append(path)

texts = []
for file_name in entities_paths:
	f = open(file_name)
	text = []
	texts.append(text)
	for word in f:
		text.append(word.strip())

all_tokens = sum(texts, [])
tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
texts = [[word for word in text if word not in tokens_once]
          for text in texts]

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]
# TODO: calibrate num_topics (no artigo do Kuhn se fala em 20 a 50)
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=50) 
corpus_lsi = lsi[corpus_tfidf]
index = similarities.MatrixSimilarity(corpus_lsi)

if args.destination == '.':
	for row in index:
	  first = True
	  for col in row:
	    if not first:
	      print(",",end="")
	    first = False
	    print(col, end="")
	  print("")
else:
	index.save(args.destination)