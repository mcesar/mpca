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
parser.add_argument("-m", "--print_modules_count", default=False, action="store_true")
parser.add_argument("-v", "--verbose", default=False, action="store_true")
parser.add_argument("-c", "--clusters", default="")
parser.add_argument("-n", "--new_path_prefix", default="")
parser.add_argument("-x", "--exclude_clusters", default=False, action="store_true")
parser.add_argument("-k", "--dont_use_cluster_name", default=False, action="store_true")
parser.add_argument("-f", "--ignore_not_found_paths", default=False, action="store_true")

args = parser.parse_args()

filepaths = filesystem.find(args.source,'*')
if len(filepaths) == 0:
        print('Source path not found', args.source)
        exit()

if args.granularity == 'coarse':
        entity_types = ['CL','IN']
else:
        entity_types = ['MT','FE','CN']

clusters = {}
if args.clusters != "":
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
                clusters[entity_path.replace('/CM/','/MT/')] = cluster_name

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
        module_path = '/'.join(arr[0:-3])
        if args.clusters != "":
                key = path.replace(args.source, '')
                if key in clusters:
                        if args.exclude_clusters:
                                module_path = ''
                        elif not args.dont_use_cluster_name:
                                module_path = clusters[key]
                else:
                        if not args.exclude_clusters:
                                module_path = ''
        if module_path != '':
                if module_path not in modules:
                        modules[module_path] = []
                modules[module_path].append(path)

if args.print_modules_count:
        s = 0
        for v in modules.values():
                s += len(v)
        print(len(modules), s)
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
#       row_arr = []
#       index_arr.append(row_arr)
#       for col in row:
#               pass
#               row_arr.append(col)

sum_m = 0
count = 0
min_cohesion = {'module':'','CCM':1, 'n':0, 'paths':[]}
max_cohesion = {'module':'','CCM':0, 'n':0, 'paths':[]}
min_elements = {'module':'','CCM':0, 'n':99999, 'paths':[]}
max_elements = {'module':'','CCM':0, 'n':0, 'paths':[]}
for (module,paths) in modules.items():
        n = len(paths)
        if n <= 1:
                continue
        sum = 0
        for i, path1 in enumerate(paths):
                if args.new_path_prefix != '':
                        path1 = path1.replace(args.source, args.new_path_prefix)
                if args.ignore_not_found_paths and path1 not in path_index:
                    continue
                v = index.similarity_by_id(path_index[path1])
                for j, path2 in enumerate(paths):
                        if args.new_path_prefix != '':
                                path2 = path2.replace(args.source, args.new_path_prefix)
                        if j >= i or path1 == path2:
                                continue
                        sum += v[path_index[path2]]
        CCM = sum/(n*(n-1)/2) #Conceptual Coesion of Module
        if CCM < 0: CCM = 0
        if args.verbose:
                print(module, CCM)
        if CCM < min_cohesion['CCM'] and CCM > 0:
            min_cohesion['module'] = module
            min_cohesion['CCM'] = CCM
            min_cohesion['n'] = n
            if args.verbose:
                min_cohesion['paths'] = paths
        if CCM > max_cohesion['CCM']:
            max_cohesion['module'] = module
            max_cohesion['CCM'] = CCM
            max_cohesion['n'] = n
            if args.verbose:
                max_cohesion['paths'] = paths
        if n < min_elements['n'] and CCM > 0:
            min_elements['module'] = module
            min_elements['CCM'] = CCM
            min_elements['n'] = n
            if args.verbose:
                min_elements['paths'] = paths
        if n > max_elements['n']:
            max_elements['module'] = module
            max_elements['CCM'] = CCM
            max_elements['n'] = n
            if args.verbose:
                max_elements['paths'] = paths
        sum_m += CCM
        count += 1
print('\nAVG', sum_m/count, '\nMIN_COH', min_cohesion, '\nMAX_COH', max_cohesion, '\nMIN_ELE', min_elements, '\nMAX_ELE', max_elements)
