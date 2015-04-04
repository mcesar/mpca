import os
from glob import glob

def find(dir, pattern):
	return [y for x in os.walk(dir) for y in glob(os.path.join(x[0], pattern))]
