import os,sys
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

def process_path(path, callback, pool=None, regex='*'):
	entry = FileEntry(path, None)
	entry.build(regex=regex)
	if pool:
		pool = multiprocessing.Pool()

	for file in entry.get_files():
		if pool:
			pool.apply_async(func=callback, args=(file.path(),))
		callback(file.path())
	if pool:
		pool.close()
		pool.join()
