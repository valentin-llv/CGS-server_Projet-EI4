"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire
Licence: GPL

File: Constants.py
	Contains the constants of the game Ticket To Ride
	-> defines the constants used for the client communication, the colors and text display

Copyright 2020 T. Hilaire
"""

from colorama import Fore, Back, Style

# definitions of colors
# list of colors
colorNames = ['None', 'Purple', 'White', 'Blue', 'Yellow', 'Orange', 'Black', 'Red', 'Green', 'Multicolor']

# constants
NONE = 0
PURPLE = 1
WHITE = 2
BLUE = 3
YELLOW = 4
ORANGE = 5
BLACK = 6
RED = 7
GREEN = 8
MULTICOLOR = 9

# wagons color
tracksColors = [
	Fore.RESET,
	Fore.MAGENTA,                   # PURPLE
	Fore.LIGHTWHITE_EX,             # White
	Fore.BLUE,                      # Blue
	Fore.LIGHTYELLOW_EX,             # Yellow
	Fore.YELLOW,                    # Orange
	Fore.BLACK,                     # Black
	Fore.LIGHTRED_EX,               # Red
	Fore.GREEN,                     # Green
	Fore.WHITE                      # Multi
]

playerColors = [Style.BRIGHT + Fore.LIGHTBLUE_EX, Style.BRIGHT + Fore.LIGHTRED_EX]

# define the blocks (Simple and double)
BLOCK_S_NS = '\U00002502'     # '┃'
BLOCK_S_EW = '\U00002500'     # '━'
BLOCK_S_NE = '\U00002514'     # '┗'
BLOCK_S_NW = '\U00002518'     # '┛'
BLOCK_S_SE = '\U0000250C'     # '┏'
BLOCK_S_SW = '\U00002510'     # '┓'

BLOCK_D_NS = '\U00002551'     # '║'
BLOCK_D_EW = '\U00002550'     # '═'
BLOCK_D_NE = '\U0000255A'     # '╚'
BLOCK_D_NW = '\U0000255D'     # '╝'
BLOCK_D_SE = '\U00002554'     # '╔'
BLOCK_D_SW = '\U00002557'     # '╗'

BLOCK = '\U00002588'

dcol = {'N':  0, 'S': 0, 'E': 1, 'W': -1}
dlin = {'N': -1, 'S': 1, 'E': 0, 'W':  0}

# define the block to display in function of the current and next direction ('N', 'E', 'S' or 'W')
# for the track
BlockTr = {
	('N', ''): BLOCK_S_NS, ('S', ''): BLOCK_S_NS, ('E', ''): BLOCK_S_EW, ('W', ''): BLOCK_S_EW,
	('N', 'N'): BLOCK_S_NS, ('S', 'S'): BLOCK_S_NS, ('E', 'E'): BLOCK_S_EW, ('W', 'W'): BLOCK_S_EW,
	('N', 'E'): BLOCK_S_SE, ('N', 'W'): BLOCK_S_SW, ('S', 'E'): BLOCK_S_NE, ('S', 'W'): BLOCK_S_NW,
	('E', 'S'): BLOCK_S_SW, ('E', 'N'): BLOCK_S_NW, ('W', 'N'): BLOCK_S_NE, ('W', 'S'): BLOCK_S_SE
}
# for the wagons
BlockWg = {
	('N', ''): BLOCK_D_NS, ('S', ''): BLOCK_D_NS, ('E', ''): BLOCK_D_EW, ('W', ''): BLOCK_D_EW,
	('N', 'N'): BLOCK_D_NS, ('S', 'S'): BLOCK_D_NS, ('E', 'E'): BLOCK_D_EW, ('W', 'W'): BLOCK_D_EW,
	('N', 'E'): BLOCK_D_SE, ('N', 'W'): BLOCK_D_SW, ('S', 'E'): BLOCK_D_NE, ('S', 'W'): BLOCK_D_NW,
	('E', 'S'): BLOCK_D_SW, ('E', 'N'): BLOCK_D_NW, ('W', 'N'): BLOCK_D_NE, ('W', 'S'): BLOCK_D_SE
}

# score for the tracks
Scores = [0, 1, 2, 4, 7, 10, 15, 18, 21]

checkChar = {True: Fore.LIGHTGREEN_EX + '\U00002714' + Fore.RESET, False: Fore.LIGHTRED_EX + '\U00002718' + Fore.RESET}
