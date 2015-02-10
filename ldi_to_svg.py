#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree

def draw_rectangle(x, y, width, height):
	fill = ''
	if width == 1 and height == 1:
		fill = 'fill="black"'
	print('	<rect width="{}" height="{}" x="{}" y="{}" {} />'.format(width,height,y,x,fill));


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	parser.add_argument("-i", "--ignore", default='')
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
				matrix.append((indexes[e1.attrib['name']], indexes[e2.attrib['provider']]))
	print('<?xml version="1.0" standalone="no"?>')
	print('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
	print('<svg width="{}px" height="{}px" version="1.1" xmlns="http://www.w3.org/2000/svg">'.format(len(indexes), len(indexes)))
	print('<g fill="none" stroke="black" stroke-width="0.25" >')
	for element in matrix:
		draw_rectangle(element[0], element[1], 1,1)
	print("</g>")
	print("</svg>")

	# private static void printRectangle(PrintStream printStream, int x, int y,
	# 		int width, int height) {
	# 	// coordinates in SVG are inverse from the matrix coordinates
	# 	printStream.println("    <rect width=\"" + width + "\"  " +
	# 									"height=\"" + height + "\" " +
	# 									"x=\"" + y + "\" " +
	# 									"y=\"" + x + "\" " +
	# 									(width == 1 && height == 1 ? " fill=\"black\" " : "") + "/>");

	# }