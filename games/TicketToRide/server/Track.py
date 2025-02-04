"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire
Licence: GPL

File: Track.py
	Contains the class Track for the TicketToRide game
	-> defines a track


Copyright 2020 T. Hilaire
"""

from itertools import zip_longest
from Constants import NONE, MULTICOLOR, playerColors, tracksColors, colorNames
from Constants import dcol, dlin, BlockWg, BlockTr, BLOCK


class Track:
	"""simple class to store a track"""
	def __init__(self, cities, length, colors, txt, jpg=[], **_):
		"""a track contains the two cities, the length and the colors"""
		self._cities = (min(cities), max(cities))       # index of the two cities
		self._length = length                           # length
		self._pos = tuple(txt[:2])                      # position in the raw twt
		self._path = txt[2]                             # string describing the path in the raw txt
		self._taken = False                             # True if taken by a player
		self._player = 0                                # if taken, it gives the number of the player who have it
		self._jpg = jpg                                 # list of coordinate of the wagons for the web display
		# colors
		colors = colors.split(',')
		if len(colors) == 1:
			col = (colorNames.index(colors[0].strip()), NONE)
		else:
			col = (colorNames.index(colors[0].strip()), colorNames.index(colors[1].strip()))
		self._colors = col

	def __str__(self):
		return "%d %d %d %d %d" % (self._cities[0], self._cities[1], self._length, self._colors[0], self._colors[1])

	@property
	def cities(self):
		"""return the cities"""
		return self._cities

	@property
	def isTaken(self):
		"""returns if the track is already taken"""
		return self._taken

	def isTakenBy(self, player):
		"""Returns True if the track is taken by player"""
		return self._taken and self._player == player

	@property
	def length(self):
		"""Returns the length of the track"""
		return self._length

	@property
	def color0(self):
		"""Returns the 1st color"""
		return self._colors[0]

	@property
	def color1(self):
		"""Returns the 1st color"""
		return self._colors[1]


	def checkCards(self, card, nbCards, nbLocomotives):
		"""check if nbCards of color card, plus nbLocomotives locomotives can be used to claim the track
		Return True if the player can take the card, False otherwise
		HERE is the rule to claim a track (to be modified for Europe map, for example)
		"""
		# if the tracks is MULTICOLOR (ie with any determine color), then the player just needs enough card of its color
		# if the track is not MULTICOLOR, the player need to propose a color that is in the set of possible colors
		# and also he needs just enough card of the color
		if self._colors[0] != MULTICOLOR and card not in self._colors:
			return False
		return (nbLocomotives + nbCards) >= self._length

	def claims(self, player):
		"""Claim the track as taken by the player"""
		self._taken = True
		self._player = player

	@property
	def iterColors(self):
		"""return the color(s)
		generator that returns 1 or 2 colors"""
		yield self._colors[0]
		if self._colors[1] != NONE:
			yield self._colors[1]

	def draw(self, rawtxt):
		"""Draw the path in the raw text"""
		color1 = tracksColors[self._colors[0]]
		color2 = tracksColors[self._colors[1]] if self._colors[1] != 0 else color1
		line, column = self._pos
		i = 0
		for cour, suiv in zip_longest(self._path, self._path[1:], fillvalue=''):
			color = playerColors[self._player] if self._taken else (color1 if i % 2 else color2)
			line += dlin[cour]
			column += dcol[cour]
			# rail character changes if the track is double or is taken
			if self._taken or self._colors[1] != NONE:
				rail = BlockWg[(cour, suiv)]
			else:
				rail = BlockTr[(cour, suiv)]
			middle = BLOCK if self._taken else str(self._length)
			ch = rail if i != int(len(self._path) / 2) else middle      # char to display
			rawtxt[line - 1][column - 1] = color + ch
			i += 1

	@property
	def imagePos(self):
		"""Return the position list for the image"""
		return self._jpg
