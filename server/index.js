const httpServer = require("http").createServer();
const io = require("socket.io")(httpServer, {
	cors: {
	    origin: "*",
	    methods: ["GET", "POST"]
  	}
});

players = []
playersHr = []

currentlyPlaying = false
remainingAction = false

io.on("connection", (socket) => {
  console.log("Client connected");
  socket.join('game_room')
  socket.on("connected", (data) => {
  	console.log("Player client transmitted join data.")
  	console.log(data)
  	players.push({
  		playerNick: data.name,
  		playerIdentifier: data.identifier,
  		playerSocket: socket
  	})
  	playersHr.push({
  		playerNick: data.name,
  		playerIdentifier: data.identifier
  	})
  	if(currentlyPlaying == false){
  		console.log("No current player found. Defaulting the new player as the currentlyPlaying.")
  		currentlyPlaying = {
  			playerNick: data.name,
  			playerIdentifier: data.identifier
  		}
  		console.log(currentlyPlaying)
  	}
  	io.to('game_room').emit("player_list_update", playersHr )
  	io.to('game_room').emit("new_turn", currentlyPlaying)
  })
  socket.on("card", (card) => {
  	console.log(card)
  	if(card.cardType == "plustwo"){
  		remainingAction = "plustwo"
  	}
  	if(card.cardType == "plusfour"){
  		remainingAction = "plusfour"
  	}
  	if(card.cardType == "reverse"){
  		remainingAction = "reverse"
  	}
  	io.to('game_room').emit("card", card)
  })
  socket.on("turn_over", (data) => {
  	if(remainingAction == "reverse"){
  		players.reverse()
  		playersHr.reverse()
  		io.to('game_room').emit("player_list_update", playersHr )
  		console.log("Reversed gameplay order.")
  		remainingAction = false
  	}
  	console.log("Received player turn complete message from:")
  	console.log(data)
  	console.log("Player found:")
  	let player = players.find(x => x.playerIdentifier === data.identifier)
  	let index = players.indexOf(player)
  	console.log(playersHr[index])
  	console.log(index)

  	if(index == (players.length-1)){
  		console.log("Reached the end of the player list. Resetting index to zero.")
  		index = 0
  	}else{
  		console.log("Still more players to go. Incrementing index.")
  		index = index + 1
  	}

  	let next_player = playersHr[index]
  	currentlyPlaying = next_player

  	console.log("Sending in the new player.")
  	console.log(currentlyPlaying)

  	if(remainingAction){
  		if(remainingAction == "plustwo"){
  			players[index].playerSocket.emit("plus_cards", 2)
  		}
  		if(remainingAction == "plusfour"){
  			players[index].playerSocket.emit("plus_cards", 4)
  		}
  		remainingAction = false
  	}

  	io.to('game_room').emit("new_turn", currentlyPlaying)
  })
});

httpServer.listen(9375, '0.0.0.0');
