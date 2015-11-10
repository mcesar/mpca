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
        result = db.execute("select * " + \
            "from mpca.grafos g " + \
            "    inner join mpca.clusters c on g.id = c.grafo " + \
            "    inner join mpca.clusters_entidades ce on ce.cluster = c.id " + \
            "    inner join mpca.entidades e on ce.entidade = e.id " + \
            "where g.arquivo = %s", (file_name,))
        with open(file + '.csv', 'w') as out:
            for (f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12) in result:
                out.write("{},{},{},{},{},{},{},{},{},{},{},{}\n".\
                    format(f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12))

db.close()
