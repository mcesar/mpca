#!/usr/local/bin/python3

import logging
from gensim import corpora, models, similarities

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

documents = ["Human machine interface for lab abc computer applications",
              "A survey of user opinion of computer system response time",
              "The EPS user interface management system",
              "System and human system engineering testing of EPS",
              "Relation of user perceived response time to error measurement",
              "The generation of random binary unordered trees",
              "The intersection graph of paths in trees",
              "Graph minors IV Widths of trees and well quasi ordering",
              "Graph minors A survey"]

stoplist = set('for a of the and to in'.split())

texts = [[word for word in document.lower().split() if word not in stoplist]
          for document in documents]

all_tokens = sum(texts, [])
tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
texts = [[word for word in text if word not in tokens_once]
          for text in texts]

# ***************

dictionary = corpora.Dictionary(texts)
#dictionary.save('/tmp/deerwester.dict') # store the dictionary, for future reference

corpus = [dictionary.doc2bow(text) for text in texts]
#corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus)

tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
corpus_tfidf = tfidf[corpus]

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2)
corpus_lsi = lsi[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi

index = similarities.MatrixSimilarity(corpus_lsi) # transform corpus to LSI space and index it

sims = index[lsi[corpus[0]]]
sims = sorted(enumerate(sims), key=lambda item: -item[1])

print(sims)
