	var canvas = document.getElementById('game_canvas');
	var ctx = canvas.getContext('2d');
	const colors = ["blue", "red"];
	var players = [{},{}];

	/**
	 * Draw a <color> rectangle centered on <pos>, and rotated <angle> degrees.
	 **/
	function drawRectangle(pos, color) {
		ctx.save();
		ctx.fillStyle = "black";
		ctx.translate(pos[0], pos[1]);
		ctx.rotate(pos[2] * Math.PI / 180);
		ctx.fillRect(-7, -20, 13, 40);
		ctx.fillStyle = color;
		ctx.fillRect(-6, -19, 11 ,38);
		ctx.restore();
	}

	// function run by Game.html and Player.html
	function updateWebSocket(){
		// when received update about a Game, just display it
		socket.on('update{{ GameName }}', function (msg) {
			// get data (it's a json)
			var data = JSON.parse(msg);

			// load image and get players names only first time
			if (data.hasOwnProperty('map_name')) {
				// load the image and draw it
				let map_bg = new Image();
				map_bg.src = '../data/game/maps/' + data['map_image'];
				map_bg.onload = function () {
					canvas.setAttribute("width", map_bg.width);
					canvas.setAttribute("height", map_bg.height);
					ctx.drawImage(map_bg, 0, 0);
					// draw all rectangles (only for testing)
					/*for (const track of data.rectangles) {
						for (const wagon of track) {
							drawRectangle(wagon, "green");
						}
					}*/
					// draw already claimed tracks
					for(let i=0; i<2; i++){
		                for (const track of data.players[i].tracks) {
		                    for (const wagon of track) {
		                        drawRectangle(wagon, colors[i]);
		                    }
						}
	                }
				}
			}

			// a player claimed a track, draw it
			if (data.hasOwnProperty('track')) {
				for (const wagon of data.track[0]) {
					drawRectangle(wagon, colors[data.track[1]]);
				}
			}
			// display move message
			if (data.hasOwnProperty('move')){
				let comments = document.getElementById('moves');
				comments.innerHTML += data['move'] + "</br>";
				comments.scrollTop = comments.scrollHeight;
			}
			// update face up cards
			if (data.hasOwnProperty('faceUp')){
				for(let i=0; i<5; i++){
					document.getElementById('f' + i).style.backgroundImage = cards[data.faceUp[i]];
				}
			}
			// update players information
			for(let i=0; i<2; i++){
				document.getElementById('p' + (i+1) + '-info').innerHTML =
				"<B>" + data.players[i].name + "</B><BR/>" +
				"Score: " + data.players[i].score + "pts, " +
				"Wagons: " + data.players[i].wagons + ", " +
				"Cards: " + data.players[i].nbCards + ", " +
				"Objectives: " + data.players[i].objectives;
			}

			// update comments
			if (data.comments) {
				let comments = document.getElementById('comments');
				comments.innerHTML += data.comments + "</br>";
				comments.scrollTop = comments.scrollHeight;
			}
		});
	}

    /* register to endOfGame and display it when received*/
    function displayEndOfGame(){
        socket.on('endOfGame', function(msg){
            document.getElementById('endOfGame').innerHTML = msg;
        });
    }
