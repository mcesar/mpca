#!/usr/bin/python

import sys
import argparse
import nltk
from nltk.corpus import stopwords

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--code_page", default="utf-8")
parser.add_argument("-l", "--language", default="english")
args = parser.parse_args()

stop = stopwords.words(args.language)

porter = nltk.PorterStemmer()
# [porter.stem(t) for t in tokens]

processed = set()

for token in sys.stdin:
	t = token.lower().strip()
	t = unicode(t, args.code_page)
	if t not in stop:
		t = porter.stem(t)
		if t not in processed and len(t) > 1 and not t.isdigit():
			processed.add(t)
			print(t.encode('utf-8'))
