"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire
Licence: GPL

File: DoNothingPlayer.py
	Contains the class DoNothingPlayer
	-> defines a stupid player that does... nothing (it plays DO_NOTHING every time)

Copyright 2020 T. Hilaire
"""

from random import choice
from CGSserver.Player import TrainingPlayer
from ..Constants import MULTICOLOR, NONE


class PlayRandomPlayer(TrainingPlayer):
	"""
	This class defines a stupid training player that play randomly
	(it get a card from the deck  or the face up card every time)
	It is used for the first part of the project (players need an opponent that does nothing to check their	code)
	"""

	def __init__(self, **_):
		"""Initialize the Training Player
		no options, nothing to do with options
		"""
		super().__init__('PlayRandom')
		self._round = 0
		self._cities = set()
		self._obj = []
		self._onceAgain = False
		self._tr = None


	def playMove(self):
		"""
		Plays the move
		Returns the move
		"""
		if self._tr is None:
			self._tr = list(self.game._tracks.values())    # list of tracks
		# get our player number
		us = 0 if (self.game.players[0] is self) else 1
		if not self._onceAgain:
			# check for 1st or 2nd round
			if self._round == 0:
				# 1st round, take 3 objectives
				self._round = 1
				return "4"
			elif self._round == 1:
				# then keep the three
				self._round = 2
				self._obj = list(self.game._objDrawn)     # FIXME: do it correctly (get back the answer of the move)
				self._cities.update(o.city1 for o in self._obj)
				self._cities.update(o.city2 for o in self._obj)
				return "5 1 1 1"
			# other try to claim a route that starts from one of its cities
			else:
				# list of tracks that goes from the cities (sorted by length)
				tr = [t for c in self._cities for t in self._tr if not t.isTaken and t.length<= self.game._nbWagons[us]]
				tr.sort(key=lambda x: x.length, reverse=True)
				# try to take one that has the same length as the longest
				for t in tr:
					for color in t.iterColors:
						nbCards = self.game._cards[us][color] if color != MULTICOLOR else max(self.game._cards[us])
						if nbCards >= t.length >= (tr[0].length - 1):
							self._cities.add(t.cities[0])
							self._cities.add(t.cities[1])
							if color == MULTICOLOR:
								color = self.game._cards[us].index(nbCards)
							# take it
							return "1 %d %d %d 0" % (t.cities[0], t.cities[1], color)

		# otherwise, take a face up cards that are not a Locomotive
		self._onceAgain = not self._onceAgain
		faceUp = ["3 %d" % c for c in self.game.faceUpCards() if c != MULTICOLOR]
		return choice(["2", choice(faceUp)])

