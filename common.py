import os,sys,argparse
import logging
import multiprocessing

# Just so I don't piss off people with an additional setup step :)
try:
	import pycommons
except:
	# No pycommons. Fetch it
	import subprocess
	subprocess.check_call('git clone https://github.com/gurupras/pycommons', shell=True)
	import pycommons


from pycommons import generic_logging
generic_logging.init(level=logging.DEBUG)
logger = logging.getLogger(__file__)

from pycommons.file_entry import FileEntry

def setup_parser(parser=None):
	if parser is None:
		parser = argparse.ArgumentParser(description='Process audio file')
	parser.add_argument('source', help='The file or directory to process')
	parser.add_argument('--dump', action='store_true', help='Dump intermediate format')
	parser.add_argument('--plot', action='store_true', default=False, help='Plot')
	return parser

def common_process(dump_callback, print_callback, regex):
	parser = setup_parser()
	args = parser.parse_args()

	if args.dump:
		process_path(args.source, dump_callback, regex=['*.mp3', '*.m4a'], **vars(args))
	else:
		process_path(args.source, print_callback, regex=regex, **vars(args))

def process_path(path, callback, pool=None, regex='*', **kwargs):
	entry = FileEntry(path, None)
	entry.build(regex=regex)
	if pool:
		pool = multiprocessing.Pool()

	if entry.isdir():
		for file in entry.get_files():
			if pool:
				pool.apply_async(func=callback, args=(file.path(),))
			process_path(file.path(), callback, pool, regex, **kwargs)
	else:
		callback(entry.path(), **kwargs)
	if pool:
		pool.close()
		pool.join()
