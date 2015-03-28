#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree

def draw_rectangle(x, y, width, height, fill_color):
	fill = ''
	if fill_color:
		fill = 'fill="{}"'.format(fill_color)
	print('	<rect width="{}" height="{}" x="{}" y="{}" {} stroke="{}" />'.format(width,height,y,x,fill,fill_color));

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	parser.add_argument("-i", "--ignore", default='')
	parser.add_argument("-d", "--dot_size", type=int, default=1)
	args = parser.parse_args()

	ignore = args.ignore.split(',')

	root = etree.parse(args.file).getroot()
	names = []
	indexes = {}
	matrix = []
	for e1 in root:
		names.append(e1.attrib['name'])
	index = 0
	for n in sorted(names):
		indexes[n] = index
		index += 1
	for e1 in root:
		for e2 in e1:
			if 'kind' in e2.attrib:
				kind = e2.attrib['kind']
			else:
				kind = 'static'
			if kind in ignore:
				continue
			if e2.attrib['provider'] in indexes:
				matrix.append((indexes[e1.attrib['name']], indexes[e2.attrib['provider']], kind))
	print('<?xml version="1.0" standalone="no"?>')
	print('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
	print('<svg width="{}px" height="{}px" version="1.1" xmlns="http://www.w3.org/2000/svg">'.format(len(indexes), len(indexes)))
	print('<g fill="none" stroke-width="{}" >'.format(args.dot_size))
	processed = set()
	for element in matrix:
		if element[2] != 'static':
			continue
		draw_rectangle(element[0], element[1], 1, 1, 'black')
		processed.add((element[0], element[1]))
	for element in matrix:
		if element[2] != 'evolutionary' or (element[0], element[1]) in processed:
			continue
		draw_rectangle(element[0], element[1], 1, 1, 'red')
	print("</g>")
	print('<g fill="none" stroke="black" stroke-width="{}" >'.format(args.dot_size * 4))
	draw_rectangle(0, 0, len(indexes), len(indexes), '')
	print("</g>")
	print("</svg>")