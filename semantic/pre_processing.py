#!/usr/bin/python

import sys
import argparse
import nltk
from nltk.corpus import stopwords

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--code_page", default="utf-8")
parser.add_argument("-l", "--language", default="english")
parser.add_argument("-d", "--allow_duplicates", default=False, action="store_true")
args = parser.parse_args()

stop = stopwords.words(args.language)

porter = nltk.PorterStemmer()
# [porter.stem(t) for t in tokens]

if args.allow_duplicates:
	processed = {}
else:
	processed = set()

for token in sys.stdin:
	t = token.lower().strip()
	t = unicode(t, args.code_page)
	if t not in stop:
		t = porter.stem(t)
		if len(t) > 1 and not t.isdigit():
			if t not in processed:
				if args.allow_duplicates:
					processed[t] = 1
				else:
					processed.add(t)
			elif args.allow_duplicates:
				processed[t] = processed[t] + 1

if args.allow_duplicates:
	for (k,v) in processed.items():
		print("%s\t%s" % (k,v))
else:
	for t in processed:
		print(t.encode('utf-8'))
