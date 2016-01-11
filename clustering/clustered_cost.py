#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree

def dependency_cost(d1, d2, busses, clusters, lamb, dsm_size):
	if d2 in busses:
		return 1
	elif cluster_name(d1) == cluster_name(d2):
		return pow(clusters[cluster_name(d1)], lamb)
	else:
		return pow(dsm_size, lamb)

def cluster_name(full_name):
	return full_name.rpartition('.')[0]

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	parser.add_argument("-l", "--lamb", default=2, type=int)
	parser.add_argument("-b", "--bus_threshold", default=0.1, type=float)
	args = parser.parse_args()

	dsm_size = 0
	columns = {}
	busses = []
	clusters = {}
	clustered_cost = 0
	dependency_count = 0

	root = etree.parse(args.file).getroot()
	elements = {}
	for e1 in root:
		dsm_size += 1
		cname = cluster_name(e1.attrib['name'])
		if cname not in clusters:
			clusters[cname] = 0
		clusters[cname] += 1
		for e2 in e1:
			dependency_count += 1
			if e2.attrib['provider'] not in columns:
				columns[e2.attrib['provider']] = 0
			columns[e2.attrib['provider']] += 1

	for b, c in columns.items():
		if c / dsm_size > args.bus_threshold:
			busses.append(b)

	for e1 in root:
		for e2 in e1:
			clustered_cost += dependency_cost(e1.attrib['name'], e2.attrib['provider'], busses, clusters, args.lamb , dsm_size)

	print(len(clusters), dsm_size, dependency_count, clustered_cost)
