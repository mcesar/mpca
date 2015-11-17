#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
import re
import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", default="")
parser.add_argument("-c", "--code_page", default="utf-8")
parser.add_argument("-l", "--language", default="english")
parser.add_argument("-d", "--allow_duplicates", default=False, action="store_true")
parser.add_argument("-t", "--html", default=False, action="store_true")
parser.add_argument("-o", "--output", default="")
args = parser.parse_args()

stop = stopwords.words(args.language)

porter = nltk.PorterStemmer()
# [porter.stem(t) for t in tokens]

if args.allow_duplicates:
	processed = {}
else:
	processed = set()

if args.file == "":
    f = sys.stdin
else:
    f = open(args.file)
if args.output == "":
    out = sys.stdout
else:
    out = open(args.output, 'w')

RE_WHITE_SPACES = re.compile("\s+")
if args.html:
    txt = BeautifulSoup(f, "html5lib").get_text()
    txt = re.sub(u"[^a-zA-Záàãéíóõúç]", " ", txt)
    tokens = RE_WHITE_SPACES.split(txt.strip())
else:
    tokens = f

for token in tokens:
	t = token.lower().strip()
        if args.code_page != 'none':
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
		out.write("%s\t%s\n" % (k,v))
else:
	for t in processed:
		out.write(t.encode('utf-8') + "\n")

if args.file != "":
    f.close()
if args.output != "":
    out.close()
