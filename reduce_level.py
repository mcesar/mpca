#!/usr/local/bin/python3

import sys
import argparse
import xml.etree.ElementTree as etree

def reduce_level(str, n, s, fix):
	result = str
	if fix:
		result = result.partition('.src.main.')[0]
		result = result.partition('.src.test.')[0]
	skipped = ''
	for x in xrange(0, s):
		p = result.rpartition('.')
		skipped = '.' + p[2] + skipped
		result = p[0]
	for x in xrange(0, n):
		result = result.rpartition('.')[0]
	return result + skipped

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file", default='')
	parser.add_argument("-n", "--levels", default=2, type=int)
	parser.add_argument("-s", "--skip", default=0, type=int)
	parser.add_argument("-i", "--ignore", default='')
	parser.add_argument("-e", "--exclude", default='')
	parser.add_argument("-x", "--fix_geronimo", action="store_true", default=False)
	args = parser.parse_args()

	ignore = args.ignore.split(',')

	f = args.file
	if len(f) == 0:
		f = sys.stdin
	root = etree.parse(f).getroot()
	elements = {}
	for e1 in root:
		if args.exclude and args.exclude in e1.attrib['name']:
			continue
		element = reduce_level(e1.attrib['name'], args.levels, args.skip, args.fix_geronimo)
		if element not in elements:
		 	elements[element] = {}
		for e2 in e1:
			if args.exclude and args.exclude in e2.attrib['provider']:
				continue
		 	provider = reduce_level(e2.attrib['provider'], args.levels, args.skip, args.fix_geronimo)
		 	if 'kind' in e2.attrib:
		 		kind = e2.attrib['kind']
		 	else:
		 		kind = 'static'
		 	if kind in ignore:
		 		continue
		 	key = provider + '|' + kind
		 	if key not in elements[element] and element != provider:
		 		elements[element][key] = {'name': provider, 'kind': kind}

	print("<?xml version=\"1.0\" ?>\n<ldi>\n")
	for e, providers in elements.items():
		print("<element name=\"{}\">".format(e))
		for p in providers.values():
			print("	<uses provider=\"{}\" kind=\"{}\"/>".format(p['name'],p['kind']))
		print("</element>")
	print("</ldi>")