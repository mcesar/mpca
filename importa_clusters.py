#!/usr/bin/python

import os
import re
from db import Db
import constants
from glob import glob

files = [y for x in os.walk('.') for y in glob(os.path.join(x[0], '*.dot'))]

previous_graphs = {}

db = Db()

print "Excluindo clusters_entidades"
db.execute("delete from clusters_entidades")
print "Excluindo clusters"
db.execute("delete from clusters")
print "Excluindo grafos"
db.execute("delete from grafos")

print "Incluindo grafos"
for file in files:
	if re.search('\.dot$', file):
		arr = file.split('/')
		repository = constants.repository_map[arr[len(arr)-2]]
		file_name = arr[len(arr)-1]
		if not previous_graphs.get(file_name):
			graph_id = db.insert('insert into grafos(repositorio, arquivo) values (%s,%s)', 
				(repository,file_name))
	with open(file) as f:
		print file
		for line in f:
			match = re.search('subgraph (.+) {', line)   			
			if match:
				cluster_name = match.group(1)
				cluster_id = db.insert('insert into clusters(grafo, nome) values (%s,%s)', 
					(graph_id, cluster_name))
			match = re.search('\"(\d+)\"\[', line)
			if match:
				db.insert('insert into clusters_entidades(cluster, entidade) values (%s,%s)', 
					(cluster_id, match.group(1)))

db.commit()
db.close()
