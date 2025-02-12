"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, T. Gautier
Licence: GPL

File: RandomPlayer.py
	Contains the class RandomPlayer
	-> defines a stupid player

Copyright 2019 T. Hilaire, T. Gautier
"""

from random import choice

import sys, importlib

sys.path.append("../../../server/")
Bot = importlib.import_module("player.bot.bot").Bot

from constants import EAST, NORTH, SOUTH, WEST, Ddx, Ddy

class RandomPlayer(Bot):
	"""
	class RandomPlayer

	Inherits from TrainingPlayer
	"""

	def __init__(self, **options):
		"""
		Initialize the Training Player

		There is no options
		"""

		super().__init__()

		self.name = 'RandomPlayer'

	def playMove(self):
		"""
		Returns the move to play (string)
		"""
		# get our player number
		us = 0 if (self.game.players[0] is self) else 1

		# build the list of the possible moves
		moves = []

		# move
		for direction in (NORTH, EAST, SOUTH, WEST):
			# head position and next position
			hx, hy, _ = self.game.playerPos[us][0]
			nx = hx + Ddx[direction]
			ny = hy + Ddy[direction]
			# check if possible
			if not self.game.arena.getWall(hx, hy, direction) and self.game.arena.getPlayer(nx, ny) is None:
				moves.append(str(direction))

		# choose one (up to 4 moves and 4 rotations)
		if moves:
			return choice(moves)
		else:
			# sometimes, we cannot move...
			self.game.sendComment(self, "I am blocked... I cannot move...")
			return "%d" % NORTH


