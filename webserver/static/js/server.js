var player;
var socket;

window.onload = function() {
	player = plyr.setup('#plyr', {
		controls: [
			'play',
			'current-time',
			'duration',
			'mute',
			'volume',
			'progress',
			'fullscreen'
		],
		keyboardShortcuts: {
			focused: true,
			global: true
		},
	})[0];

	socket = io('http://dirtydeeds:8080');

	socket.on('autocomplete', function(msg) {
		var json = JSON.parse(msg);
		var data = {data: {}};
		for(var i in json) {
			data.data[json[i]] = null;
		}
		$('#search-input').autocomplete(data);
	});

	socket.on('mashup', function(msg) {
		var json = JSON.parse(msg);
		player.source({
			type: 'audio',
			//title: 'Mashup: ' + json.artist + ' - ' + json.track,
			sources: [{
				src: json.src,
				type: 'audio/mp3',
			}],
		});
	});

	function submit(file) {
		socket.emit('mashup', {file: file});
	};

	var runOnce;
	$('#search').on('keyup', function() {
		if(runOnce) {
			$('#search').off('keyup');
		} else {
			$('#search').find('.dropdown-content').on('click', function(e) {
				submit($(e.target).text());
			});
			runOnce = true;
		}
	});
};
