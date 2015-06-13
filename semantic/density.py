#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	args = parser.parse_args()

	root = etree.parse(args.file).getroot()
	clusters = {}
	for e1 in root:
		cluster = e1.attrib['name'][:e1.attrib['name'].index('.')]
		if cluster not in clusters:
			clusters[cluster] = {"V":0,"E":0}
		clusters[cluster]["V"] += 1
		for e2 in e1:
			clusterp = e2.attrib['provider'][:e1.attrib['provider'].index('.')]
			if cluster == clusterp:
				clusters[cluster]["E"] += 1
	print(clusters)