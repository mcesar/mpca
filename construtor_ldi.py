#!/usr/local/bin/python3

import argparse
import os
from glob import glob
from db import Db
import constants
import dependencias_estaticas as simplifier

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--repository")
args = parser.parse_args()

files = [y for x in os.walk('.') for y in glob(os.path.join(x[0], '*.graphL*.dot'))]
db = Db()

classes = {}
dependencies = {}
entities_clusters_map = {}

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
	print('Carregando dependências...')
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

def write_xmls():
	for file in files:
		file_name = file.split('/').pop()
		if ('fine_grained' in file or 'coarse_grained' in file) and file_name.startswith(args.repository):
			print(file_name)
			q = """
					select c.id, c.nome, e.id, e.caminho, e.tipo
					from clusters c 
						inner join grafos g on c.grafo = g.id 
						inner join clusters_entidades ce on c.id = ce.cluster 
						inner join entidades e on e.id = ce.entidade 
					where g.arquivo = %s
				"""			
			clusters = db.query(q, (file_name,))
			# fills the entities x clusters mapping to further reference
			entities_clusters_map.clear()
			for cluster_id, cluster_name, entity_id, entity_path, entity_type in clusters:
				if 'coarse_grained' in file:
					for d in classes[entity_id]:
						method_name = d['type'] + '_' + strip_args(d['path'].split('/').pop())
						entity_full_name = "{}.{}".format(simplified(entity_path), method_name)
						entities_clusters_map[entity_full_name] = cluster_name
				else:
					entity_full_name = entity_type + '_' + simplified(entity_path)
					entities_clusters_map[entity_full_name] = cluster_name
			# writes down the lattix xmls
			clusters = db.query(q, (file_name,))
			with open(file.replace('.dot', '.ldi'), 'w') as xml:
				if file.endswith('.graphL1.dot'):
					xml_dep = open(file.replace('.graphL1.dot', '.dependencies.ldi'), 'w')
				else:
					xml_dep = None
				xml.write("<?xml version=\"1.0\" ?>\n<ldi>\n")
				if xml_dep is not None: xml_dep.write("<?xml version=\"1.0\" ?>\n<ldi>\n")
				for cluster_id, cluster_name, entity_id, entity_path, entity_type in clusters:
					if 'coarse_grained' in file:
						for d in classes[entity_id]:
							method_name = d['type'] + '_' + strip_args(d['path'].split('/').pop())
							entity_full_name = "{}.{}".format(simplified(entity_path), method_name)
							xml_write_element(xml, "{}.{}".format(cluster_name, entity_full_name), 
								[ d[0] for d in entity_dependencies_with_cluster(d['id'], coarse_grained_dependency_name) ])
							if xml_dep is not None: 
								xml_write_element(xml_dep, strip_args(to_java(d['path']) + '_' + d['type']), 
									[ d[2] + '_' + d[1] for d in entity_dependencies_with_cluster(d['id'], coarse_grained_dependency_name) ])
					else:
						entity_full_name = entity_type + '_' + strip_args(simplified(entity_path))
						xml_write_element(xml, "{}.{}".format(cluster_name, entity_full_name), 
							[ d[0] for d in entity_dependencies_with_cluster(entity_id, lambda d : d[1] + '_' + d[0]) ])
						if xml_dep is not None:
							xml_write_element(xml_dep, strip_args(to_java(entity_path)) + '_' + entity_type, 
								[ d[2] + '_' + d[1] for d in entity_dependencies_with_cluster(entity_id, lambda d : d[1] + '_' + d[0]) ])
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

def entity_dependencies_with_cluster(id, func):
	return [("{}.{}".format(entities_clusters_map[func(d)], func(d)), d[1], d[2]) 
				for d in entity_dependencies_simplified(id) if func(d) in entities_clusters_map]

def xml_write_element(xml, name, e_d):
	xml.write("    <element name=\"{}\">\n".format(name))
	for d in e_d:
		xml.write("        <uses provider=\"{}\"/>\n".format(d))
	xml.write("    </element>\n")

def strip_args(method_name):
	# if '(' in method_name: 
	# 	return method_name[:method_name.find('(')]
	return method_name.replace('<', '_').replace('>', '_')

load_db_entities()
load_dependencies()
write_xmls()
db.close()