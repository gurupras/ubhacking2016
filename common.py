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

def process_path(path, callback, pool=None):
	entry = FileEntry(path, None)
	entry.build(regex='*')
	if pool:
		pool = multiprocessing.Pool()


	if entry.isdir():
		for child in entry:
			process_path(child.path(), callback)
	else:
		# This is a file
		if pool:
			pool.apply_async(func=callback, args=(entry.path(),))
		callback(entry.path())
	if pool:
		pool.close()
		pool.join()
