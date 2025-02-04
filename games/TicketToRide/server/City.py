"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire
Licence: GPL

File: City.py
	Contains the class City for the TicketToRide game
	-> defines a city (stupid class)


Copyright 2020 T. Hilaire
"""

from colorama import Back, Fore

class City:
	"""Simple class for a city
	- name: name of the city
	- txt: position of the city in the raw text: line, column, size
	- jpg: position of the city on the jpg"""
	def __init__(self, name, txt, jpg=[]):
		"""constructor"""
		self._name = name
		self._txt = tuple(txt)
		self._jpg = tuple(jpg)

	@property
	def name(self):
		"""Returns its name"""
		return self._name

	def highlight(self, rawtxt):
		"""Highlights the city in the raw txt
		modify the rawtxt list of lists (of char)"""
		lin, col, size = self._txt
		for dc in range(size):
			rawtxt[lin - 1][col + dc - 1] = Back.LIGHTWHITE_EX + Fore.BLACK + rawtxt[lin - 1][col + dc - 1] + Fore.RESET + Back.RESET
