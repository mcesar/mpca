#!/usr/local/bin/python3

import math
import argparse
import reduce_level

# NOV
# ---

# # Sum of nov of modules (modules are packages and clusters)

# Q = []
# n(i): size(i)/N
# Z(i): sum of n(j), where module j depends on module i
# nov(i, k): 2.5 * sqrt(n(i)) * Q[k] - n(i) * k - Z(i) 

# nov(1,0) = 2,5 * sqrt(0,225) * 0 - 0,225 * 0 - 0,575

Q = [0.000000,0.398942,0.681037,0.888147,1.045756,1.169705,1.270073,1.353426,1.424153,1.485261,1.538865]

MAX_K = 10

class DSM(object):
	"""docstring for DSM"""
	def __init__(self, matrix, sizes):
		super(DSM, self).__init__()
		self.matrix = matrix
		self.sizes = sizes
		self.size = sum([sizes[i] for i in range(0, len(matrix))])
	def NOV(self):
		return sum([self.nov(i) for i in range(0, len(self.matrix))])
	def nov(self, i):
		n_i = self.n(i)
		Z_i = self.Z(i)
		return max([self.nov_k(k, n_i, Z_i) for k in range(0, MAX_K)]+[0])
	def nov_k(self, k, n_i, Z):
		return 2.5 * math.sqrt(n_i) * Q[k] - n_i * k - Z
	def n(self, i):
		return self.sizes[i] / float(self.size)
	def Z(self, i):
		result = 0
		for j in range(0, len(self.matrix)):
			if i != j and self.matrix[j][i] == 1:
				result += self.n(j)
		return result

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file", default='')
	parser.add_argument("-p", "--print_matrix", action="store_true", default=False)
	args = parser.parse_args()
	(elements, sizes) = reduce_level.reduce(args.file)
	names = sorted(elements)
	matrix = []
	sizes_arr = []
	for k_i in range(0,len(names)):
		matrix.append([])
		sizes_arr.append(sizes[names[k_i]])
		for k_j in range(0,len(names)):
			if names[k_j] + '|static' in elements[names[k_i]] or names[k_j] + '|evolutionary' in elements[names[k_i]]:
				d_ij = 1
			else:
				d_ij = 0
			matrix[k_i].append(d_ij)
	if args.print_matrix:
		print(names, elements, matrix, sizes_arr)
	else:
		print(DSM(matrix, sizes_arr).NOV())


if __name__ == '__main__':
	main()