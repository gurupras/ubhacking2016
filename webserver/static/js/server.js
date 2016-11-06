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

	socket = io();

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
		$('#download').on('click', function() {
			window.location = json.src;
		});

		// Hide spinner
		$('#spinner').hide();

		for (var b of json.blobs) {
			delete b.path;
		}
		var pretty = JSON.stringify(json.blobs, null, 4).replace(/\n/g, '<br>');
		$('#debug').html(pretty);
	});

	function submit(file) {
		$('#spinner').show();
		socket.emit('mashup', {file: file});
	};

	var runOnce;

//TODO: Enter

	$('#search-input').on('keyup', function(e) {
		// Clear debug
		$('#debug').html('');
		if(e.which == 13) {
			submit($(this).val());
		}

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
