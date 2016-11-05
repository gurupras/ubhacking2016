import sys
import common
import argparse
import json

import pycommons

import logging
from pycommons import generic_logging
generic_logging.init(level=logging.DEBUG)

from aubio import source, pitch

def process(path, downsample=1, samplerate=44100, win_s=4096, hop_s=512, tolerance=0.8, algorithm='yin', unit='freq', dump=False):
	'''
		downsample = 1
		samplerate = 44100 // downsample
		if len( sys.argv ) > 2: samplerate = int(sys.argv[2])

		win_s = 4096 // downsample # fft size
		hop_s = 512  // downsample # hop size


		tolerance = 0.8
	'''
	s = source(path, samplerate, hop_s)
	samplerate = s.samplerate

	pitch_o = pitch(algorithm, win_s, hop_s, samplerate)
	pitch_o.set_unit(unit)
	pitch_o.set_tolerance(tolerance)

	pitches = []
	confidences = []

	# total number of frames read
	total_frames = 0
	while True:
		samples, read = s()
		p = pitch_o(samples)[0]
		#pitch = int(round(pitch))
		confidence = pitch_o.get_confidence()
		#if confidence < 0.8: pitch = 0.
#		print("%f %f %f" % (total_frames / float(samplerate), p, confidence))
		pitches += [p]
		confidences += [confidence]
		total_frames += read
		if read < hop_s: break

	# XXX: The demo_pitch.py seems to skip the first value
	# We just do the same
	pitches = pitches[1:]
	confidences = confidences[1:]
	times = [t * hop_s for t in range(len(pitches))]

	return pitches, confidences

def dump_callback(path):
	pitches, confidences = process(path)
	d = {
		'file': path,
		'pitches': [float(x) for x in pitches],
		'confidences': [float(x)for x in confidences],
	}
	outpath = path + '.pitch.gz'
	with pycommons.open_file(outpath, 'wb', True) as f:
		f.write(json.dumps(d))


def print_callback(path):
	if path.endswith('.mp3'):
		path += '.pitch'
	with pycommons.open_file(path, 'rb', True) as f:
		d = json.loads(f.read())
	json.dumps(d, indent=2)

if __name__ == '__main__':
	common.common_process(dump_callback, print_callback, '*.pitch.gz')
