#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	args = parser.parse_args()

	root = etree.parse(args.file).getroot()
	elements = {}
	for e1 in root:
		elements[e1.attrib['name']] = {}
		for e2 in e1:
			if e2.attrib['kind'] == 'static':
				elements[e1.attrib['name']][e2.attrib['provider']] = e2.attrib['kind']
	
	for e1 in root:
		if e1.attrib['name'] not in elements: elements[e1.attrib['name']] = {}
		for e2 in e1:
			if e2.attrib['provider'] not in elements[e1.attrib['name']]:
				elements[e1.attrib['name']][e2.attrib['provider']] = e2.attrib['kind']

	print("<?xml version=\"1.0\" ?>\n<ldi>\n")
	for e, item in elements.items():
		print("<element name=\"{}\">".format(e))
		for p,kind in item.items():
			print("	<uses provider=\"{}\" kind=\"{}\"/>".format(p,kind))
		print("</element>")
	print("</ldi>")