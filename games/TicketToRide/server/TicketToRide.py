"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire
Licence: GPL

File: TicketToRide.py
	Contains the class TicketToRide
	-> defines the Ticket To Ride game (its rules, moves, etc.)

Copyright 2020 T. Hilaire
"""

import sys, importlib

# Add the CGS server directory to the path
sys.path.append("../../../server/")

# Import files
Game = importlib.import_module("game.game").Game
constants = importlib.import_module("game.constants")

Bot = importlib.import_module("player.bot.bot").Bot

# Assign constants
NORMAL_MOVE = constants.NORMAL_MOVE
LOSING_MOVE = constants.LOSING_MOVE
WINNING_MOVE = constants.WINNING_MOVE

# Import bot players
from bot.NiceBot import NiceBot

BOTS = { 0x1: NiceBot }

from re import compile
from colorama import Style
from random import shuffle, choice
from itertools import zip_longest
from Map import Map, longestPath
from Cards import Deck, strCards
from Constants import colorNames, tracksColors, MULTICOLOR, PURPLE, Scores, playerColors, checkChar

class MoveNames:
	CLAIM_ROUTE = "1"
	DRAW_BLIND_CARD = "2"
	DRAW_CARD = "3"
	DRAW_OBJECTIVES = "4"
	CHOOSE_OBJECTIVES = "5"

class TicketToRide(Game):
	"""
	class TicketToRide (Ticket To Ride)

	Inherits from Game
	- players: tuple of the two players
	- _logger: logger to use to log infos, debug, ...
	- _name: name of the game
	- whoPlays: number of the player who should play now (0 or 1)
	- _waitingPlayer: Event used to wait for the players
	- _lastMove, _last_return_code: string and returning code corresponding to the last move

	Add some properties
	- _theMap: Map object (only used to build the object or get initial data)
	- _deck: the train cards deck (a Deck object, with all the methods to get cards, shuffle, etc.)
	- _cards: cards[pl] is the list of cards of the player pl.
	            _cards[pl][i] gives how many cards of colors i the player pl has
	- _score, _nbWagons: a 2-element list with the score and number of wagons for each player
	- _objectivesDeck: list of objectives cards in the deck (an objective card is 3-uplet city1;city2;points)
	- _objectives: list of objectives of each player (a 2-element list)
	"""

	# create all the maps (each game will have a reference to its map)
	maps = {m: Map(m) for m in ('USA', 'small', 'Europe')}

	def __init__(self, player1, player2, id, **options):
		Game.__init__(self, player1, player2, id, **options)

		"""
		Create a game
		:param player1: 1st Player
		:param player2: 2nd Player
		:param options: dictionary of options (the options 'seed' and 'timeout' are managed by the Game class)
		"""

		self.name = "Ticket to Ride"

		# get the map
		if 'map' not in options:
			options['map'] = 'USA'
		try:
			self._theMap = self.maps[options['map']]
		except KeyError:
			raise ValueError(
				"The option `map` is incorrect (%s instead of being in [%s])"
				% (options['map'], list(self.maps.keys())))
		self._mapTxt = self._theMap.rawtxt

		# initialize the deck and give 4 cards per player
		self._deck = Deck()                 # deck of train cards
		self._cards = [[0]*10, [0]*10]        # self._cards[pl][c] gives how many cards c the player pl has
		for pl in range(2):
			for _ in range(4):
				self._cards[pl][self._deck.drawBlind()] += 1

		# score and wagons
		self._score = [0, 0]
		self._nbWagons = [self._theMap.nbWagons, self._theMap.nbWagons]

		# objectives
		self._objectivesDeck = self._theMap.objectives      # get a copy of the list of objectives
		shuffle(self._objectivesDeck)
		self._objectives = [[], []]
		self._objDrawn = []     # list of drawn objectives (3 objectives kept between drawObjective and chooseObjective)

		self._shouldTakeAnotherCard = False      # True if the player has taken a card and MUST take another one

		# tracks
		self._tracks = self._theMap.tracks      # get a copy of the tracks in a dictionary (city1, city2): Track
		self._taken = []

		# manage the 1st round
		self._firstMove = [True, False]

		# manage the last round
		self._lastRound = 3      # == 0 for the very last move

		# actions that happened on last move, will be sent to the web client
		self._lastMoveWeb = {}

		self.width = 0
		self.height = 0

		self.logger.debug("FaceUp= " + " ".join(str(c) for c in self._deck.faceUp))
		self.logger.debug("Init cards = " + str(self._cards))

	def getBoard(self):
		return self.getData(self.players[0]) # TODO do not set player

	def HTMLrepr(self):
		"""Returns an HTML representation of your game"""
		# this, or something you want...
		return "<A href='/game/%s'>%s</A>" % (self.name, self.name)

	def getDictInformations(self, firstTime=False):
		"""
		Returns a dictionary for HTML display
		- firstTime is True when this is called for the 1st time by a websocket
		:return:
		"""
		data = {'players': [{
				"name": self.players[pl].name,
				"wagons": self._nbWagons[pl],
				"score": self._score[pl],
				"nbCards": sum(self._cards[pl]),
				"objectives": len(self._objectives[pl])
				} for pl in range(2)]
		}
		if firstTime:
			data["map_name"] = self._theMap.name
			data["map_image"] = self._theMap.imagePath
			# data["rectangles"] = [tr.imagePos for tr in self._tracks.values()]
			for pl in range(2):
				data["players"][pl]["tracks"] = [tr.imagePos for tr in self._taken if tr.isTakenBy(pl)]
			data["faceUp"] = self._deck.faceUp

		# add info from the last move
		data.update(self._lastMoveWeb)

		# add comments
		data['comments'] = self._comments.getString(2, [p.name for p in self.players], html=True)

		return data

	def __str__(self):
		"""
		Convert a Game into string (to be send to clients, and display)
		"""
		# map lines
		mapLines = ["".join(line) for line in self._mapTxt]

		# score lines
		scoreLines = [
			"\t\tGame: " + self.name, '',
			"\t\tCards: " + " ".join(strCards(c, c) for c in self._deck.faceUp),
			'', ''
		]
		for i, pl in enumerate(self.players):
			br = "[]" if self.whoPlays == i else "  "
			scoreLines.append(
				"\t\t" + br[0] + playerColors[i] + "Player " + str(i + 1) + ": " + pl.name + Style.RESET_ALL + br[1]
			)
			scoreLines.append(
				"\t\t Score: %3d \t Wagons: %2d \t Objectives: %d" %
				(self._score[i], self._nbWagons[i], len(self._objectives[i]))
			)
			if not isinstance(self.players[i], Bot) and isinstance(self.players[1-i], Bot):
				scoreLines.append("\t\t Cards (%2d): " % sum(self._cards[i]))
				for c, (name, color) in enumerate(zip(colorNames[1:], tracksColors[1:])):
					scoreLines.append("\t\t\t - (%d) %10s:%s" % (c+1, name, strCards(c+1, self._cards[i][c+1])))
			else:
				scoreLines.append("\t\t Cards (%2d)" % sum(self._cards[i]))

			scoreLines.append("")

		# assembly
		res = list(mapLines[:5])
		res.extend([l1+l2 for l1, l2 in zip_longest(
			mapLines[5:], scoreLines, fillvalue=' '*len(res[0]) if len(scoreLines) > len(mapLines) else ''
		)])
		return "\n".join(res)


	def updateGame(self, move):
		"""
		update the game by playing a move
		- move: a string
		Return a tuple (move_code, msg), where
		- move_code: (integer) 0 if the game continues after this move, >0 if it's a winning move, -1 otherwise (illegal move)
		- msg: a message to send to the player, explaining why the game is ending
		"""
		# reset move action
		self._lastMoveWeb = {}

		regClaimRoute = compile(r"^\s*1\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")   # regex to parse a "1 %d %d %d %d"
		regDrawBlindCard = compile(r"^\s*2")                                # regex to parse "2"
		regDrawCard = compile(r"^\s*3\s+(\d+)")                             # regex to parse "3 %d"
		regDrawObjectives = compile(r"^\s*4")                               # regex to parse "4"
		regChooseObjectives = compile(r"^\s*5\s+(\d+)\s+(\d+)\s+(\d+)")     # regex to parse "5 %d %d %d"

		# print("Move: ", move)

		# # parse for the different moves
		# match move["move"]:
		# 	case MoveNames.CLAIM_ROUTE:
		# 		answer = self._claimRoute(move)
		# 	case MoveNames.DRAW_BLIND_CARD:
		# 		answer = self._drawBlindCard()
		# 	case MoveNames.DRAW_CARD:
		# 		answer = self._drawCard(move)
		# 	case MoveNames.DRAW_OBJECTIVES:
		# 		answer = self._drawObjectives()
		# 	case MoveNames.CHOOSE_OBJECTIVES:
		# 		answer = self._chooseObjectives(move)
		# 	case _:
		# 		return LOSING_MOVE, "The move is not correct!"

		claimRoute = regClaimRoute.match(move)
		drawBlindCard = regDrawBlindCard.match(move)
		drawCard = regDrawCard.match(move)
		drawObjectives = regDrawObjectives.match(move)
		chooseObjectives = regChooseObjectives.match(move)
		# if the last move was drawObjectives, then this move MUST be chooseObjectives
		if self._objDrawn and not chooseObjectives:
			return LOSING_MOVE, "a `draw objectives` move must be followed by a `choose objectives` move"
		# if the last move was drawCard and the card was not a Locomotive, then this move MUST be drawCard or drawBlindCard
		if self._shouldTakeAnotherCard and not (drawCard or drawBlindCard):
			return LOSING_MOVE, "a `draw card` or `draw blind card` must be followed by a `draw card` " \
			                    "or `draw blind card` (except for Locomotive taken face up)"
		# the 1st move MUST be chooseObjectives
		if self._firstMove[self.whoPlays] and not drawObjectives:
			return LOSING_MOVE, "The 1st move MUST be a `draw objective` move!"
		# Claim a route
		if claimRoute:
			answer = self._claimRoute(claimRoute)
		# Draw a blind card
		elif drawBlindCard:
			answer = self._drawBlindCard()
		# Draw a train card
		elif drawCard:
			answer = self._drawCard(drawCard)
		# Draw an objective card
		elif drawObjectives:
			answer = self._drawObjectives()
		# Choose an objective card
		elif chooseObjectives:
			answer = self._chooseObjectives(chooseObjectives)
		# otherwise, an incorrect move
		else:
			return LOSING_MOVE, "The move is not in correct !"

		# end of the 1st round
		self._firstMove[self.whoPlays] = False

		# check the end of the game
		if self._lastRound < 3 and not (self._shouldTakeAnotherCard or self._objDrawn):
			self._lastRound -= 1
		if self._lastRound < 0:
			# check how has won !
			return self.whoWins()

		return answer

	def getDataSize(self):
		"""
		Returns the size of the datas send by getData
		(for example sizes of arrays, so that the arrays could be allocated before calling getData)
		"""
		# send the number of cities and the number of tracks
		return "%d %d" % (self._theMap.nbCities, self._theMap.nbTracks)



	def getData(self, player):
		"""
		Return the datas of the game (when ask with the GET_GAME_DATA message) asked by player `player`
		ie the map data, the face up cards and the 4 initial cards (for each player)
		"""
		# get the list of the cards
		pl = 0 if player == self.players[0] else 1     # index of the player
		cards = []
		for i, c in enumerate(self._cards[pl]):
			if c > 0:
				for _ in range(c):
					cards.append(str(i))

		# send the cities, the face-up cards and the player cards
		return self._theMap.data + " " + " ".join(str(c) for c in self._deck.faceUp) + " " + " ".join(cards)


	def getNextPlayer(self):
		"""
		Change the player who plays

		Returns the next player (but do not update self.whoPlays)
		"""
		# in case of `draw objective` move, the player replay
		return self.whoPlays if (self._shouldTakeAnotherCard or self._objDrawn) else 1 - self.whoPlays

	def faceUpCards(self):
		"""Return the list of face up cards (for the bots)"""
		return list(self._deck.faceUp)

	def whoWins(self):
		"""called at the end of the game
		Determines who wins, and returns the information required by updateGame
		- counts the objectives
		- counts the longest path"""
		msg = ['']
		# count the objectives for every player
		for pl in [0, 1]:
			msg.append(self.players[pl].name + ":")
			for obj in self._objectives[pl]:
				done = obj.check(self._tracks, pl)
				self._score[pl] += +obj.score if done else -obj.score
				msg.append("\t" + checkChar[done] + "Objective %s (%d) \U00002192 %s (%d) : %s%d points" % (
					self._theMap.getCityName(obj.city1), obj.city1,
					self._theMap.getCityName(obj.city2), obj.city2,
					'+' if done else '-',
					obj.score
				))

		# longest path (10 points)
		long = [0, 0]
		for pl in [0, 1]:
			long[pl] = longestPath([tr for tr in self._tracks.values() if tr.isTakenBy(pl)])
		if long[0] > long[1]:
			self._score[0] += 10
			msg.append("Player %s has the longest path (%d vs %d)" % (self.players[0].name, long[0], long[1]))
		elif long[1] > long[0]:
			self._score[1] += 10
			msg.append("Player %s has the longest path (%d vs %d)" % (self.players[1].name, long[1], long[0]))
		else:
			self._score[0] += 10
			self._score[1] += 10
			msg.append("Both players has the longest path (%d wagons)" % long[0])
		# total score
		msg.append("Total score: \t%s: %dpts\t%s: %dpts" %
		           (self.players[0].name, self._score[0], self.players[1].name, self._score[1]))
		msg.append("")
		# determine who wins
		if self._score[self.whoPlays] > self._score[1-self.whoPlays]:
			return WINNING_MOVE, "\n".join(msg)
		elif self._score[self.whoPlays] < self._score[1-self.whoPlays]:
			return LOSING_MOVE, "\n".join(msg)
		else:
			# equality, check the longest path
			if long[self.whoPlays] > long[1-self.whoPlays]:
				msg.append("Equality, but %s has longest path %s" %
				           (self.players[self.whoPlays].name, self.players[1-self.whoPlays].name))
				return WINNING_MOVE, "\n".join(msg)
			if long[1-self.whoPlays] > long[self.whoPlays]:
				msg.append("Equality, but %s has longest path %s" %
				           (self.players[1-self.whoPlays].name, self.players[self.whoPlays].name))
				return LOSING_MOVE, "\n".join(msg)
			# equality, check the number of objectives
			else:
				msg.append("Same longest path")
				if len(self._objectives[self.whoPlays]) > len(self._objectives[1-self.whoPlays]):
					msg.append("Equality, but %s has more objective cards than %s" %
					           (self.players[self.whoPlays].name, self.players[1-self.whoPlays].name))
					return WINNING_MOVE, "\n".join(msg)
				elif len(self._objectives[self.whoPlays]) < len(self._objectives[1-self.whoPlays]):
					msg.append("Equality, but %s has more objective cards than %s" %
					           (self.players[1-self.whoPlays].name, self.players[self.whoPlays].name))
					return LOSING_MOVE, "\n".join(msg)
				else:
					msg.append("Same number of objective cards")
					# equality, check the number of cards
					if sum(self._cards[self.whoPlays]) < sum(self._cards[1 - self.whoPlays]):
						msg.append("Equality, but %s has less wagon cards than %s" %
						           (self.players[self.whoPlays].name, self.players[1 - self.whoPlays].name))
						return WINNING_MOVE, "\n".join(msg)
					elif sum(self._cards[self.whoPlays]) > sum(self._cards[1 - self.whoPlays]):
						msg.append("Equality, but %s has less wagon cards than %s" %
						           (self.players[1 - self.whoPlays].name, self.players[self.whoPlays].name))
						return LOSING_MOVE, "\n".join(msg)
					else:
						# flip a coin
						msg.append("Same number of wagon cards")
						winner = choice([0, 1])
						if winner == self.whoPlays:
							msg.append("Coin tossing: %s wins" % self.players[self.whoPlays].name)
							return WINNING_MOVE, "\n".join(msg)
						else:
							msg.append("Coin tossing: %s wins" % self.players[1-self.whoPlays].name)
							return LOSING_MOVE, "\n".join(msg)




	def _chooseObjectives(self, move):
		"""play a `choose objectives` move
		called by updateGame"""
		if not self._objDrawn:
			return LOSING_MOVE, "`Choose Objectives` is not preceded by `Draw Objectives`"
		objs = [int(move.group(1)), int(move.group(2)), int(move.group(3))]
		# check if at least one objective is taken
		nbObjectives = sum([1 if o else 0 for o in objs])
		if nbObjectives == 0:
			return LOSING_MOVE, "None objective has been kept"
		# check that at least 2 objectives are kept for the 1st move
		if len(self._objectives[self.whoPlays])==0 and nbObjectives < 2:
			return LOSING_MOVE, "At least two objectives should be taken for the 1st time"
		# put the chosen objectives in the player hand, or back in the objective deck
		for i in range(3):
			if objs[i]:
				self._objectives[self.whoPlays].append(self._objDrawn[i])
			else:
				self._objectivesDeck.append(self._objDrawn[i])
		self._objDrawn = []
		# message for web client
		self._lastMoveWeb = {
			'move': 'Player %s take a %d objective cards' % (self.players[self.whoPlays].name, len([o for o in objs if o]))
		}
		# returns the number of chosen objectives
		return NORMAL_MOVE, str(len([o for o in objs if o]))


	def _drawObjectives(self):
		"""play a `draw objective` move
		called by updateGame"""
		# check if there are some objectives left
		if len(self._objectivesDeck) < 3:
			if len(self._objectives[self.whoPlays]) > len(self._objectives[1 - self.whoPlays]):
				return LOSING_MOVE, "No more available objective cards !!"
			else:
				return WINNING_MOVE, "No more available objective cards !!"
		# get the 3 objective cards
		self._objDrawn = [self._objectivesDeck.pop() for _ in range(3)]
		return NORMAL_MOVE, " ".join(str(c) for c in self._objDrawn)


	def _drawCard(self, move):
		"""play a `draw Card` move
		called by updateGame"""
		# get a card from the face up cards (end of the game if the deck is empty, or the card doesn't exist)
		# get the card position
		card = int(move.group(1))
		try:
			nC = self._deck.faceUp.index(card)
		except ValueError:
			return LOSING_MOVE, "The card doesn't exist in the face up cards"
		# replace it by one in the deck
		try:
			if self._deck.drawFaceUpCard(nC):
				self.sendComment(self.players[self.whoPlays], "Choo choo, three locomotives... New face up cards !")
		except ValueError:
			return (LOSING_MOVE if sum(self._cards[self.whoPlays]) >= sum(
				self._cards[1 - self.whoPlays]) else WINNING_MOVE), "No more cards in the deck !!"
		# check if the player can take a Locomotive
		if self._shouldTakeAnotherCard and card == MULTICOLOR:
			return LOSING_MOVE, "You cannot take a Locomotive as 2nd drawn card"
		# add it in the hand
		self._cards[self.whoPlays][card] += 1
		# if it's not a Locomotive, the player MUST take another one
		if card != MULTICOLOR:
			self._shouldTakeAnotherCard = not self._shouldTakeAnotherCard
		deck = " ".join(str(c) for c in self._deck.faceUp)
		# message for web client
		self._lastMoveWeb = {
			'faceUp': self._deck.faceUp,
			'move': 'Player %s take a %s card' % (self.players[self.whoPlays].name, colorNames[card])
		}
		# send:
		# - to the player: the deck
		# - to the opponent: if the player replay, the card taken and the deck
		return NORMAL_MOVE, deck


	def _drawBlindCard(self):
		"""Play a `draw blind card` move
		called by upgradeGame"""
		pl = self.whoPlays
		# get a card from the deck (end of the game if the deck is empty)
		try:
			draw = self._deck.drawBlind()
			self._cards[pl][draw] += 1
		except ValueError:
			if sum(self._cards[pl]) >= sum(self._cards[1 - pl]):
				return LOSING_MOVE,  "No more cards in the deck !!"
			else:
				return WINNING_MOVE, "No more cards in the deck !!"
		self._shouldTakeAnotherCard = not self._shouldTakeAnotherCard  # need/no need to take another card
		# message for web client
		self._lastMoveWeb = {'move': 'Player %s take a blind card' % self.players[self.whoPlays].name}
		# send:
		# - to the player: card drawn
		# - to the opponent: if the player replay
		return NORMAL_MOVE, str(draw)


	def _claimRoute(self, move):
		"""play a `claim a route` move
		called by upgradeGame"""
		# get the values
		city1 = min(int(move.group(1)), int(move.group(2)))
		city2 = max(int(move.group(1)), int(move.group(2)))
		card = int(move.group(3))
		nbLoco = int(move.group(4))
		if not ((0 <= city1 < self._theMap.nbCities) and (0 <= city2 < self._theMap.nbCities)
		        and (PURPLE <= card <= MULTICOLOR) and (0 <= nbLoco)):
			return LOSING_MOVE, "The data given to claim a city are incorrect (%s)" % move.string
		msg = "he track between %s (%d) and %s (%d)" % \
		      (self._theMap.getCityName(city1), city1, self._theMap.getCityName(city2), city2)
		# check if the road exists
		if (city1, city2) not in self._tracks:
			return LOSING_MOVE, "T" + msg + " doesn't exist"
		tr = self._tracks[(city1, city2)]
		# check if the player can claim it
		if tr.isTaken:
			return LOSING_MOVE, "T" + msg + " is already taken"
		if self._cards[self.whoPlays][MULTICOLOR] < nbLoco:
			return LOSING_MOVE, "The players doesn't have enough Locomotives (%d required, %d in the hand)" % \
			                    (nbLoco, self._cards[self.whoPlays][MULTICOLOR])
		if not tr.checkCards(card, self._cards[self.whoPlays][card], nbLoco):
			return LOSING_MOVE, "The cards given for t" + msg + " are incorrect"
		# check the number of wagons
		if self._nbWagons[self.whoPlays] < tr.length:
			return LOSING_MOVE, "You don't have enough wagons left!"
		# remove the cards
		self._cards[self.whoPlays][MULTICOLOR] -= nbLoco
		self._cards[self.whoPlays][card] -= (tr.length - nbLoco)
		if self._cards[self.whoPlays][MULTICOLOR] < 0 or self._cards[self.whoPlays][card] < 0:
			return LOSING_MOVE, "You don't have enough card to claim the route!"
		for i in range(nbLoco):
			self._deck.discard(MULTICOLOR)
		for i in range(tr.length - nbLoco):
			self._deck.discard(card)
		# take the track
		tr.claims(self.whoPlays)
		self._taken.append(tr)
		# update the score
		self._score[self.whoPlays] += Scores[tr.length]
		self._nbWagons[self.whoPlays] -= tr.length
		# update the txt map
		tr.draw(self._mapTxt)
		# check for the last turn
		if self._nbWagons[self.whoPlays] < 3 and self._lastRound > 2:
			self._lastRound = 2

		# message for web client
		self._lastMoveWeb = {
			'track': [tr.imagePos, self.whoPlays],
			'move': "Player %s takes the road %s \U00002192 %s<br/> (%s, %d locomotives)" % (
				self.players[self.whoPlays].name, self._theMap.getCityName(city1), self._theMap.getCityName(city2), colorNames[card], nbLoco
			)
		}

		# normal move
		return NORMAL_MOVE, ""
