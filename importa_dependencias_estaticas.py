#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree
from db import Db
import constants

repository_prefixes = { 
	'siop': '', 
	'derby': '', 
	'hadoop': '', 
	'wildfly': '', 
	'eclipse.platform.ui': '', 
	'eclipse.jdt': '', 
	'geronimo': '', 
	'lucene': '', 
	'jhotdraw7': {'xml':'org.jhotdraw','db':'src/main/java/org/jhotdraw'} }

def load_entities_from_db():
	db = Db()
	repository_id = constants.repository_map[args.repository]
	prefix = repository_prefixes[args.repository]['db']
	db_entities = {}
	cursor = db.query(
		"select id, caminho from entidades where repositorio = %s and caminho like %s", 
		(repository_id, prefix + '%'))
	for (id, path) in cursor:
		key = simplified(path, args.repository)
		if not key in db_entities: db_entities[key] = {'id': id, 'path': path}
	db.close()
	return db_entities

def simplified(path, repository):
	prefix_db = repository_prefixes[repository]['db'].replace('/', '.')
	prefix_xml = repository_prefixes[repository]['xml']
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
		new_s = s.replace('.c', '')
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
		new_arr.append(new_s)
	return '.'.join(new_arr).replace(prefix_db, prefix_xml).replace('.$.','$')

def parse_xml():
	root = etree.parse(args.file).getroot()
	prefix = repository_prefixes[args.repository]['xml']
	classes = []
	for e1 in root:
		for e2 in e1:
			if e2.tag == 'name':
				package_name = e2.text
				if package_name is None: package_name = ''
			if e2.tag == 'class' and package_name.startswith(prefix):
				for e3 in e2:
					if e3.tag == 'name':
						class_dict = {'name': e3.text, 'entities': []}
						classes.append(class_dict)
					if e3.tag == 'feature':
						for e4 in e3:
							if e4.tag == 'name':
								feature_name = simplified_args(e4.text)
								feature_dict = {'name': feature_name, 'dependencies': []}
								class_dict['entities'].append(feature_dict)
								if feature_name.endswith(')'):
									if simple_name(feature_name) == simple_name(class_dict['name']):
										feature_type = 'CN'
									else:
										feature_type = 'MT'
								else:
									feature_type = 'FE'
								feature_dict['type'] = feature_type
							if e4.tag == 'outbound' and e4.text.startswith(prefix) and feature_type in ('MT','CN'):
								dependency_name = simplified_args(e4.text)
								#if class_top_level_name(feature_name) != class_top_level_name(dependency_name):
								feature_dict['dependencies'].append(dependency_name)
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
		new_args.append(simple_name(arg))
	return feature_name.replace('('+args_str+')','(' + ','.join(new_args) + ')')

def simple_name(qualified_name):
	result = qualified_name
	if result.find('(') != -1:
		result = result[:result.find('(')]
	result = result[result.rfind('.')+1:]
	return result.strip()

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	parser.add_argument("-r", "--repository")
	args = parser.parse_args()

	db_entities = load_entities_from_db()
	classes = parse_xml()

	prefix_db = repository_prefixes[args.repository]['db']
	prefix_xml = repository_prefixes[args.repository]['xml']

	db = Db()

	db.delete("""
		delete from dependencias 
		where entidade1 in (select id from entidades where repositorio=%s)""",
		(constants.repository_map[args.repository],))

	for c in classes:
		for e in c['entities']:
			if e['name'] in db_entities:
				for d in e['dependencies']:
					if d in db_entities:
						#print(db_entities[e['name']]['id'], db_entities[d]['id'])
						db.insert('insert into dependencias values (%s,%s)', 
							(db_entities[e['name']]['id'], db_entities[d]['id']))
					#else:
					#	print(d)
			else:
				print(e['name'])

	db.commit()
	db.close()
