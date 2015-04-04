#!/usr/bin/python

import sys
import nltk
from nltk.corpus import stopwords

stop = stopwords.words('english')

porter = nltk.PorterStemmer()
# [porter.stem(t) for t in tokens]

processed = set()

for token in sys.stdin:
	t = token.lower().strip()
	if t not in stop:
		t = porter.stem(t)
		if t not in processed and len(t) > 1 and not t.isdigit():
			processed.add(t)
			print(t)
