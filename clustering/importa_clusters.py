#!/usr/bin/python

import os
import re
import argparse
from db import Db
import constants
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--repository", default="")
parser.add_argument("-f", "--file", default="")
args = parser.parse_args()

repository = None

if args.file == "":
    files = [y for x in os.walk('.') for y in glob(os.path.join(x[0], '*.dot'))]
    repository = constants.repository_map[args.repository] if args.repository != "" else None
else:
    files = [args.file]

previous_graphs = {}

db = Db()

# print "Excluindo clusters_entidades"
# db.execute("delete from clusters_entidades where entidade in " + \
        # "(select id from entidades where repositorio = %s)", (repository,))
# print "Excluindo clusters"
# db.execute("delete from clusters where grafo in " + \
        # "(select id from grafos where repositorio = %s)", (repository,))
# print "Excluindo grafos"
# db.execute("delete from grafos where repositorio = %s", (repository,))

print "Incluindo grafos"
for file in files:
    if re.search('\.dot$', file):
        file_name = file.rpartition('/')[2]
        file_repository = None
        for k in reversed(sorted(constants.repository_map.keys())):
            if file_name.startswith(k):
                file_repository = constants.repository_map[k]
                break
        if repository != None and file_repository != repository:
            continue
        db.execute("delete from clusters_entidades where cluster in " + \
            "(select id from clusters where grafo in " + \
                "(select id from grafos where arquivo = %s))", (file_name,))
        db.execute("delete from clusters where grafo in " + \
            "(select id from grafos where arquivo = %s)", (file_name,))
        db.execute("delete from grafos where arquivo = %s", (file_name,))
        graph_id = db.insert('insert into grafos(repositorio, arquivo) values (%s,%s)', 
                        (file_repository,file_name))
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
