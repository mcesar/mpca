#!/usr/local/bin/python3

import argparse
import os
import re
from glob import glob
from db import Db
import constants
import util
import dependencias_estaticas as simplifier

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--repository")
parser.add_argument("-a", "--all_levels", action="store_true", default=False)
args = parser.parse_args()

db = Db()

classes = {}
dependencies = {}

def load_db_entities():
	print('Carregando classes e entidades...')
	cursor = db.query("select id, caminho, tipo from entidades where repositorio = %s order by caminho", 
		(constants.repository_map[args.repository],))
	for id, path, type in cursor:
		if type in ('CL', 'IN'):
			class_id = id
			classes[id] = []
		else:
			classes[class_id].append({'id': id, 'path': path, 'type': type})

def load_dependencies():
	print('Carregando dependências fine grained...')
	cursor = db.query("""
			select e1.id, e2.id, e2.caminho, e2.tipo
			from dependencias d 
				inner join entidades e1 on d.entidade1 = e1.id
				inner join entidades e2 on d.entidade2 = e2.id
			where e1.repositorio = %s""", 
		(constants.repository_map[args.repository],))
	for id1, id2, path, etype in cursor:
		if int(id1) not in dependencies:
			dependencies[int(id1)] = []
		dependencies[int(id1)].append({'id': id2, 'path': path, 'type': etype})
	print('Carregando dependências coarse grained...')
	cursor = db.query("""
			select e1.id, e2.id, e2.caminho, e2.tipo
			from dependencias_coarse_grained d 
				inner join entidades e1 on d.entidade1 = e1.id
				inner join entidades e2 on d.entidade2 = e2.id
			where e1.repositorio = %s""", 
		(constants.repository_map[args.repository],))
	for id1, id2, path, etype in cursor:
		if int(id1) not in dependencies:
			dependencies[int(id1)] = []
		dependencies[int(id1)].append({'id': id2, 'path': path, 'type': etype})

def clusters_files():
	""" recover the list of files containing the clusters, sorted by ascending level """
	files = [y for x in os.walk('.') for y in glob(os.path.join(x[0], '*.mdgL*.dot'))]
	clusters_files = []
	clusters_dict = {}
	for file in files:
		file_name = file.rpartition('/')[2]
		if ('fine_grained' in file or 'coarse_grained' in file) and file_name.startswith(args.repository):
			if args.all_levels:
				new_file_name = re.sub('\.mdgL\d+\.','.mdgAllLevels.', file_name)
				path = re.sub('\.mdgL\d+\.','.mdgAllLevels.', file)
				if path not in clusters_dict:
					clusters_dict[path] = {'name': new_file_name, 'path': path, 'subfiles': []}
				clusters_dict[path]['subfiles'].append([file_name,int(file_name.partition('.mdgL')[2].partition('.')[0])])
			else:
				clusters_files.append({'name': file_name, 'path': file})
	if args.all_levels:
		clusters_files = clusters_dict.values()
		for c_f in clusters_files:
			c_f['subfiles'] = sorted(c_f['subfiles'], key = lambda sf : sf[1])
	return clusters_files

def entities_clusters_map(file):
	""" builds a dict containing the clusters names of the entities, plus entities attributes """
	if file['name'].endswith('.mdgAllLevels.dot'):
		files = [arr[0] for arr in file['subfiles']]
	else:
		files = [ file['name'] ]
	entities_clusters_map = {}
	for file_name in files:
		q = """
				select c.id, c.nome, e.id, e.caminho, e.tipo
				from clusters c 
					inner join grafos g on c.grafo = g.id 
					inner join clusters_entidades ce on c.id = ce.cluster 
					inner join entidades e on e.id = ce.entidade 
				where g.arquivo = %s
			"""
		clusters = db.query(q, (file_name,))
		for cluster_id, cluster_name, entity_id, entity_path, entity_type in clusters:
			if 'coarse_grained' in file_name:
				e = {'id': entity_id, 'path': entity_path, 'type': entity_type}
				add_cluster_to_map(simplified(entity_path), cluster_name, entities_clusters_map, e)				
				# for e in classes[entity_id]:
				# 	method_name = e['type'] + '_' + strip_args(e['path'].split('/').pop())
				# 	entity_full_name = "{}.{}".format(simplified(entity_path), method_name)
				# 	add_cluster_to_map(entity_full_name, cluster_name, entities_clusters_map, e)
			else:
				entity_full_name = "{}_{}".format(entity_type, simplified(entity_path))
				e = {'id': entity_id, 'path': entity_path, 'type': entity_type}
				add_cluster_to_map(entity_full_name, cluster_name, entities_clusters_map, e)
	return entities_clusters_map

