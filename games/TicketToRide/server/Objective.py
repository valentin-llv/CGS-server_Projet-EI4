"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire
Licence: GPL

File: Map.py
	Contains the class Objective for the TicketToRide game
	-> defines a objective


Copyright 2020 T. Hilaire
"""


class Objective:
	"""Simple class to store an objective"""
	def __init__(self, city1, city2, score):
		"""an objective is composed of two cities and the score"""
		self._city1 = city1
		self._city2 = city2
		self._score = score

	def __str__(self):
		"""return a string usued for communication with client"""
		return "%d %d %d" % (self._city1, self._city2, self._score)

	@property
	def city1(self):
		"""Returns the 1st city"""
		return self._city1

	@property
	def city2(self):
		"""Returns the 2nd city"""
		return self._city2

	@property
	def score(self):
		"""Returns the score of the objective"""
		return self._score


	def check(self, tracksDict, player):
		"""Check if the objective is done by the player
		Returns True if there is a path (for the player) from city1 to city2"""
		# list of tracks taken by the player
		tracks = [tr for tr in tracksDict.values() if tr.isTakenBy(player)]

		# initial set of cities linked to city1
		cities = set()
		s = set()
		remainTracks = []
		for tr in tracks:
			if self._city1 in tr.cities:
				s.update(set(tr.cities))
			else:
				remainTracks.append(tr)
		tracks = remainTracks

		# update to get all the cities we can reach from self.city1
		count = 0
		while s:
			count += 1
			if count>500:
				return False
			cities.update(s)
			s = set()
			remainTracks = []
			for tr in tracks:
				if tr.cities[0] in cities or tr.cities[1] in cities:
					s.update(set(tr.cities))
				else:
					remainTracks.append(tr)
			tracks = remainTracks

		return self._city2 in cities
