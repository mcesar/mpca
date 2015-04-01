#!/usr/local/bin/python3

import std
import logging
from gensim import corpora, models, similarities

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

texts = []
for file_name in sys.stdin:
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
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=20) # TODO: calibrate num_topics (no artigo do Kuhn se fala em 20 a 50)
corpus_lsi = lsi[corpus_tfidf]
index = similarities.MatrixSimilarity(corpus_lsi)

# TODO: verify if the entire set of documents must be processed or only the ones contained on cluster/package
selected_corpus = [c for c in corpus] # TODO: add a 'if' condition
for c in selected_corpus:
	sims = index[lsi[c]]
	sims = [c for c in sorted(enumerate(sims), key=lambda item: -item[1]) ] # TODO add the same 'if' condition
	print(sims) # print the similarities of the c document regarding the other documents in the cluster/package
