import sys
import common

def callback(path):
	print 'Received callback: {}'.format(path)

common.process_path(sys.argv[1], callback)
