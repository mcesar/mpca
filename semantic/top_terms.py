#!/usr/local/bin/python3

import os
import sys
import argparse
import filesystem
from gensim import similarities, corpora, models

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", default=".")
parser.add_argument("-i", "--index_source", default=".")
parser.add_argument("-p", "--prefix", default="corpus")
parser.add_argument("-c", "--clusters", default="")
parser.add_argument("-k", "--cluster", default="")
parser.add_argument("-n", "--new_path_prefix", default="")
args = parser.parse_args()

clusters = {}
for cluster_entity in open(args.clusters):
	if '\"' in cluster_entity:
		arr = cluster_entity.split('\"')
		entity_path = arr[1]
		arr = arr[0].split(',')
		cluster_name = arr[4]
	else:
		arr = cluster_entity.split(',')
		cluster_name = arr[4]
		entity_path = arr[9]
	if cluster_name not in clusters:
		clusters[cluster_name] = []
	clusters[cluster_name].append(entity_path.replace('/CM/','/MT/'))

q = set()
for path in clusters[args.cluster]:
	for l in open(os.path.join(args.source, path)):
		q.add(l.strip())

print(q)

dictionary = corpora.Dictionary.load(
	os.path.join(args.index_source, args.prefix + '.dict'))

lsi = models.LsiModel.load(
	os.path.join(args.index_source, args.prefix + '.lsi'))

index_t = similarities.Similarity.load(
	os.path.join(args.index_source, args.prefix + '.sm'))

sims = index_t[lsi[dictionary.doc2bow(q)]]
sims = sorted(enumerate(sims), key=lambda item: -item[1])[0:20]
# print the result, converting ids (integers) to words (strings) 
fmt = ["%s(%s)" %(dictionary[idother], sim) for idother, sim in enumerate(sims) if idother in dictionary]

print("the query is similar to", ', '.join(fmt))