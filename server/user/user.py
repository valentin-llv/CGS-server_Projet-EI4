import sys, json, socket as SocketType, logging, select

from user.exceptions import *

from gamesManager.gamesManager import GamesManager
from gamesManager.exceptions import PlayerReconnectFailed

from player.player import Player

from utils.pollableQueue import PollableQueue

# State machine
class StateMachine:
	WAIT_FOR_NAME = 0
	WAIT_FOR_GAME_SETTINGS = 1
	PLAYING_GAME = 2

class User(Player):
	users = []
	uidsCounter = 0

	@staticmethod
	def listUsers():
		print("Users :")
		for user in User.users: print(f"- User {user.id}: {user.name}")

	def __init__(self, socket: SocketType):
		# Init parent class Player
		Player.__init__(self)

		# Store ref of each user and assign unique id
		User.users.append(self)
		self.id = User.uidsCounter
		User.uidsCounter += 1

		self.logger = logging.getLogger()
		self.queue = PollableQueue()
	
		# Store ref to socket and self communication manager
		self.socket: SocketType = socket
		self.socket.setblocking(False)

		self.state = StateMachine.WAIT_FOR_NAME

		self.name = None
		self.game = None

		self.waitingToReconnect = False

	def start(self):
		try: self.loop()
		except SocketClosedException: # Handle user disconnection
			logging.getLogger().message(f"User {self.name} has been disconnected")

			# If user is in a game, notify the game that the player has been disconnected, he will have x seconds to reconnect
			if self.game:
				self.waitingToReconnect = True
				self.game.event("playerDisconnected", { "player": self })

			# Delete user
			self.destroy()

	def loop(self):
		nextMsgLength: str = None
		
		while True:
			# Use select on socket recv and queue to handle multiple events
			readable, _, _ = select.select([self.socket, self.queue], [], [])

			for r in readable:
				if r == self.socket: # If socket is readable, get message from user
					if not nextMsgLength: # Transmission always start by sending the message length
						try: nextMsgLength = self.readFirstBlock()
						except FirstSocketMessageIsNotInt or MessageTooLong: continue
					else: # Get message from user
						try:
							self.handleMessage(self.readMessage(nextMsgLength))
						except MessageNotInJsonFormat: continue

						nextMsgLength = None
				else: # If queue is readable, get event and data from the queue
					event, data = self.queue.get()

					try: self.handleEvent(event, data)
					except InvalidGameSettings or PlayerReconnectFailed: continue

	def readFirstBlock(self):
		try: firstBlock = self.socket.recv(6)
		except ConnectionResetError: raise SocketClosedException()

		# If message is empty then users has been disconnected
		if not firstBlock: raise SocketClosedException()

		firstBlock = firstBlock.decode("UTF-8")
		self.logger.debug(f"User {self.name} sent first block size: {firstBlock}")

		try: nextMsgLength: int = int(firstBlock.strip()[0: -1])
		except Exception: raise FirstSocketMessageIsNotInt(self.sendMsg, self.name)

		if not (1 <= nextMsgLength <= 99999): raise MessageTooLong(self.sendMsg, self.name)
		return nextMsgLength
	
	def readMessage(self, nextMsgLength: int):
		try: message: str = self.socket.recv(nextMsgLength)
		except ConnectionResetError: raise SocketClosedException()

		if not message: raise SocketClosedException()

		message = message.decode("UTF-8")
		message = message.replace("'", '"')
		
		self.logger.debug(f"User {self.name} sent message: {message}")
		return message
	
	def handleMessage(self, message):
		try: message = json.loads(message)
		except json.decoder.JSONDecodeError: raise MessageNotInJsonFormat(self.sendMsg, self.name)

		try:
			match self.state:
				case StateMachine.WAIT_FOR_NAME: self.getName(message)
				case StateMachine.WAIT_FOR_GAME_SETTINGS: self.getGameSettings(message)
				case StateMachine.PLAYING_GAME: self.userPlay(message)
		except MessageDoesNotContainName: pass
		except UsernameAlreadyTaken: pass
		except UserDidNotSendGameSettings or InvalidGameSettings: pass
		except UserSentInvalidInstruction or UserSentWrongActionDuringHisTurn or UserSentInvalidMove or UserSentWrongActionDuringOpponentTurn: pass

	def sendMsg(self, message: dict):
		try: jsonMessage = json.dumps(message)
		except Exception: raise InvalidMessageFormat()
		
		messageLength: str = len(jsonMessage)

		firstBlock = str(messageLength).encode() + b' ' * (5 - len(str(messageLength)))
		secondBlock = jsonMessage.encode()

		try:
			self.socket.send(firstBlock)
			self.socket.send(secondBlock)
		except ConnectionResetError: raise SocketClosedException()

	def handleEvent(self, event, data):
		if event == "joinedGame":
			self.game = data["game"]

			board = self.game.getBoard()
			self.sendMsg({
				"state": 1, # OK
				"gameId": self.game.id,
				"gameSeed": self.game.seed,
				"firstPlayer": 2 if self.game.players[self.game.whoPlays] == self else 1,
				"boardWidth": self.game.width,
				"boardHeight": self.game.height,
				"nbElements": len(board),
				"board": board,
			})

			self.state = StateMachine.PLAYING_GAME

		# Game events
		elif event == "getMoveResponse": self.sendMsg({ "state": 1, "returnCode": data["returnCode"], "move": data["move"], "op_message": data["message"], "message": data["message"] })
		elif event == "sendMoveResponse": self.sendMsg({ "state": 1, "returnCode": data["returnCode"], "message": data["message"] })
		elif event == "gameEnded": self.sendMsg({ "state": 1, "winner": data["winner"].name })

		# Errors
		elif event == "invalidGameSettings" or event == "invalidBotName": raise InvalidGameSettings(self.sendMsg, self.name)
		elif event == "playerReconnectFailed": raise ReconnectionToSessionFailed(self.sendMsg, self.name)

		# Default
		else: self.logger.debug(f"User {self.name} received unknown event {event}")
	
	def getName(self, message):
		# State 0: Waiting for user name
		if not "name" in message or not message["name"]: raise MessageDoesNotContainName(self.sendMsg, self.name)
		
		# Check if username is already taken
		for user in User.users:
			if user.name == message["name"] and user.waitingToReconnect == False: 
				raise UsernameAlreadyTaken(self.sendMsg, self.name)

		self.name = message["name"]
		self.state = StateMachine.WAIT_FOR_GAME_SETTINGS

		self.sendMsg({ "state": 1 }) # Send confirmation message, state = 1 => OK

	def getGameSettings(self, gameSettings):
		# State 1: Waiting for game settings
		if not "gameType" in gameSettings: raise UserDidNotSendGameSettings(self.sendMsg, self.name)

		# If player already in a game, remove him from the game
		if self.game: self.game.playerQuitGame(self)

		GamesManager.event("registerPlayer", { "user": self, "gameSettings": gameSettings })

	def userPlay(self, message):
		# State 2: User is playing, send move, get move, display game, quit game ...
		if not "action" in message: raise UserSentInvalidInstruction(self.sendMsg, self.name)

		match message["action"]:
			case "getMove": # User ask for latest opponent move
				# Check if it's user turn, if it is this action is not available
				if self.game.players[self.game.whoPlays] == self: raise UserSentWrongActionDuringHisTurn(self.sendMsg, self.name)

				self.game.event("getMove", { "player": self })

			case "sendMove": # User send move to the game
				if not "move" in message and not message["move"]: raise UserSentInvalidMove(self.sendMsg, self.name)
				
				# Check if it's user turn, if it is not this action is not available
				if self.game.players[self.game.whoPlays] != self: raise UserSentWrongActionDuringOpponentTurn(self.sendMsg, self.name)
				
				# Send move to the game
				self.game.event("sendMove", { "player": self, "move": message["move"] })

			case "displayGame":
				board = str(self.game).encode()
				self.sendMsg({ "state": 1, "boardSize": len(board) })

				# Do not use sendMsg, json parser does not support hex escape sequences (ex: \xe2\x94\x8f\xe2\x94\x81 for ┏━)
				try: self.socket.send(board)
				except ConnectionResetError: raise SocketClosedException()

			case "quitGame":
				if self.game: 
					self.game.playerQuitGame(self)
					self.game = None
				self.sendMsg({ "state": 1 })

				self.state = StateMachine.WAIT_FOR_GAME_SETTINGS
		
			case _:
				self.logger.debug(f"User {self.name} send invalid instruction")
				self.sendMsg({ "state": 0, "reason": "Invalid instruction" }) # INVALID_INSTRUCTION

	def event(self, event: str, data: dict):
		self.queue.put((event, data))

	def destroy(self):
		super().destroy()

		self.game = None
		User.users.remove(self)

		self.socket.close()
		exit()

	def __del__(self):
		self.logger.debug("User object instance have been garbage collected")
