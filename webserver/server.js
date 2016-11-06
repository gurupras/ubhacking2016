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

//function mashup(

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

function round5(x) {
	return Math.ceil(x/5)*5
}

var bpms;

function createBpmLists(callback) {
	if (bpms) {
		callback()
		return
	}
	bpms = {}
	collection = mongo.collection('songs')
	collection.find({}, {_id:true, ub_source_file:true, sections:true}).toArray(function(err, docs) {
		for (var d of docs) {
			for (section of d.sections) {
				tempo = round5(section.tempo);
				if (!bpms[tempo]) {
					bpms[tempo] = []
				}
				bpms[tempo].push({_id:d._id, source: d.ub_source_file, data: section})
			}
		}
		callback()
	});
}

const startDuration = 15.0;
const usePrevBpm = false;
const sourceFreq = 2;

function mashup(id, callback) {
	result = []
	collection = mongo.collection('songs')
	collection.findOne({_id: id}, function(err, item) {
		var pos = 0.0, index = 0, prevBpm = 0;
		var wasSource = false, blobs = [];
		var l = item.sections.length;
		sourceCntr = 0;

		for (s of item.sections) {
			var choice;
			// Pick next section
			if (pos < startDuration || sourceCntr == sourceFreq || index == l-1) {
				pos += s.duration;
				choice = {_id: item._id, source: item.ub_source_file, data: s}
				sourceCntr = 0;
			} else {
				if (usePrevBpm) {
					tempo = prevBpm;
				} else {
					tempo = s.tempo;
				}
				tempo = round5(s.tempo);
				r = Math.floor(Math.random() * bpms[tempo].length);
				choice = bpms[tempo][r];
				sourceCntr += 1;
			}
			prevBpm = choice.data.tempo;
			blob = {source: choice.source, start: choice.data.start, duration: choice.data.duration}
			blobs.push(blob)
			index += 1;
		}
		callback(blobs)
	});
}

io.on('connection', function(socket) {
	// Get autocomplete json
	listAvailableTracks(function(json) {
		socket.emit('autocomplete', JSON.stringify(json));
		createBpmLists(function(){});
	});
	socket.on('mashup', function(msg) {
		track = msg.file;
		var id = trackMap[track]
		if (id) {
			console.log('found id=' +id)
			mashup(id, function(blobs) {
				//data.src = json.ub_source_file;
				//socket.emit('mashup', JSON.stringify(data));
				for (b of blobs) {
					console.log(b)
				}
				// TODO: What?
				console.log('mashup done')
			});
		}
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

