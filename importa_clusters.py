#!/usr/bin/python

import mysql.connector    
import os
import re
from glob import glob

repositorioMap = { 'siop': 1, 'derby': 2, 'hadoop': 3, 'wildfly': 4, 'eclipse.platform.ui': 5, 'eclipse.jdt': 6, 'geronimo': 7, 'lucene': 8, 'jhotdraw7': 9 }

files = [y for x in os.walk('.') for y in glob(os.path.join(x[0], '*.dot'))]

previous_graphs = {}

cnx = mysql.connector.connect(user='root', password='', host='localhost', database='mpca')

try:
   cursor = cnx.cursor()

   print "Excluindo clusters_entidades"
   cursor.execute("delete from clusters_entidades")
   print "Excluindo clusters"
   cursor.execute("delete from clusters")
   print "Excluindo grafos"
   cursor.execute("delete from grafos")

   print "Incluindo grafos"
   for file in files:
   	if re.search('\.dot$', file):
   		arr = file.split('/')
   		repository = repositorioMap[arr[len(arr)-2]]
   		file_name = arr[len(arr)-1]
   		if not previous_graphs.get(file_name):
   			cursor.execute('insert into grafos(repositorio, arquivo) values (%s,%s)', 
   				(repository,file_name))
   			graph_id = cursor.lastrowid
			with open(file) as f:
				print file
				for line in f:
					match = re.search('subgraph (.+) {', line)   			
   					if match:
   						cluster_name = match.group(1)
   						cursor.execute('insert into clusters(grafo, nome) values (%s,%s)', 
   							(graph_id, cluster_name))
   						cluster_id = cursor.lastrowid
					match = re.search('\"(\d+)\"\[', line)
   					if match:
   						cursor.execute('insert into clusters_entidades(cluster, entidade) values (%s,%s)', 
   							(cluster_id, match.group(1)))

   cnx.commit()
   cursor.close()
finally:
    cnx.close()