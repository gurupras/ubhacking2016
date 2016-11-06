var express = require('express');
var morgan = require('morgan');
var app = express();
var fs = require('fs');
var compression = require('compression');
var crypto = require('crypto');
var child_process = require('child_process');

var http = require('http').createServer(app);
var io = require('socket.io')(http);

var MongoClient = require('mongodb').MongoClient
var assert = require('assert')

var HTTP_PORT = 8080;

app.use(morgan('combined'));
app.use(compression());

/* ------------------------ TEST URLS ------------------------*/
app.get('/', function (req, res) {
	res.send(fs.readFileSync(__dirname + '/static/html/index.html', 'utf-8'));
});

/* -------------------- END OF TEST URLS --------------------*/

app.use('/static', express.static('./static'));
app.use('/media/ext/Guru/Music', express.static('/media/ext/Guru/Music'));


function endsWith(str, suffix) {
	return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

var availableTracks;
var trackMap = {};

function listAvailableTracks(callback) {
	if (availableTracks) {
		callback(availableTracks);
		return;
	}
	var result = [];
	collection = mongo.collection('songs')
	collection.find({}, {_id:true, artist:true, track:true}).toArray(function(err, docs) {
		console.log(docs.length)
		for (var d of docs) {
			var name = d.artist + ' - ' + d.track.replace('.features', '')
			name = name.replace(/_/g, '/');
			result.push(name);
			trackMap[name] = d._id
		}
		console.log('result files:' + result.length);
		availableTracks = result;

		callback(result);
	});
}

io.on('connection', function(socket) {
	// Get autocomplete json
	listAvailableTracks(function(json) {
		socket.emit('autocomplete', JSON.stringify(json));
	});
	socket.on('mashup', function(msg) {
		track = msg.file;
		file = track + '.features.gz';
		file = file.replace(/\//g, '_');
		// Open this file and find the source
		file = '/phonelab/hackathon-data/' + file;
		//file = file.replace(/ /g, '\ ');
		var cmd = 'zcat "' + file + '"';
		console.log('CMD:' + cmd);
		var jsonStr = child_process.execSync(cmd, {shell: '/bin/bash'});
		var json = JSON.parse(jsonStr);
		var data = {};
		data.src = json.ub_source_file;
		socket.emit('mashup', JSON.stringify(data));
	});
});

var url = 'mongodb://localhost:27017/music'
console.log(url)
var mongo;

MongoClient.connect(url, function(err, db) {
	assert.equal(null, err);
	console.log("Connected successfully to server");
	mongo = db
	http.listen(HTTP_PORT, function () {
		console.log('HTTP listening on port ' + HTTP_PORT);
	});
});

