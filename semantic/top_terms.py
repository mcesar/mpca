#!/usr/local/bin/python3

import os
import re
import sys
import argparse
import filesystem
from gensim import similarities, corpora, models, matutils
import nltk
from nltk.corpus import stopwords

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", default=".")
parser.add_argument("-i", "--index_source", default=".")
parser.add_argument("-l", "--language", default="english")
parser.add_argument("-p", "--prefix", default="corpus")
parser.add_argument("-c", "--clusters", default="")
parser.add_argument("-f", "--frequency", default=False, action="store_true")
parser.add_argument("-e", "--entities", default=False, action="store_true")
parser.add_argument("-d", "--filter_based_on_documentation", default=False, action="store_true")
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

if args.entities:
    stop = stopwords.words(args.language)
    porter = nltk.PorterStemmer()
    if args.filter_based_on_documentation:
        filepaths = filesystem.find(args.source,'*')
        doc_words = set()
        for path in filepaths:
            if not path.endswith('.txt'):
                continue
            f = open(path)
            for l in f:
                doc_words.add(l.strip())
    all_terms = {}
    clusters_terms = {}
    for key in clusters.keys():
        terms = set()
        for entity in clusters[key]:
            words = re.sub("(?<=[A-Z])(?=[A-Z][a-z])|(?<=[^A-Z])(?=[A-Z])|(?<=[A-Za-z])(?=[^A-Za-z])", \
               " ", entity).split("/")
            for w in words:
                t = re.sub(u"[^a-zA-Záàãéíóõúç]", " ", w.lower()).strip()
                for t in t.split(" "):
                    if len(t) > 2 and t not in stop:
                        t = porter.stem(t)
                        if args.filter_based_on_documentation and t not in doc_words:
                            continue
                        terms.add(t)
                        if t in all_terms:
                            all_terms[t] += 1
                        else:
                            all_terms[t] = 1
        clusters_terms[key] = list(terms)
    byCommonality = lambda e : e[1]
    for key in clusters.keys():
        print(key, sorted( \
                [(e,0) if e not in all_terms else (e,-all_terms[e]) for e in clusters_terms[key]], \
                key=byCommonality, reverse=True))

elif args.frequency:
    keys = clusters.keys()
    # Collect frequencies
    clusters_terms = {}
    for key in keys:
        terms = {}
        clusters_terms[key] = terms
        for path in clusters[key]:
            fn = os.path.join(args.source, path)
            if os.path.isfile(fn):
                for l in open(fn):
                    arr = l.split('\t')
                    if arr[0].strip() not in terms:
                        terms[arr[0].strip()] = 0
                    terms[arr[0].strip()] = terms[arr[0].strip()] + int(arr[1].strip())
            else:
                print(fn)
    average_frequency = {}
    # Compute relevance of the terms comparing the frequency on all other clusters. See Kuhn (2007)
    for key in keys:
        for term in clusters_terms[key]:
            if term not in average_frequency:
                average_frequency[term] = 0
            average_frequency[term] = average_frequency[term] + clusters_terms[key][term]
    for term in average_frequency:
        average_frequency[term] = average_frequency[term] / len(clusters)
    for key in keys:
        for term in clusters_terms[key]:
            clusters_terms[key][term] = clusters_terms[key][term] - average_frequency[term]
    # Print results
    first = True
    for key in keys:
            if first:
                    first = False
            else:
                    print("")
            print("%s;" % key, end="")
            tfirst = True
            for k in sorted(clusters_terms[key], key=clusters_terms[key].get, reverse=True):
                    if tfirst:
                            tfirst = False
                    else:
                            print(",", end="")
                    print("%s:%d" % (k, clusters_terms[key][k]), end="")
else:
    #Load LSI index
    dictionary = corpora.Dictionary.load(
            os.path.join(args.index_source, args.prefix + '.dict'))
    lsi = models.LsiModel.load(
            os.path.join(args.index_source, args.prefix + '-t.lsi'))
    index_t = similarities.Similarity.load(
            os.path.join(args.index_source, args.prefix + '-t.sm'))
    terms = {}
    i = 0
    for term in open(os.path.join(args.index_source, args.prefix + '.terms')):
            terms[i] = term
            i = i + 1
    first = True
    sims = {}
    # Compute similarities
    for key in clusters:
            # Build a query from cluster's terms
            q = set()
            for path in clusters[key]:
                    fn = os.path.join(args.source, path)
                    if os.path.isfile(fn):
                            for l in open(fn):
                                    q.add(l.strip())
            # Perform query
            sims[key] = list(enumerate(index_t[lsi[dictionary.doc2bow(q)]]))
    # Compute averages
    averages = {}
    for key in clusters:
            for s in sims[key]:
                    if s[0] not in averages:
                            averages[s[0]] = 0
                    averages[s[0]] = averages[s[0]] + s[1]
    for k in averages.keys():
            averages[k] = averages[k] / len(clusters)
    # Compute relevance of the terms comparing the frequency on all other clusters. See Kuhn (2007)
    for key in clusters:
            new_sims = {}
            for s in sims[key]:
                    new_sims[s[0]] = (s[0], s[1] - averages[s[0]])
            sims[key] = new_sims.values()
    # Print results
    for key in clusters:
            if first:
                    first = False
            else:
                    print("")
            print("%s;" % key, end="")
            cluster_sims = sorted(sims[key], key=lambda item: -item[1])[0:100]
            tfirst = True
            for sim in cluster_sims:
                    if tfirst:
                            tfirst = False
                    else:
                            print(",", end="")
                    print("%s:%s:%s" % (sim[0],terms[sim[0]].strip(), sim[1]), end="")
