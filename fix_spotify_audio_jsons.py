import os,sys,argparse
import json
import re
import multiprocessing
import traceback

from pycommons.file_entry import FileEntry
import pycommons.shutil_helper as sh
import pycommons

# Fixes data from spotify
# Initial version of files don't have aritst/track info in the jsons themselves
# This adds them by parsing filename which is of format artist - track



def process(path, queue):
	name, _ = os.path.splitext(os.path.basename(path))
	# Split name by -
	match = pattern.match(name)
	try:
		assert match, 'Did not match: {}'.format(name)
		gd = match.groupdict()
		with pycommons.open_file(path, 'rb') as f:
			data = json.loads(f.read())
		data['artist'] = gd['artist']
		data['track'] = gd['track']

		with pycommons.open_file(path, 'wb') as f:
			f.write(json.dumps(data))

		if queue is not None:
			queue.put(None)
	except Exception, e:
		if queue is not None:
			tb = traceback.format_exc()
			queue.put((path, tb))
		raise e



basepath = sys.argv[1]

pattern = re.compile('(?P<artist>.*) - (?P<track>.*)')


pool = multiprocessing.Pool()
queue = multiprocessing.Queue()

started = 0
files, _ = sh.ls(basepath, '*.gz')
for f in files:
	path = os.path.join(basepath, f)

	#pool.apply_async(func=process, args=(path, queue))
	process(path, queue)
	started += 1
	if started % 1 == 0:
		print 'Finished {}'.format(started)
pool.close()

print 'Started all'
for idx in range(started):
	data = queue.get()
	if data is not None:
		print '{} - {}'.format(data[0], data[1])
	if idx % 1 == 0:
		print 'Processed %03d files' % (dx)
pool.join()
