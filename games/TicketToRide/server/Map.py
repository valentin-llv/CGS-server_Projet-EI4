"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire
Licence: GPL

File: Map.py
	Contains the class Map for the TicketToRide game
	-> defines a map


To create a new map,
a) add its name in the definition of TicketToRide.map (see TicketToRide.py linee 62)
b) create a folder (with the same name as the map) in games/TicketToRide/maps/
c) with the following files
  - cities.csv:     list of cities (number;cityName)
  - tracks.csv:     list of tracks (city1;city2;length;track1 color;track2 color)
  - map.txt:        raw text for the map

Copyright 2020 T. Hilaire
"""

from os.path import join, curdir, splitext
from copy import copy
from yaml import SafeLoader, load
from yamlinclude import YamlIncludeConstructor
from shutil import copyfile
from Track import Track
from Objective import Objective
from City import City

YamlIncludeConstructor.add_to_loader_class(
	loader_class=SafeLoader, base_dir='../games/TicketToRide/maps/'
)


class Map:
	"""One object Map per existing map is created
	The objects are created from the following files in the folder maps:
	- cities.csv    # list of the cities (with coordinates)
	- tracks.csv    # list of the tracks"""

	def __init__(self, name):
		"""create the object from the files"""

		# load the yml file (with possible included files)
		self._name = name

		with open('../games/TicketToRide/maps/' + name + '.yml', encoding="utf8") as ymlFile:
			yml = load(ymlFile, Loader=SafeLoader)

		# build the list of cities
		self._cities = [City(list(city)[0], **list(city.values())[0]) for city in yml['cities']]
		invCities = {c.name: i for i, c in enumerate(self._cities)}

		# open the text map and store it in a 2D array (list of lists)
		with open(join('../games', 'TicketToRide', 'maps', yml['map']['txt']), encoding="utf8") as txtMap:
			self._rawtxt = [list(line[:-1]) for line in txtMap]
		# highlight the cities in the txt
		for c in self._cities:
			c.highlight(self._rawtxt)

		# build the list of tracks
		self._tracks = []
		for cities, data in yml['tracks'].items():
			cities = [invCities[c.strip()] for c in cities.split(',')]
			tr = Track(cities, **data)
			self._tracks.append(tr)
			tr.draw(self._rawtxt)

		# build the list of objectives
		self._objectives = []
		for cities, data in yml['objectives'].items():
			cities = [invCities[c.strip()] for c in cities.split(',')]
			self._objectives.append(Objective(*cities, data))

		# copy the image to server/template/game (because the webserver cannot access elsewhere)
		copyfile(
			join('../games', 'TicketToRide', 'maps', yml['map']['image']),
			join('../games', 'TicketToRide', 'server', 'templates', 'game', 'maps', name + '.jpg')
		)
		self._image = name + splitext(yml['map']['image'])[1]

		# other properties
		self._nbWagons = yml['nbWagons']



		# build (once) the string to send to each client
		self._data = "\n".join([c.name.replace(' ', '_') for c in self._cities] + [str(tr) for tr in self._tracks])


	@property
	def name(self):
		"""Return the name of the map"""
		return self._name

	@property
	def data(self):
		"""Returns the list of cities (with the space replaced by an underscore)
		and the tracks (5 integers by tracks)
		used to transmit the cities to the client"""
		return self._data


	@property
	def nbCities(self):
		"""Returns the number of cities"""
		return len(self._cities)

	def getCityName(self, city):
		"""Return the name of a city"""
		return self._cities[city].name

	@property
	def nbTracks(self):
		"""Returns the number of tracks"""
		return len(self._tracks)

	@property
	def objectives(self):
		"""Return a list of copied objectives"""
		return [copy(o) for o in self._objectives]

	@property
	def rawtxt(self):
		"""Return the raw text"""
		# copy the list of list
		return [list(t) for t in self._rawtxt]

	@property
	def tracks(self):
		"""Return the tracks, a dictionary of the copy of the tracks"""
		# build the dictionary of tracks
		return {t.cities: copy(t) for t in self._tracks}

	@property
	def imagePath(self):
		"""Returns the path of the image"""
		return self._image

	@property
	def nbWagons(self):
		"""Returns the number of wagons"""
		return self._nbWagons



def longestPath(tracks):
	"""tracks: dict of tracks owned by a player"""
	# get the city and how many tracks related to them
	cities = {}
	for t in tracks:
		for i in range(2):
			if t.cities[i] in cities:
				cities[t.cities[i]].append(t)
			else:
				cities[t.cities[i]] = [t]
	# check longest from each city with only one track
	cityEnd = [c for c, tr in cities.items() if len(tr) == 1]
	l = [_longestUnvisited(c, {c: list(track) for c, track in cities.items()}) for c in cityEnd]
	return max(l)
	# return max(_longestUnvisited(c, deepcopy(cities)) for c, tr in cities.items() if len(tr) == 1)


def _longestUnvisited(start, cities):
	"""recursively explore the graph"""
	long = 0

	# explore the route up to a branch
	# (continue the road until we reach a branch)
	count = 0
	while len(cities[start]) == 1:
		count += 1
		if count>500:
			return 0
		# remove the track
		tr = cities[start][0]
		for c in tr.cities:
			cities[c].remove(tr)
		# go to the next city
		start = tr.cities[1] if tr.cities[0] == start else tr.cities[0]
		long += tr.length

	# end of the road or a branch
	if len(cities[start]) == 0:
		return long
	else:
		length = []
		# try each possible branch
		for tr in cities[start]:
			# copy the cities
			cpy = {c: list(track) for c, track in cities.items()}
			# remove the track
			for c in tr.cities:
				cpy[c].remove(tr)
			# go to the next city
			nextCity = tr.cities[1] if tr.cities[0] == start else tr.cities[0]
			# recursively compute the length starting from this new city
			length.append(tr.length + _longestUnvisited(nextCity, cpy))

		return long + max(length)
