import os,sys,argparse
import tempfile
import pycommons

def setup_parser(parser=None):
	if not parser:
		parser = argparse.ArgumentParser()
	parser.add_argument('--input', '-i', required=True,
			help='Input file to process')
	parser.add_argument('--convert', '-C',
		help='Convert to WAV format and process that')
	return parser

def should_convert(file):
	if not os.path.exists(file):
		sys.stderr.write('''File '{}' does not exist!'''.format(file))
		sys.exit(-1)

	name, ext = os.path.splitext(os.path.basename(file))
	if ext != '.wav':
		return True
	else:
		return False

def convert(file):
	if not os.path.exists(file):
		sys.stderr.write('''File '{}' does not exist!'''.format(file))
		sys.exit(-1)

	fd = tempfile.NamedTemporaryFile(suffix='.wav')
	tmpfile = fd.name
	pycommons.run('ffmpeg -i {} {}'.format(file, tmpfile))
	return tmpfile

