"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire
Licence: GPL

File: Cards.py
	Contains the class Deck for the TicketToRide game
	-> manipulate deck of train cards
Copyright 2020 T. Hilaire
"""

from colorama import Fore, Back
from random import shuffle
from Constants import MULTICOLOR, PURPLE, tracksColors


def strCards(color, amount):
	"""return a string to display a card (using color)"""
	if color == MULTICOLOR:
		return tracksColors[color] + " (%d)" % amount + Fore.RESET + Back.RESET
	else:
		return tracksColors[color] + " %2d" % amount + Fore.RESET + Back.RESET



class Deck:
	"""class for a deck of train cards"""
	def __init__(self):
		"""build the deck"""
		# 12 cards of Purple, White, Blue, Yellow, Orange, Black, Red, Green and 14 Multicolor
		self._cards = list(range(PURPLE, MULTICOLOR))*12 + [MULTICOLOR]*14
		shuffle(self._cards)
		self._discarded = []
		# distribute 5 cards face up (and prevent having more than 2 Locomotives)
		self._faceUp = [self._cards.pop() for _ in range(5)]    # Five 1st cards face up
		count =0
		while self._faceUp.count(MULTICOLOR) >= 3:
			count += 1
			if count>500:
				return
			# remove the 5 face up cards
			for i in range(5):
				self.discard(i)
			# put some new cards
			self._faceUp = [self._pop() for _ in range(5)]


	def _pop(self):
		"""drawn a card in the deck"""
		if self._cards:
			return self._cards.pop()
		elif self._discarded:
			self._cards = self._discarded
			self._discarded = []
			shuffle(self._cards)
			return self._cards.pop()
		else:
			raise ValueError("No more available cards !!")


	def drawBlind(self):
		"""drawn a card"""
		return self._pop()


	def drawFaceUpCard(self, pos):
		"""draw a face-up card
		pos is an integer between 0 and 4
		Return True if we had 3 Locomotives"""
		ThreeLoco = False
		if not (0 <= pos <= 4):
			raise ValueError("The position (%s) in the face-up cards is invalide" % (pos,))
		# get a card from the deck and put it face up
		card = self._faceUp[pos]
		self._faceUp[pos] = self._pop()
		# check for three Locomotives
		count = 0
		while self._faceUp.count(MULTICOLOR) >= 3:
			count += 1
			if count > 50:
				raise ValueError("Only Locomotives in the deck!")
			ThreeLoco = True
			# remove the 5 face up cards
			for i in range(5):
				self.discard(self._faceUp[i])
			# put some new cards
			self._faceUp = [self._pop() for _ in range(5)]
		return ThreeLoco


	def discard(self, card):
		"""discard a card"""
		self._discarded.append(card)

	@property
	def faceUp(self):
		"""return the 5 face up cards"""
		return self._faceUp