def add_cluster_to_map(entity_full_name, cluster_name, entities_clusters_map, e):
	if entity_full_name not in entities_clusters_map:
		entities_clusters_map[entity_full_name] = [ cluster_name, e ]
	else:
		e_c = entities_clusters_map[entity_full_name]
		e_c[0] = cluster_name + '.' + e_c[0]

def write_xmls():
	for file in clusters_files():
		file_name = file['name']
		print(file['path'])
		e_c_m = entities_clusters_map(file)
		prefixes = constants.repository_prefixes[args.repository]['xml']
		# writes down the lattix xmls
		with open(file['path'].replace('.dot', '.ldi'), 'w') as xml:
			if file_name.endswith('.mdgL1.dot') or file_name.endswith('.mdgAllLevels.dot'):
				dependencies_file_name = file['path'].replace('.mdgL1.dot', '.dependencies.ldi')
				dependencies_file_name = dependencies_file_name.replace('.mdgAllLevels.dot', '.dependencies.ldi')
				xml_dep = open(dependencies_file_name, 'w')
			else:
				xml_dep = None
			xml.write("<?xml version=\"1.0\" ?>\n<ldi>\n")
			if xml_dep is not None: xml_dep.write("<?xml version=\"1.0\" ?>\n<ldi>\n")
			if 'coarse_grained' in file_name:
				func = coarse_grained_dependency_name
			else:
				func = lambda d : d[1] + '_' + d[0]
			for entity_full_name, item in e_c_m.items():
				cluster_name = item[0]
				e = item[1]
				if not util.has_prefix(to_java(e['path']), prefixes):
					continue
				xml_write_element(xml, "{}.{}".format(cluster_name, entity_full_name), 
					[ d[0] for d in entity_dependencies_with_cluster(e['id'], func, e_c_m) ])
				if xml_dep is not None: 
					if 'coarse_grained' in file_name:
						xml_write_element(xml_dep, strip_args(to_java(e['path'])), 
							[ d[2] for d in entity_dependencies_with_cluster(e['id'], func, e_c_m) if util.has_prefix(d[2], prefixes) ])
					else:
						xml_write_element(xml_dep, strip_args(to_java(e['path']) + '_' + e['type']), 
							[ d[2] + '_' + d[1] for d in entity_dependencies_with_cluster(e['id'], func, e_c_m) ])

			xml.write("</ldi>")
			if xml_dep is not None: 
				xml_dep.write("</ldi>")
				xml_dep.close()

def coarse_grained_dependency_name(d):
	if d[1] in ['CN','CM','FE','MT']:
		t = d[0].rpartition('_')
		return t[0] + '.' + d[1] + '_' + t[2]
	else:
		return d[0]

def to_java(entity_path):
	return simplifier.to_java_convention(entity_path, args.repository)

def simplified(entity_path):
	return to_java(entity_path).replace('.','_')

def entity_dependencies(id):
	if int(id) not in dependencies: return []
	return [ (d['path'], d['type']) for d in dependencies[int(id)] ]

def entity_dependencies_simplified(id):
	return [ (strip_args(simplified(d[0])), d[1], strip_args(to_java(d[0]))) for d in entity_dependencies(id)]

def entity_dependencies_with_cluster(id, func, entities_clusters_map):
	return [("{}.{}".format(entities_clusters_map[func(d)][0], func(d)), d[1], d[2]) 
				for d in entity_dependencies_simplified(id) if func(d) in entities_clusters_map]

def xml_write_element(xml, name, e_d):
	xml.write("    <element name=\"{}\">\n".format(name))
	for d in e_d:
		xml.write("        <uses provider=\"{}\"/>\n".format(d))
	xml.write("    </element>\n")

def strip_args(method_name):
	return method_name.replace('<', '_').replace('>', '_')

load_db_entities()
load_dependencies()
write_xmls()
db.close()