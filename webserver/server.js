var express = require('express');
var morgan = require('morgan');
var app = express();
var fs = require('fs');
var compression = require('compression');
var crypto = require('crypto');
var child_process = require('child_process');

var http = require('http').createServer(app);
var io = require('socket.io')(http);

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
function listAvailableTracks() {
	var result = [];
	var files = fs.readdirSync('/phonelab/hackathon-data');
	for(var f in files) {
		if(endsWith(files[f], '.analysis.gz')) {
			var name = files[f].substring(0, files[f].indexOf('.analysis.gz'));
			name = name.replace(/_/g, '/');
			result.push(name);
		}
	}
	console.log('result files:' + result.length);
	availableTracks = result;
	return result;
}

io.on('connection', function(socket) {
	// Get autocomplete json
	var json = listAvailableTracks();
	socket.emit('autocomplete', JSON.stringify(json));

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


http.listen(HTTP_PORT, function () {
	console.log('HTTP listening on port ' + HTTP_PORT);
});
