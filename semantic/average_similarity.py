#!/usr/local/bin/python3

import os
import sys
import argparse
import filesystem
from gensim import similarities

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", default=".")
parser.add_argument("-i", "--index_source", default=".")
parser.add_argument("-p", "--prefix", default="corpus")
parser.add_argument("-g", "--granularity", default="coarse")
parser.add_argument("-m,", "--print_modules_count", default=False, action="store_true")
parser.add_argument("-v,", "--verbose", default=False, action="store_true")
args = parser.parse_args()

filepaths = filesystem.find(args.source,'*')

if args.granularity == 'coarse':
	entity_types = ['CL','IN']
else:
	entity_types = ['MT','FE','CN']

modules = {}
for path in filepaths:
	if path.endswith('.c'):
		continue
	arr = path.split('/')
	if len(arr) < 2: 
		continue
	entity_type = arr[-2:-1][0]
	if not entity_type in entity_types: 
		continue
	# entities_paths.append(path)
	module_path = '/'.join(arr[0:-3])
	if module_path not in modules:
		modules[module_path] = []
	modules[module_path].append(path)

if args.print_modules_count:
	print(len(modules))
	exit()

path_index = {}
i = 0
for path in open(os.path.join(args.index_source, args.prefix + '.index')):
	path_index[path.strip()] = i
	i = i + 1

index = similarities.Similarity.load(
	os.path.join(args.index_source, args.prefix + '.sm'))

# index_arr = []
# for row in index:
# 	row_arr = []
# 	index_arr.append(row_arr)
# 	for col in row:
# 		pass
# 	 	row_arr.append(col)

sum_m = 0
count = 0
for (module,paths) in modules.items():
	n = len(paths) 
	if n <= 1:
		continue
	sum = 0
	for i, path1 in enumerate(paths):
		v = index.similarity_by_id(path_index[path1])
		for j, path2 in enumerate(paths):
			if j >= i or path1 == path2:
				continue
			sum += v[path_index[path2]]
	CCM = sum/(n*(n-1)/2) #Conceptual Coesion of Module
	if CCM < 0: CCM = 0
	if args.verbose:
		print(module, CCM)
	sum_m += CCM
	count += 1
print(sum_m/count)
