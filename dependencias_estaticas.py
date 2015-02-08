#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree
from db import Db
import constants
import re

def load_entities_from_db():
	db = Db()
	repository_id = constants.repository_map[args.repository]
	prefixes = constants.repository_prefixes[args.repository]['db']
	db_entities = {}
	sql_args = (repository_id,)
	prefixes_str = ''
	for prefix in prefixes:
		sql_args += (prefix + '%',)
		if len(prefixes_str) > 0: prefixes_str += ' or '
		prefixes_str += 'caminho like %s'
	cursor = db.query(
		"select id, caminho from entidades where repositorio = %s and (" + prefixes_str + ")", sql_args)
	for (id, path) in cursor:
		key = to_java_convention(path, args.repository, True)
		if not key in db_entities: db_entities[key] = {'id': id, 'path': path}
	db.close()
	return db_entities

def load_evolutionary_dependencies_from_db():
	db = Db()
	repository_id = constants.repository_map[args.repository]
	types = 'CN,CM,FE,MT'
	if args.coarse_grained:
		types = 'CL,IN'
	graphs_ed = {}
	cursor = db.query("""select g.id, g.source, g.max_entities, g.min_confidence, 
			g.min_support, g.min_date, g.types, de.entidade1, de.entidade2, e.caminho
		from dependencias_evolucionarias de 
			inner join grafos_de g on de.grafo = g.id 
			inner join entidades e on de.entidade2 = e.id 
		where g.repositorio = %s and g.types = %s""", 
		(repository_id,types))
	for (id, source, max_entitites, min_confidence, min_support, min_date, types, entity1, entity2, e2_path) in cursor:
		if id not in graphs_ed:
			graphs_ed[id] = {
				'source': source, 
				'max_entitites': max_entitites, 
				'min_confidence': min_confidence, 
				'min_support': min_support, 
				'min_date': min_date, 
				'types': types,
				'dependencies': {}
			}
		if entity1 not in graphs_ed[id]['dependencies']:
			graphs_ed[id]['dependencies'][entity1] = []
		entity2_java_name = to_java_convention(e2_path, args.repository, True)
		graphs_ed[id]['dependencies'][entity1].append(entity2_java_name)
	db.close()
	return graphs_ed

def to_java_convention(path, repository, strip_generics=False):
	arr = path.split('/')
	new_arr = []
	class_count = 0
	for s in arr:
		if s.endswith('.f'):
			continue
		if s == 'CL':
			class_count += 1
			if class_count > 1:
				s = '$'
		if s in constants.entity_types:
			continue
		new_s = re.sub('\.c$', '', s)
		# remove generic types
		if strip_generics:
			while '<' in new_s:
				i = new_s.find('<')
				count = 0
				for j in range(i, len(new_s)):
					if new_s[j] == '>':
						count -= 1
					if new_s[j] == '<':
						count += 1
					if count == 0:
						break
				new_s = new_s.replace(new_s[i:j+1], '')
		# change signature of inner classe's constructors
		if '(' in new_s and class_count > 1 and new_s.partition('(')[0] == new_arr[len(new_arr)-1]:
			outer_class = new_arr[len(new_arr)-3]
			new_s = outer_class + '$' + new_s
			if '()' in new_s:
				new_s = new_s.replace('(', '(' + outer_class)
			#else:
			#	new_s = new_s.replace('(', '(' + outer_class + ',')
		new_arr.append(new_s)
	result = '.'.join(new_arr).replace('.$.','$')
	for i in range(0, len(constants.repository_prefixes[repository]['db'])):
		prefix_db = constants.repository_prefixes[repository]['db'][i].replace('/', '.')
		prefix_xml = constants.repository_prefixes[repository]['xml'][i]
		result = result.replace(prefix_db, prefix_xml)
	return result

