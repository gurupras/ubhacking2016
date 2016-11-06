import os,sys,argparse
import json
import traceback
import hashlib
import atexit

import spotify

import pycommons
import logging
from pycommons import generic_logging
generic_logging.init(level=logging.DEBUG)
logger = logging.getLogger(__file__)

from pycommons.file_entry import FileEntry

import mutagenwrapper

def setup_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('path', help='Path with audio files to process')
	parser.add_argument('outdir', help='Output directory')
	parser.add_argument('--regex', default=['*.mp3', '*.aac', '*.m4a'], action=pycommons.ListAction,
			help='Regex with which to filter files')
	parser.add_argument('--sample', type=float, default=1.0,
			help='Random sampling. If value > provided value, it will be ignored. Thus 1.0 means no file will be ignored')
	return parser

def get_state_and_file(outdir):
	state_file = os.path.join(outdir, 'state.log')
	state = {}
	file = None
	if not os.path.exists(state_file):
		file = pycommons.open_file(state_file, 'wb')
		file.write('{}')
		file.close()
	else:
		with pycommons.open_file(state_file, 'rb') as f:
			state = json.loads(f.read())
	state_file = open(state_file, 'wb')
	return state, state_file

def process(path, outdir, regex, sampling):
	if not os.path.exists(outdir):
		os.makedirs(outdir)

	global state

	# Get a file that should exist in the outdir
	# this file is used for saving state between multiple
	# runs of this script
	state, state_file = get_state_and_file(outdir)

	s = spotify.Spotify()
	s.authenticate()

	entry = FileEntry(path, None)
	entry.build(regex=regex)

	for file in entry.get_files():
		digest = hashlib.md5(open(file.path(), 'rb').read()).hexdigest()
		if state.get(digest, None) is not None:
			continue

		try:
			data = mutagenwrapper.read_tags(file.path())
			artist = data.get('artist')[0]
			title = data.get('title')[0]
			if artist == '' or title == '':
				logger.error('Failed on file {}'.format(file.path()))
				continue
			print '{} - {}'.format(artist, title)
			params = {
					'q': 'artist:{} title:{}'.format(artist, title),
					'type': 'track',
					'limit': 1
			}
		except Exception, e:
			tb = traceback.format_exc()
			print tb

		try:
			search = s.search(params)
			item0 = search['tracks']['items'][0]
			trackid = item0['id']
			artist = item0['artists'][0]['name']
			track = item0['name']

			features = s.audio_features(trackid)
			analysis = s.audio_analysis(trackid)

			features['ub_source_file'] = os.path.abspath(file.path())
			analysis['ub_source_file'] = os.path.abspath(file.path())

			base = '{} - {}'.format(artist, track)
			# XXX: Hack..handle AC/DC
			base = base.replace('/', '_')
			# Now join with outdir
			base = os.path.join(outdir, base)

			features_file = '{}.features.gz'.format(base)
			analysis_file = '{}.analysis.gz'.format(base)

			with pycommons.open_file(features_file, 'wb', True) as f:
				f.write(json.dumps(features))
			with pycommons.open_file(analysis_file, 'wb', True) as f:
				f.write(json.dumps(analysis))

			state[digest] = True
		except Exception, e:
			logger.error("Could not process file {}: {}".format(file.path(), e))
	state_file.write(json.dumps(state))
	state_file.close()

args = None
state = {}

def main(argv):
	parser = setup_parser()
	global args
	args = parser.parse_args(argv[1:])

	atexit.register(on_exit)
	process(args.path, args.outdir, args.regex, args.sample)

def on_exit():
	outdir = args.outdir
	fpath = os.path.join(outdir, 'state.log')
	if len(state) > 0:
		with pycommons.open_file(fpath, 'wb') as f:
			f.write(json.dumps(state))
		print 'Wrote state before exit'

if __name__ == '__main__':
	main(sys.argv)
