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
		return bpms
	else:
		b = 0
		print("not enough beats found in {:s}".format(path))
		return []

def dump_bpm(path):
	outpath = path + '.bpm'
	allbpm = get_file_all_bpm(path)
	with pycommons.open_file(outpath, 'wb', True) as f:
		f.write(json.dumps(list(allbpm)))

def print_bpm(path):
	if not path.endswith('.bpm'):
		path += '.bpm'
	with pycommons.open_file(path, 'rb', True) as f:
		bpm =json.loads(f.read())
		print '{} -> {}'.format(path, np.median(bpm))

if __name__ == '__main__':
	common.common_process(dump_bpm, print_bpm, '*.bpm')
