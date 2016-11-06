import os,sys,argparse
import json

import pycommons
from cpuprof import plot

from pycommons.file_entry import FileEntry
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans, DBSCAN
import numpy as np

def setup_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('path')
	return parser

def __process(tempo, energy, path):
	with pycommons.open_file(path, 'rb') as f:
		data = json.loads(f.read())
	t = data['tempo']
	e = data['energy']
	tempo.append(t)
	energy.append(e)
	return [t, e]

def kmeans(ax, X):
	max_bpm = max([x[0] for x in X])
	for e in X:
		e[0] = e[0] / max_bpm

	n_clusters = 5
	km = KMeans(n_clusters=n_clusters, init='random', n_init=10)
	y_km = km.fit_predict(X)

	for i in range(n_clusters):
		plt.scatter(X[y_km == i,0], X[y_km==i,1],s=50, c=plot.kelly_colors_hex[i], marker=plot.markers[i], label='Cluster {}'.format(i+1))
	plt.scatter(km.cluster_centers_[:,0], km.cluster_centers_[:,1], s=250, marker='*', c='k', label='Centroids')

	ax.set_xlabel('\\textbf{Beats Per Minute}')
	ax.set_ylabel('\\textbf{Energy}')
	plt.legend()
	plt.show()

def dbscan(ax, X):
	max_bpm = max([x[0] for x in X])
	for e in X:
		e[0] = e[0] / max_bpm

	db = DBSCAN(eps=0.05, min_samples=5, metric='euclidean')
	y_db = db.fit_predict(X)
	import ipdb; ipdb.set_trace()
	print ''

	
def process(path):
	entry = FileEntry(path, None)

	entry.build(regex='*.features.gz')

	fig = plot.new_fig()
	ax = fig.add_subplot(111)

	tempo = []
	energy = []
	features = []
	for file in entry.get_files():
		feature = __process(tempo, energy, file.path())
		features.append(feature)

	X = np.array(features)
	kmeans(ax, X)
	#dbscan(ax, X)

def main(argv):
	parser = setup_parser()
	args = parser.parse_args(argv[1:])

	process(args.path)


if __name__ == '__main__':
	main(sys.argv)
