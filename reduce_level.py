#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree

def reduce_level(str, n, fix):
	result = str
	if fix:
		result = result.partition('.src.main.')[0]
		result = result.partition('.src.test.')[0]
	for x in xrange(0,n):
		result = result.rpartition('.')[0]
	return result

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	parser.add_argument("-n", "--levels", default=2, type=int)
	parser.add_argument("-x", "--fix_geronimo", action="store_true", default=False)
	args = parser.parse_args()

	root = etree.parse(args.file).getroot()
	elements = {}
	for e1 in root:
		 element = reduce_level(e1.attrib['name'], args.levels, args.fix_geronimo)
		 if element not in elements:
		 	elements[element] = []
		 for e2 in e1:
		 	provider = reduce_level(e2.attrib['provider'], args.levels, args.fix_geronimo)
		 	if provider not in elements[element] and element != provider:
		 		elements[element].append(provider)

	print("<?xml version=\"1.0\" ?>\n<ldi>\n")
	for e, providers in elements.items():
		print("<element name=\"{}\">".format(e))
		for p in providers:
			print("	<uses provider=\"{}\" />".format(p))
		print("</element>")
	print("</ldi>")