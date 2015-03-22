#!/usr/local/bin/python3

import sys
import tokenize
import plyj.parser as plyj

parser = plyj.Parser()

tree = parser.parse_file(sys.stdin)

print(tree)
