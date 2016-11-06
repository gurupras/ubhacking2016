'use strict';

var MongoClient = require('mongodb').MongoClient,
	assert = require('assert'),
	ArgumentParser = require('argparse').ArgumentParser,
	child_process = require('child_process');

const fs = require('fs');
const zlib = require('zlib');


/////////////////////////////////////////////////////////
// Argument parsing	
var parser = new ArgumentParser({
	version: '0.0.1',
	addHelp:true,
	description: 'Create music analysis mongodb'
});

parser.addArgument(
	['source'],
	{
		help: 'source of analysis files'
	}
);
parser.addArgument(
	['db'],
	{
		help: 'name of the db to create'
	}
);

var args = parser.parseArgs();
console.dir(args)	

/////////////////////////////////////////////////////////

var url = 'mongodb://localhost:27017/' + args.db;
console.log(url)

MongoClient.connect(url, function(err, db) {
	assert.equal(null, err);
	console.log("Connected successfully to server");
	insertDocuments(db, function() {
		db.close();
	});
});

function processFile(path, collection) {
	var other = path.replace('features.gz', 'analysis.gz')
	var cmd1 = 'gunzip -c "' + path + '"';
	var cmd2 = 'gunzip -c "' + other + '"';
	try {
		var jsonStr = child_process.execSync(cmd1, {shell: '/bin/bash'});
		var features = JSON.parse(jsonStr);

		jsonStr = child_process.execSync(cmd2, {shell: '/bin/bash'});
		var analysis = JSON.parse(jsonStr)
		var sections = analysis.sections
		features.sections = sections

		collection.insert(features)
	} catch (err) {
		console.log('SKIPPING: ' + path)
		console.log(err)
	}
}

function processDir(path, db) {
	var collection = db.collection('songs');
	var files = fs.readdirSync(path)
	for (var f of files) {
		if (f.endsWith('features.gz')) {
			if(f.indexOf('"') >= 0) {
				continue;
			}
			console.log(f)
			processFile(args.source + f, collection)
		}
	}
}

var insertDocuments = function(db, callback) {
	var collection = db.collection('songs');
	collection.remove()
	processDir(args.source, db)
	callback()
};