def parse_xml():
	"""Parse XML from DependencyFinder"""
	root = etree.parse(args.file).getroot()
	prefixes = constants.repository_prefixes[args.repository]['xml']
	classes = {}
	for e1 in root:
		for e2 in e1:
			if e2.tag == 'name':
				package_name = e2.text
				if package_name is None: package_name = ''
			has_prefix = [prefix for prefix in prefixes if package_name.startswith(prefix)]
			if e2.tag == 'class' and has_prefix and e2.attrib['confirmed'] == 'yes':
				is_enum = False
				for e3 in e2:
					if e3.tag == 'name':
						class_dict = {'name': e3.text, 'entities': [], 'superclasses': [], 'dependencies': set()}
						classes[e3.text] = class_dict
					if e3.tag == 'outbound' and e3.attrib['type'] == 'class' and e3.attrib['confirmed'] == 'no' and e3.text == 'java.lang.Enum':
						is_enum = True
					elif e3.tag == 'outbound' and e3.attrib['type'] == 'class' and e3.attrib['confirmed'] == 'yes':
						class_dict['superclasses'].append(e3.text)
					if e3.tag == 'feature' and e3.attrib['confirmed'] == 'yes':
						for e4 in e3:
							if e4.tag == 'name':
								feature_name = simplified_args(e4.text)
								# ignores static initializers
								if simple_name(feature_name) == 'static {}':
									break
								# ignores enum features not supported by historage
								if is_enum and simple_name(feature_name) in ['$VALUES', 'valueOf', 'values']:
									break
								# find out the feature type
								if feature_name.endswith(')'):
									if simple_name(feature_name) == simple_name(class_dict['name']):
										feature_type = 'CN'
									else:
										feature_type = 'MT'
								else:
									feature_type = 'FE'
								# ignores enums constructors
								if is_enum and feature_type == 'CN' and feature_name.endswith(simple_name(feature_name) + '(String,int)'):
									break
								feature_dict = {'name': feature_name, 'dependencies': []}
								class_dict['entities'].append(feature_dict)
								feature_dict['type'] = feature_type
							has_prefix = [prefix for prefix in prefixes if e4.text.startswith(prefix)]
							if e4.tag == 'outbound' and has_prefix and e4.attrib['type'] == 'feature':
								#e4.attrib['confirmed'] == 'yes' and
								dependency_name = simplified_args(e4.text)
								#if class_top_level_name(feature_name) != class_top_level_name(dependency_name):
								feature_dict['dependencies'].append(dependency_name)
								if class_dict['name'] != class_name(dependency_name):
									class_dict['dependencies'].add(class_name(dependency_name))
	return classes

def class_name(feature_name):
	result = feature_name
	if result.find('(') != -1:
		result = result[:result.find('(')]
	result = result[:result.rfind('.')]
	return result

def class_top_level_name(feature_name):
	result = class_name(feature_name)
	if result.find('$') != -1:
		result = result[:result.find('$')]
	return result

def simplified_args(feature_name):
	if not '(' in feature_name: return feature_name
	args_str = feature_name[feature_name.find('(')+1:len(feature_name)-1]
	args = args_str.split(',')
	new_args = []
	for arg in args:
		simple_arg = simple_name(arg)
		simple_arg = simple_arg.rpartition('$')[2]
		new_args.append(simple_arg)
	return feature_name.replace('('+args_str+')','(' + ','.join(new_args) + ')')

def simple_name(qualified_name):
	result = qualified_name
	if result.find('(') != -1:
		result = result[:result.find('(')]
	result = result[result.rfind('.')+1:]
	return result.strip()

def is_default_constructor(feature_name):
	class_name = simple_name(feature_name.rpartition('.')[0])
	if simple_name(feature_name) != class_name:
		return False
	if feature_name.endswith('()'):
		return True
	if '$' in class_name:
		return feature_name.endswith("({})".format(class_name.partition('$')[0]))	

def find_id_in_class_or_superclasses(feature_name, classes, db_entities, e):
	#cn = class_name(feature_name)
	#superclasses = classes[cn]['superclasses']
	if feature_name not in db_entities:
		# anonymous_inner_class = re.search('\$\d+\.', feature_name)
		# compiler_generated_element = re.search('access\$\d+\(', feature_name) or re.search('\.this\$\d+', feature_name)
		# default_constructor = is_default_constructor(feature_name)
		# # prints feature names not found in db
		# if anonymous_inner_class and not compiler_generated_element and not default_constructor:
		# 	print(feature_name)
		return None
	return db_entities[feature_name]['id']

