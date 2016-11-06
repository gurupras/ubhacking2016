from aubio import source, tempo
import numpy as np
import common
import sys
import argparse
import json
import pycommons

def get_file_all_bpm(path, params = None):
	""" Calculate the beats per minute (bpm) of a given file.
		path: path to the file
		param: dictionary of parameters
	"""
	if params is None:
		params = {}
	try:
		win_s = params['win_s']
		samplerate = params['samplerate']
		hop_s = params['hop_s']
	except KeyError:
		"""
		# super fast
		samplerate, win_s, hop_s = 4000, 128, 64 
		# fast
		samplerate, win_s, hop_s = 8000, 512, 128
		"""
		# default:
		samplerate, win_s, hop_s = 44100, 1024, 512

	s = source(path, samplerate, hop_s)
	samplerate = s.samplerate
	o = tempo("specdiff", win_s, hop_s, samplerate)
	# List of beats, in samples
	beats = []
	# Total number of frames read
	total_frames = 0

	while True:
		samples, read = s()
		is_beat = o(samples)
		if is_beat:
			this_beat = o.get_last_s()
			beats.append(this_beat)
			#if o.get_confidence() > .2 and len(beats) > 2.:
			#	break
		total_frames += read
		if read < hop_s:
			break

	# Convert to periods and to bpm 
	if len(beats) > 1:
		if len(beats) < 4:
			print("few beats found in {:s}".format(path))
		bpms = 60./np.diff(beats)
		return bpms, total_frames, win_s, samplerate, hop_s
	else:
		b = 0
		print("not enough beats found in {:s}".format(path))
		return []

def dump_bpm(path, **kwargs):
	outpath = path + '.bpm.gz'
	allbpm, total_frames, win_s, samplerate, hop_s = get_file_all_bpm(path)
	d = {
		'file': path,
		'bpm': list(allbpm),
		'total_frames': total_frames,
		'win_s': win_s,
		'samplerate': samplerate,
		'hop_s': hop_s,
	}
	with pycommons.open_file(outpath, 'wb', True) as f:
		f.write(json.dumps(d))

def print_bpm(path, **kwargs):
	if not path.endswith('.bpm'):
		path += '.bpm.gz'
	with pycommons.open_file(path, 'rb', True) as f:
		bpm =json.loads(f.read())
		print '{} -> {}'.format(path, np.median(bpm['bpm']))
	plot(path, bpm['bpm'], **bpm)

def plot(path, beats, total_frames, win_s, samplerate, hop_s, **kwargs):
	from numpy import mean, median, diff
	import matplotlib.pyplot as plt
	bpms = 60./ diff(beats)
	print('mean period: %.2fbpm, median: %.2fbpm' % (mean(bpms), median(bpms)))
	print('plotting %s' % path)
	plt1 = plt.axes([0.1, 0.75, 0.8, 0.19])
	plt2 = plt.axes([0.1, 0.1, 0.8, 0.65], sharex = plt1)
	plt.rc('lines',linewidth='.8')
	for stamp in beats: plt1.plot([stamp, stamp], [-1., 1.], '-r')
	plt1.axis(xmin = 0., xmax = total_frames / float(samplerate) )
	plt1.xaxis.set_visible(False)
	plt1.yaxis.set_visible(False)

	# plot actual periods
	plt2.plot(beats[1:], bpms, '-', label = 'raw')

	# plot moving median of 5 last periods
	median_win_s = 5
	bpms_median = [ median(bpms[i:i + median_win_s:1]) for i in range(len(bpms) - median_win_s ) ]
	plt2.plot(beats[median_win_s+1:], bpms_median, '-', label = 'median of %d' % median_win_s)
	# plot moving median of 10 last periods
	median_win_s = 20
	bpms_median = [ median(bpms[i:i + median_win_s:1]) for i in range(len(bpms) - median_win_s ) ]
	plt2.plot(beats[median_win_s+1:], bpms_median, '-', label = 'median of %d' % median_win_s)

	plt2.axis(ymin = min(bpms), ymax = max(bpms))
	#plt2.axis(ymin = 40, ymax = 240)
	plt.xlabel('time (mm:ss)')
	plt.ylabel('beats per minute (bpm)')
	plt2.set_xticklabels([ "%02d:%02d" % (t/60, t%60) for t in plt2.get_xticks()[:-1]], rotation = 50)

	#plt.savefig('/tmp/t.png', dpi=200)
	plt2.legend()
	plt.show()


if __name__ == '__main__':
	common.common_process(dump_bpm, print_bpm, '*.bpm.gz')
