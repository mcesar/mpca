#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree

def transitive_closure(a):
    closure = set(a)
    while True:
        new_relations = set((x,w) for x,y in closure for q,w in closure if q == y)
        closure_until_now = closure | new_relations
        if closure_until_now == closure:
            break
        closure = closure_until_now
    return closure

def warshall(a):
    assert (len(row) == len(a) for row in a)
    n = len(a)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                a[i][j] = a[i][j] or (a[i][k] and a[k][j])
    return a

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	parser.add_argument("-i", "--ignore", default='')
	args = parser.parse_args()

	ignore = args.ignore.split(',')

	print('Parsing LDI')
	root = etree.parse(args.file).getroot()
	elements = {}
	for e1 in root:
		elements[e1.attrib['name']] = []
		for e2 in e1:
			if 'kind' in e2.attrib:
				kind = e2.attrib['kind']
			else:
				kind = 'static'
			if kind in ignore:
				continue
			elements[e1.attrib['name']].append(e2.attrib['provider'])

	print('Building matrix')
	matrix = []
	for k1 in iter(elements):
		row = []
		matrix.append(row)
		for k2 in iter(elements):
			row.append(k2 in elements[k1])

	total_impact = 0
	print('Computing transitive closure')
	print(len(matrix))
	exit()
	w = warshall(matrix)
	print('Computing metric')
	for i in range(len(w)):
		for j in range(len(w)):
			if w[i][j]:
				total_impact += 1

	print(total_impact/len(w))