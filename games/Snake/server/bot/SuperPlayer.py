"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, T. Gautier
Licence: GPL

File: SuperPlayer.py
	Contains the class SuperPlayer
	-> defines a better player than RandomPlayer

Copyright 2019 T. Hilaire, T. Gautier
"""

import sys, importlib

sys.path.append("../../../server/")
Bot = importlib.import_module("player.bot.bot").Bot

from constants import EAST, NORTH, SOUTH, WEST

class SuperPlayer(Bot):
	"""
	class SuperPlayer

	Inherits from TrainingPlayer
	"""

	def __init__(self):
		"""
		Initialize the Training Player

		There is no options
		"""

		super().__init__()

		self.name = 'SuperPlayer'

		self.last_dir = NORTH
		self.counter = 0

	def get_next_pos(self, x, y, dir):
		if dir == NORTH:
			return x, y - 1
		if dir == EAST:
			return x + 1, y
		if dir == SOUTH:
			return x, y + 1
		if dir == WEST:
			return x - 1, y
		return x, y

	def get_score_from_dir(self, dir):
		us = 0 if (self.game.players[0] is self) else 1
		x, y, _ = self.game.playerPos[us][0]

		if self.game.arena.getWall(x, y, dir):
			return 0

		x, y = self.get_next_pos(x, y, dir)

		arena = []
		for i in range(self.game.arena._L):
			arena.append([0] * self.game.arena._H)
		
		score = self.get_score(arena, x, y)

		"""for row in arena:
			print(row)"""

		return score

		
	def get_score(self, arena, x, y):
		if x < 0 or x >= self.game.arena._L or y < 0 or y >= self.game.arena._H:
			return 0
		if arena[x][y] != 0 or self.check_eating(x, y):
			return 0

		arena[x][y] = 1

		res = 0
		if not(self.game.arena.getWall(x, y, NORTH) or self.game.arena.getWall(x, y-1, SOUTH)):
			res += self.get_score(arena, x, y-1)
		if not(self.game.arena.getWall(x, y, EAST) or self.game.arena.getWall(x+1, y, WEST)):
			res += self.get_score(arena, x+1, y)
		if not(self.game.arena.getWall(x, y, SOUTH) or self.game.arena.getWall(x, y+1, NORTH)):
			res += self.get_score(arena, x, y+1)
		if not(self.game.arena.getWall(x, y, WEST) or self.game.arena.getWall(x-1, y, EAST)):
			res += self.get_score(arena, x-1, y)
		
		return res + 1
	
	def check_eating(self, x, y):
		return not(self.game.arena.getPlayer(x, y) is None)

	def playMove(self):
		"""
		Returns the move to play (string)
		"""
		self.counter += 1
		for i in range(4):
			direction = (self.last_dir + i + 1) % 4
			score = self.get_score_from_dir(direction)
			if score > 1.1 * self.counter + 1:
				self.last_dir = direction
				self.game.sendComment(self, "AHAH je vais gagner !!!")
				return "%d" % direction
		self.game.sendComment(self, "OH non !!!")
		self.last_dir = NORTH
		return "%d" % NORTH
