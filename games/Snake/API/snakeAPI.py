"""
* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, T. Gautier
Licence: GPL

File: snakeAPI.py
	A python API for the game Snake

Copyright 2019 T. Hilaire, T. Gautier
"""

from clientAPI import ClientAPI
from clientAPI import NORMAL_MOVE, WINNING_MOVE, LOOSING_MOVE


class SnakeClient(ClientAPI):
	"""API for the Snake game
	the available methods are:
	- waitForSnakeGame: wait for a given game
	- getSnakeArena: get the list of walls in the arena (and who starts)
	- getMove: get the opponent move
	- senbMove: play a move
	- printArena: print the arena
	- sendComment

	A SnakeClient object should be used as:
	with snakeClient( serverName, port, programName) as s:
		 s.waitForSnakeGame( game)
		 ....
		 ....
		 s.getMove()
		 ...
		 ...

	"""
	def waitForSnakeGame(self, gameType):
		"""Wait for the arena
		Returns a tuple (gameName, sizeX, sizeY, nbWalls)
		- gameName: (string) name of the game
		- sizeX, siizeY: (int) size of the arena
		- nbWalls: (int) number of walls
		"""
		gameName, data = self.waitForGame(gameType)
		sizeX, sizeY, nbWalls = [int(x) for x in data.split(" ")]
		return gameName, sizeX, sizeY, nbWalls


	def getSnakeArena(self):
		"""Get the snake arena
		Returns the tuple (walls,whoStarts):
		- walls: list of tuples (x1,y1,x2,y2) for a wall between the coordinate (x1,y1) and (x2,y2)
		- whoStarts: (int) indicates who starts:  0 if you begin, or 1 if the opponent begins
		"""
		data, whoStarts = self.getGameData()
		walls = [int(wall) for wall in data.split()]
		return walls, whoStarts


	def getMove(self):
		"""Get the opponent move
		Returns the status of the move
			- NORMAL_MOVE for normal move,
            - WINNING_MOVE for a winning move, -1
            - LOOSING_MOVE for a losing (or illegal) move
        this code is relative to the opponent (WINNING_MOVE if HE wins, ...)
		"""
		move, ret = self.getCGSMove()
		self._logger.info("move: %s, ret: %s", (move, ret))
		return int(move), int(ret)


	def sendMove(self, move):
		"""Send our  move
		Returns the status of the move
			- NORMAL_MOVE for normal move,
			- WINNING_MOVE for a winning move, -1
			- LOOSING_MOVE for a losing (or illegal) move
		this code is relative to us (WINNING_MOVE if we wins, ...)
		"""
		self._logger.info("move sent : " + str(move))
		return self.sendCGSMove(str(move))


	def printArena(self):
		"""Display the Game
			in a pretty way (ask the server what to print)"""
		self.printGame()


	def sendComment(self, comment):
		"""Send a comment to the server
		- comment: (string) comment to be sent to the server (max 100 char)"""
		self.sendComment(comment[0:99])
