import os,sys,argparse
import json
import tempfile
import subprocess
import multiprocessing
import pycommons


def run(cmd):
#	print '$>{}'.format(cmd)
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	p.wait()

def stitch_input_file(path):
	output = path + '.mp3'
	cmd = 'avconv -f concat -i {} -c:a libmp3lame {}'.format(path, output)
	run(cmd)

def stitch_concat(output, files):
	concat = ' '.join(files)
	cat_output = output + '.cat'
	cmd = 'cat {} >{}'.format(concat, cat_output)
	run(cmd)

	final_output = output
	cmd = 'avconv -i {} {}'.format(cat_output, final_output)
	run(cmd)


def main():
	outdir = sys.argv[1]
	if not os.path.exists(outdir):
		os.makedirs(outdir)

	data = json.loads(sys.argv[2])
	pool = multiprocessing.Pool()

	# Make a temporary file to get a sense of a unique prefix we can use for all temporary files
	fd = tempfile.NamedTemporaryFile(prefix='mashup-', dir=outdir)
	path = fd.name

	files = []
	# Data is an array of jsons
	for idx, chunk in enumerate(data):
		filepath = chunk['path']
		start = chunk['start']
		duration = chunk['duration']

		chunk_path = path + '-{}.chunk.mp3'.format(idx)
		files.append(chunk_path)

		# Start is a float. Convert this to hh:mm:ss?
		# Try without it
		cmd = 'avconv -ss {} -i "{}" -c:a libmp3lame -t {} {}'.format(start, filepath, duration, chunk_path)
		#pool.apply_async(func=run, args=(cmd,))
		run(cmd)

	pool.close()
	pool.join()

	# Now stitch them all
	# avconv expects an input file containing the list of other files to concatenate
	# so create that
#	with pycommons.open_file(chunk_path, 'wb') as f:
#		for file in files:
#			f.write("file '{}'\n".format(file))
#	# OK, now the file is ready.
#	stitch_input_file(chunk_path)

	# Don't do any of the above BS. Our chunk file names don't have spaces
	# So we just use the concat protocol
	output = '{}.mp3'.format(path)
	stitch_concat(output, files)

	sys.stdout.write(output)

if __name__ == '__main__':
	main()
