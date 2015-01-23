#!/usr/local/bin/python3

import constants
from db import Db

repos = {}
granularities = ('fine_grained', 'coarse_grained')

db = Db()

cursor = db.execute("select id, arquivo from grafos")

for (id, a) in cursor:
	arr = a.split('.')
	repo = arr[0]
	if repo == 'eclipse':
		repo += '.' + arr[1]
	if repo == 'eclipse.platform':
		repo += '.' + arr[2]
	granularity = arr[len(arr)-3]
	level = arr[len(arr)-2]
	if granularity in granularities and level.startswith('graphL'):
		if not repo in repos:
			repos[repo] = {}
		if not granularity in repos[repo]:
			repos[repo][granularity] = []
		repos[repo][granularity].append({'id': id, 'level': int(level.replace('graphL',''))})

for repo in repos.values():
	for granularity in granularities:
		graphs = sorted(repo[granularity], key=lambda g : g['level'])
		for i in range(1,len(graphs)):
			cursor.execute("select id from clusters where grafo = %s", (graphs[i-1]['id'],))
			clusters = cursor.fetchall()
			print(graphs[i-1]['id'], len(clusters))
			for (cluster_id,) in clusters:
				cursor2 = db.execute("""
						select count(distinct c.id)
						from clusters c inner join clusters_entidades ce on c.id = ce.cluster
						where c.grafo = %s
							and ce.entidade in (select entidade from clusters_entidades where cluster = %s)
					""", 
					(graphs[i]['id'], cluster_id))
				count = cursor2.fetchone()[0]
				if count != 1:
					print('oops', graphs[i],count)

db.close()