def import_static_dependencies(db_entities, classes, coarse_grained):
	db = Db()

	table_suffix = ""
	if coarse_grained:
		table_suffix = "_coarse_grained"

	if not args.dont_store:
		db.delete("""
			delete from dependencias{} 
			where entidade1 in (select id from entidades where repositorio=%s)""".format(table_suffix),
			(constants.repository_map[args.repository],))

	dep_map = {}

	for c in classes.values():
		if coarse_grained:
			if c['name'] in db_entities:
				caller_id = db_entities[c['name']]['id']
				for d in c['dependencies']:
					if d in db_entities and not args.dont_store:
						calle_id = db_entities[d]['id']
						db.insert('insert into dependencias_coarse_grained values (%s,%s)', (caller_id, calle_id))
				if args.verbose and not args.not_found:
					print(c['name'])
			else:
				anonymous_inner_class = re.search('\$\d+$', c['name'])
				if args.verbose and args.not_found and not anonymous_inner_class:
					print(c['name'])
		else:
			for e in c['entities']:
				if e['name'] in db_entities:
					caller_id = db_entities[e['name']]['id']
					for d in e['dependencies']:
						calle_id = find_id_in_class_or_superclasses(d, classes, db_entities, e)
						if calle_id:
							#print(db_entities[e['name']]['id'], db_entities[d]['id'])
							if not args.dont_store and '{}-{}'.format(caller_id, calle_id) not in dep_map:
								db.insert('insert into dependencias values (%s,%s)', (caller_id, calle_id))
								dep_map['{}-{}'.format(caller_id, calle_id)] = True
						#else:
						#	if args.verbose: print(d)
					if args.verbose and not args.not_found:
						print(e['name'])
				else:
					# ignore entities not supported by historage
					anonymous_inner_class = re.search('\$\d+\.', e['name'])
					compiler_generated_element = re.search('access\$\d+\(', e['name']) or re.search('\.this\$\d+', e['name'])
					default_constructor = is_default_constructor(e['name'])
					# prints feature names not found in db
					if args.verbose and args.not_found and not anonymous_inner_class and not compiler_generated_element and not default_constructor:
					 	print(e['name'])

	db.commit()
	db.close()

def export_evolutionary_dependencies(db_entities, classes, e_graphs, repository):
	for g in e_graphs.values():
		if g['types'] == 'CL,IN':
			grain = 'coarse_grained'
		else:
			grain = 'fine_grained'
		file_name = 'mixed-dependencies_{}_{}_n{}_c{}_s{}_d{}_{}.ldi'.format(repository,g['source'],g['max_entitites'],str(g['min_confidence']).replace('.','_'),g['min_support'],g['min_date'],grain)
		prefixes = constants.repository_prefixes[args.repository]['xml']
		with open(file_name, 'w') as f:
			print(file_name)
			f.write('<?xml version=\"1.0\" ?>\n<ldi>\n')
			class_count = 0
			for c in classes.values():
				has_prefix = [prefix for prefix in prefixes if c['name'].startswith(prefix)]
				if not has_prefix:
					continue
				class_count += 1
				if grain == 'coarse_grained':
					f.write("    <element name=\"{}\">\n".format(c['name']))
					added_dependencies = set()
					for d in c['dependencies']:
						has_prefix = [prefix for prefix in prefixes if d.startswith(prefix)]
						if not has_prefix or d in added_dependencies:
							continue
						f.write("        <uses provider=\"{}\" kind=\"static\"/>\n".format(d))
						added_dependencies.add(d)
					if c['name'] in db_entities:
						entity_id = db_entities[c['name']]['id']
						write_evol_deps_of_entity(f, entity_id, g)
					f.write("    </element>\n")
				else:
					for e in c['entities']:
						f.write("    <element name=\"{}\">\n".format(e['name']))
						for d in e['dependencies']:
							f.write("        <uses provider=\"{}\" kind=\"static\"/>\n".format(d))
						if e['name'] in db_entities:
							entity_id = db_entities[e['name']]['id']
							write_evol_deps_of_entity(f, entity_id, g)
						f.write("    </element>\n")
			f.write('</ldi>')
			print(class_count)

def write_evol_deps_of_entity(f, entity_id, g):
	prefixes = constants.repository_prefixes[args.repository]['xml']
	if entity_id in g['dependencies']:
		evol_deps = g['dependencies'][entity_id]
		for e_d in evol_deps:
			has_prefix = [prefix for prefix in prefixes if e_d.startswith(prefix)]
			if not has_prefix:
				continue
			f.write("        <uses provider=\"{}\" kind=\"evolutionary\"/>\n".format(e_d))

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	parser.add_argument("-r", "--repository")
	parser.add_argument("-d", "--dont_store", action="store_true", default=False)
	parser.add_argument("-v", "--verbose", action="store_true")
	parser.add_argument("-n", "--not_found", action="store_true")
	parser.add_argument("-e", "--evolutionary_dependencies", action="store_true", default=False)
	parser.add_argument("-c", "--coarse_grained", action="store_true", default=False)
	args = parser.parse_args()

	db_entities = load_entities_from_db()
	classes = parse_xml()

	if args.evolutionary_dependencies:
		e_graphs = load_evolutionary_dependencies_from_db()
		export_evolutionary_dependencies(db_entities, classes, e_graphs, args.repository)
	else:
		import_static_dependencies(db_entities, classes, args.coarse_grained)

	# print('org.apache.lucene.codecs.asserting.AssertingDocValuesFormat$AssertingDocValuesConsumer.in')
	# print(to_java_convention('lucene/test-framework/src/java/org/apache/lucene/analysis/CannedBinaryTokenStream.f/CL/CannedBinaryTokenStream.c/CL/BinaryTermAttributeImpl.c/FE/bytes', args.repository))