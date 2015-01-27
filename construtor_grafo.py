#!/usr/local/bin/python3

import argparse
import constants
from db import Db

def in_str(arr):
	s = ""
	t = ()
	for e in arr:
		if len(s) > 0: s += ","
		s += "%s"
		t += (e,)
	return (s, t)

def increment_support(graph, entities, max_entities):
	if len(entities) > max_entities: return
	for e1 in entities:
		if e1 not in graph:
			graph[e1] = {}
		for e2 in entities:
			if e2 not in graph[e1]:
				graph[e1][e2] = [0, 0]
			graph[e1][e2][0] += 1

def calculate_confidence(graph):
	for e1 in graph.keys():
		max_support = graph[e1][e1][0]
		for e2 in graph[e1].keys():
			graph[e1][e2][1] = graph[e1][e2][0]/max_support

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-r", "--repository", default="siop")
	parser.add_argument("-s", "--source", default="commits")
	parser.add_argument("-m", "--max_entities", type=int, default=100)
	parser.add_argument("-c", "--min_confidence", type=float, default=0)
	parser.add_argument("-p", "--min_support", type=float, default=0)
	parser.add_argument("-d", "--min_date", default="1900-01-01")
	parser.add_argument("-t", "--types", default="CL,CN,CM,FE,IN,MT")
	parser.add_argument("-b", "--store_on_db", action="store_true", default=False)
	args = parser.parse_args()

	sql = { 
		'commits': """
			select commit as id, entidade 
			from commits_entidades ce 
				inner join entidades e on ce.entidade = e.id 
				inner join commits c on ce.commit = c.id
			where c.repositorio = %s 
				and c.data >= %s
				and e.tipo in (?in?) 
			order by commit,entidade""",
		'issues': """
			select distinct issue as id, entidade, ce.commit
			from commits_entidades ce 
				inner join commits_issues ci on ci.commit = ce.commit 
				inner join entidades e on ce.entidade = e.id 
			where ce.commit in 
				(select id from commits where repositorio = %s and data >= %s) 
				and e.tipo in (?in?) 
			order by issue,entidade""", 
		'issues_only': """
			select distinct issue as id, entidade 
			from commits_entidades ce 
				inner join commits_issues ci on ci.commit = ce.commit 
				inner join entidades e on ce.entidade = e.id 
			where ce.commit in 
				(select id from commits where repositorio = %s and data >= %s) 
				and e.tipo in (?in?) 
			order by issue,entidade""" }

	(s, types) = in_str(args.types.split(','))

	db = Db()

	repository_id = constants.repository_map[args.repository]

	graph = {}
	entities = []
	previous_id = None

	if args.store_on_db:
		graphs = db.query("""select id 
			from grafos_de 
			where repositorio=%s 
				and source=%s 
				and max_entities=%s 
				and min_confidence=%s 
				and min_support=%s 
				and min_date=%s 
				and types=%s""",
				(repository_id,args.source,args.max_entities,args.min_confidence,args.min_support,args.min_date,args.types), cursor=False)
		if len(graphs) == 0:
			graph_id = db.insert("insert into grafos_de(repositorio,source,max_entities,min_confidence,min_support,min_date,types) values (%s,%s,%s,%s,%s,%s,%s)",
				(repository_id,args.source,args.max_entities,args.min_confidence,args.min_support,args.min_date,args.types))
		else:
			graph_id = graphs[0][0]
			db.delete("delete from dependencias_evolucionarias where grafo = %s", (graph_id,))

	cursor = db.query(sql[args.source].replace('?in?', s), (repository_id, args.min_date) + types)

	for (id, entity) in cursor:
		if previous_id != id:
			increment_support(graph, entities, args.max_entities)
			previous_id = id
			entities.clear()
		entities.append(entity)
	increment_support(graph, entities, args.max_entities)
	calculate_confidence(graph)

	for e1 in graph.keys():
		for e2 in graph[e1].keys():
			if e1 != e2 and graph[e1][e2][0] >= args.min_support and graph[e1][e2][1] >= args.min_confidence:
				if args.store_on_db:
					db.insert("insert into dependencias_evolucionarias(grafo,entidade1,entidade2,suporte,confianca) values (%s,%s,%s,%s,%s)",
						(graph_id, e1, e2, graph[e1][e2][0], graph[e1][e2][1]))
				else:
					print(e1, e2, graph[e1][e2][0])

	db.commit()
	db.close()
