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

import sys, importlib

sys.path.append("../../../server/")
Bot = importlib.import_module("player.bot.bot").Bot

from operator import itemgetter
from math import inf as infinity, isinf
from Constants import MULTICOLOR, NONE, Scores


def Dijkstra(tracks, nbCities, city1, city2, opponent):
	"""Returns the tracks to follow from city1 to city2"""
	visited = [False]*nbCities
	distance = [infinity]*nbCities
	prec = [None]*nbCities

	distance[city1] = 0
	prec[city1] = city1
	city = city1

	# repeat until going to city2
	count = 0
	while city != city2:
		count+=1
		if count>500:
			return None
		# get the closest unvisited city
		oldcity = city
		city = min(range(nbCities), key=lambda x: distance[x] if not visited[x] else infinity)
		if oldcity == city and oldcity != city1:
			break
		# update the distance for all the connected cities
		visited[city] = True
		for v in range(nbCities):
			tr = tracks.get((min(city, v), max(city, v)))
			if not visited[v] and tr and not tr.isTakenBy(opponent):
				if distance[v] > distance[city] + (0 if tr.isTaken else tr.length):
					distance[v] = distance[city] + (0 if tr.isTaken else tr.length)
					prec[v] = city

	# check if city2 is at reachable distance
	if isinf(distance[city2]):
		return None

	# return the tracks from city2 to city1
	path = []       # list of tracks to take
	count = 0
	while city != city1:
		count += 1
		if count>500:
			return None
		tr = tracks[(min(city, prec[city]), max(city, prec[city]))]
		if not tr.isTaken:
			path.append(tr)
		city = prec[city]

	return path


class NiceBot(Bot):
	"""
	This class defines a training player that play correctly (tries to finish the objectives)
	"""

	def __init__(self):
		"""Initialize the Training Player
		no options, nothing to do with options
		"""
		super().__init__()
		self._firstRound = True
		self._obj = []
		self._onceAgain = False
		self._tr = None
		self._cards = None
		self._chooseObjectives = False

		self.name = "NiceBot"


	def playMove(self):
		"""
		Plays the move
		Returns the move
		"""
		ourWagons = self.game._nbWagons[0 if (self.game.players[0] is self) else 1]

		# check for 1st and 2nd round (draw Objective and choose Objectives)
		if self._firstRound:
			if self._chooseObjectives:
				# TODO: choose only two or three
				# then keep the three
				self._firstRound = False
				self._chooseObjectives = False
				self._obj = self.game._objectives[0 if (self.game.players[0] is self) else 1]
				return "5 1 1 1"
			else:
				# now we can get the tracks and our cards
				self._tr = self.game._tracks
				self._cards = self.game._cards[0 if (self.game.players[0] is self) else 1]
				# 1st round, take 3 objectives
				self._chooseObjectives = True
				return "4"

		# chek if we have to choose some objectives
		if self._chooseObjectives:
			self._chooseObjectives = False
			# choose those that are already done or almost done (not the best algo)
			nbWagons = [infinity, infinity, infinity]
			for i, obj in enumerate(self.game._objDrawn):
				opp = 1 if (self.game.players[0] is self) else 0
				path = Dijkstra(self._tr, self.game._theMap.nbCities, obj.city1, obj.city2, opp)
				if path is not None:
					nbWagons[i] = sum([t.length for t in path])
				else:
					nbWagons[i] = infinity
			# take all if we can do it
			if sum(nbWagons) < min(self.game._nbWagons):
				return "5 1 1 1"
			else:
				# take only one
				n = min(enumerate(nbWagons), key=itemgetter(1))[0]
				return "5 " + " ".join(['1' if n == i else '0' for i in range(3)])


		# get the list of tracks to take
		tracks = [tr for tr in self.getTracksToTake() if tr.length <= ourWagons]

		# If there are no more interesting tracks to take
		if not tracks and not self._onceAgain:
			# if enough wagons are left, we can take new objectives

			if min(self.game._nbWagons) >= 8:
				self._chooseObjectives = True
				return "4"
			# otherwise, we consider the largest track we can take
			# iterate other the colors sorted by the max of cards
			# and then the tracks sorted by length
			for nb, col in sorted([(nb, col) for col, nb in enumerate(self._cards)], reverse=True):
				for tr in sorted([tr for tr in self._tr.values() if not tr.isTaken and tr.length <= ourWagons], key=lambda x: x.length, reverse=True):
					res = self.canClaim(tr)
					if res:
						self._onceAgain = False
						return "1 %d %d %d %d" % (tr.cities[0], tr.cities[1], res[0], res[1])

		# iterate over all the tracks to take
		for tr in tracks:
			if not self._onceAgain:
				# can we take it
				res = self.canClaim(tr)
				if res:
					self._onceAgain = False
					return "1 %d %d %d %d" % (tr.cities[0], tr.cities[1], res[0], res[1])
			# can we take that color ? (only if we are not in the very last end of the game)
			if min(self.game._nbWagons) > 8:
				for color in tr.iterColors:
					if color != MULTICOLOR and color in self.game.faceUpCards():
						self._onceAgain = (not self._onceAgain) if color != MULTICOLOR else False
						return "3 %d" % (color,)

		if not self._onceAgain and MULTICOLOR in self.game.faceUpCards():
			self._onceAgain = False
			return "3 %d" % (MULTICOLOR,)

		# otherwise we don't now what to do, and take a blind card
		self._onceAgain = not self._onceAgain
		return "2"


	def getTracksToTake(self):
		"""get the list of (tracks, sum of the score) to take
		to achieve the objectives"""
		# get our player number
		us = 0 if (self.game.players[0] is self) else 1

		# for each objective, run Dijkstra algorithm and get the list of tracks to take
		tracks = dict()
		for objective in self._obj:
			path = Dijkstra(self._tr, self.game._theMap.nbCities, objective.city1, objective.city2, 1-us)
			for tr in path:
				# put tr in tracks, and accumulate the objective scores
				tracks[tr] = objective.score + tracks.get(tr, Scores[tr.length])

		# return the tracks sorted by value
		return sorted(tracks, key=lambda x: x.length)       # TOFIX: getitem, or getter add method to compare Track


	def canClaim(self, track):
		"""Check if we can clam the track
		do we have the right number of cards
		Return None if we cannot or a tuple (color, nbLocomotive)"""
		# check the nb of wagons
		if self.game._nbWagons[0 if (self.game.players[0] is self) else 1] < track.length:
			return None
		# if the track is not in gray
		if track.color0 != MULTICOLOR:
			# try with the 1st color of the track
			if self._cards[MULTICOLOR] + self._cards[track.color0] >= track.length:
				return track.color0, max(0, track.length - self._cards[track.color0])
			# try with the 2nd color of the track, if double track
			if track.color1 != NONE:
				if self._cards[MULTICOLOR] + self._cards[track.color1] >= track.length:
					return track.color1, max(0, track.length - self._cards[track.color1])
		else:
			# the track can be taken with any color
			# among the color with enough cards, get one with lowest card
			lc = [(i, self._cards[i]) for i in range(1, MULTICOLOR) if self._cards[i] >= track.length]
			if lc:
				return max(lc, key=itemgetter(1))[0], 0
			# otherwise, try with Locomotives
			lc = [(i, self._cards[i]) for i in range(1, MULTICOLOR) if self._cards[i] > track.length - self._cards[MULTICOLOR]]
			if lc:
				color = max(lc, key=itemgetter(1))[0]
				return color, track.length - self._cards[color]

		# otherwise, this is not possible
		return None

