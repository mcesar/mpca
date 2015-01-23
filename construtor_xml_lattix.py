#!/usr/local/bin/python3

import argparse
import os
from glob import glob
from db import Db
import constants
import importa_dependencias_estaticas as simplifier

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
			classes[class_id].append({'id': id, 'path': path})

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
			entities_clusters_map.clear()
			q = """
					select c.id, c.nome, e.id, e.caminho
					from clusters c 
						inner join grafos g on c.grafo = g.id 
						inner join clusters_entidades ce on c.id = ce.cluster 
						inner join entidades e on e.id = ce.entidade 
					where g.arquivo = %s
				"""			
			clusters = db.query(q, (file_name,))
			for cluster_id, cluster_name, entity_id, entity_path in clusters:
				if 'coarse_grained' in file:
					for d in classes[entity_id]:
						method_name = strip_args(d['path'].split('/').pop())
						entity_full_name = "{}.{}".format(simplified(entity_path), method_name)
						entities_clusters_map[entity_full_name] = cluster_name
				else:
					entity_full_name = simplified(entity_path)
					entities_clusters_map[entity_full_name] = cluster_name
			clusters = db.query(q, (file_name,))
			with open(file.replace('.dot', '.xml'), 'w') as xml:
				xml.write("<?xml version=\"1.0\" ?>\n<ldi>\n")
				for cluster_id, cluster_name, entity_id, entity_path in clusters:
					if 'coarse_grained' in file:
						for d in classes[entity_id]:
							method_name = strip_args(d['path'].split('/').pop())
							entity_full_name = "{}.{}".format(simplified(entity_path), method_name)
							xml_write_element(xml, "{}.{}".format(cluster_name, entity_full_name), 
								entity_dependencies(d['id']), True)
					else:
						entity_full_name = strip_args(simplified(entity_path))
						xml_write_element(xml, "{}.{}".format(cluster_name, entity_full_name), 
							entity_dependencies(entity_id), False)
				xml.write("</ldi>")
				xml.close()

def simplified(entity_path):
	return simplifier.simplified(entity_path, args.repository).replace('.','_')

def entity_dependencies(id):
	result = []
	if int(id) in dependencies:
		result = dependencies[int(id)]
	return result

def xml_write_element(xml, name, e_d, coarse_grained):
	xml.write("    <element name=\"{}\">\n".format(name))
	for d in e_d:
		p = strip_args(simplifier.simplified(d['path'], args.repository).replace('.','_'))
		if coarse_grained and d['type'] in ['CN','CM','FE','MT']:
			t = p.rpartition('_')
			p = t[0] + '.' + t[2]
		if p in entities_clusters_map:
			xml.write("        <uses provider=\"{}.{}\"/>\n".format(entities_clusters_map[p], p))
		#else:
		#	xml.write("        <uses provider=\"{}.{}\"/>\n".format('', p))
	xml.write("    </element>\n")

def strip_args(method_name):
	if '(' in method_name: 
		return method_name[:method_name.find('(')]
	return method_name

load_db_entities()
load_dependencies()
write_xmls()
db.close()
print(dependencies)