# just to test the map
# run `python testMap.py mymap.yml`

from sys import argv, exc_info
from yaml import SafeLoader, load
from yamlinclude import YamlIncludeConstructor
from colorama import Fore, Back
from random import choice
from os.path import join, curdir

from games.TicketToRide.server.Track import Track
from games.TicketToRide.server.Constants import colorNames
from games.TicketToRide.server.City import City

YamlIncludeConstructor.add_to_loader_class(loader_class=SafeLoader, base_dir=curdir)


# load the yml file (with possible included files)
with open(argv[1]) as ymlFile:
	yml = load(ymlFile, Loader=SafeLoader)


# build the list of cities
cities = [City(list(city)[0], **list(city.values())[0]) for city in yml['cities']]
invCities = {c.name: i for i, c in enumerate(cities)}

# open the text map and store it in a 2D array (list of lists)
with open(yml['map']['txt']) as txtMap:
	rawtxt = [list(line[:-1]) for line in txtMap]
# highlight the cities in the txt
for c in cities:
	c.highlight(rawtxt)

# build the list of tracks
tracks = []
for cities, data in yml['tracks'].items():
	cities = [invCities[c.strip()] for c in cities.split(',')]
	try:
		tr = Track(cities, **data)
		tracks.append(tr)
		# tr._taken = True
		tr._taken = False
		# tr._taken = choice([False]*10+[True])
		tr._player = choice([0, 1])
		tr.draw(rawtxt)
	except:
		print("Unexpected error:", exc_info())
		print("Error for track %s"% cities)


# display both
with open(yml['map']['txt']) as txtMap:
	for orig, modif in zip(txtMap, rawtxt):
		print(("%-60s" % orig[:-1]) + "".join(modif))
