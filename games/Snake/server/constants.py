"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, T. Gautier
Licence: GPL

File: Constants.py
	Contains the constants of the game Snake
	-> defines the constants used for the client communication

Copyright 2019 T. Hilaire, T. Gautier
"""

from itertools import product
from unicodedata import lookup

# constants defining a move
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

# simple dictionary of x and y offsets
Ddx = {NORTH: 0, SOUTH: 0, EAST: 1, WEST: -1}
Ddy = {NORTH: -1, SOUTH: 1, EAST: 0, WEST: 0}

# Build UTF-8 Box Drawing dictionnary
# from the neighboorhood, it associates the corresponding box caracter
# see https://www.utf8-chartable.de/unicode-utf8-table.pl?start=9472&unicodeinhtml=dec
# DRAWING_BOX is a dictionary with 4 booleans (North, East, South, West) as input
DRAWING_BOX = {(False, False, False, False): ' '}
HORIZONTAL = {(True, True): "HORIZONTAL", (False, True): "LEFT", (True, False): "RIGHT"}
VERTICAL = {(True, True): "VERTICAL", (False, True): "DOWN", (True, False): "UP"}
for n, e, s, w in product([False, True], [False, True], [False, True], [False, True]):
	# build the list of parameters
	d = []
	if (n, s) in VERTICAL:
		d.append(VERTICAL[(n, s)])
	if (e, w) in HORIZONTAL:
		d.append(HORIZONTAL[(e, w)])
	if d:
		DRAWING_BOX[(n, e, s, w)] = lookup("BOX DRAWINGS HEAVY " + " AND ".join(d))
HORIZONTAL_BOX = DRAWING_BOX[(False, True, False, True)]
VERTICAL_BOX = DRAWING_BOX[(True, False, True, False)]
BOX = "\N{BLACK SQUARE}"    # FULL BLOCK
TRIANGLES = [lookup("BLACK %s-POINTING TRIANGLE" % s) for s in ("UP", "RIGHT", "DOWN", "LEFT")]
