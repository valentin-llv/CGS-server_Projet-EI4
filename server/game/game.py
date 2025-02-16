from __future__ import annotations
from typing import TYPE_CHECKING

import random, logging, threading, sys
from threading import Timer
from queue import Queue

if TYPE_CHECKING:
    from player.player import Player

from game.constants import LOSING_MOVE

from player.bot.bot import Bot
from gamesManager.gamesManager import GamesManager

from game.constants import DEFAULT_DIFFICULTY, TURN_TIMEOUT_DEFAULT

class Game(threading.Thread):
    def __init__(self, player1: Player, player2: Player, id: int, **options):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.id = id

        self.active = True
        self.winner = None

        self.players = [player1, player2]

        self.checkOptions(options)

        self.queue = Queue()
        self.logger = logging.getLogger()

        self.timers = []

    def checkOptions(self, options):
        if "start" in options and options["start"] != None: self.whoPlays = options["start"]
        else: self.whoPlays = random.randrange(2)

        if "seed" in options: self.seed = int(options['seed'])
        else: self.seed = random.randint(0, 1000000)

        if "difficulty" in options: self.difficulty = int(options['difficulty'])
        else: self.difficulty = DEFAULT_DIFFICULTY

    def run(self):
        while True:
            event, data = self.queue.get()

            if event == "getMove" or event == "sendMove" or event == "sendComment":
                if self.active:
                    if event == "getMove": self.getMove(data["player"])
                    elif event == "sendMove": self.sendMove(data["player"], data)
                    elif event == "sendComment": self.sendComment(data["player"], data["comment"]) # TODO
                else: data["player"].event("gameEnded", { "winner": self.winner })
            elif event == "getBoardState": self.getBoardStateAction(data["player"])
            elif event == "playerDisconnected": self.playerDisconnected(data["player"])
            elif event == "reconnectPlayer": self.reconnectPlayer(data["player"], data["index"])
            elif event == "playerQuitGame": self.playerQuitGame(data["player"])
            else: self.logger.error(f"Unknown event {event}")

    def getMove(self, player):
        # If player is a bot, force him to play a move
        if isinstance(self.players[self.whoPlays], Bot):
            move: str = self.players[self.whoPlays].playMove()
            result = self.updateGame(move)

            if int(move[0]) == 4:
                move: str = self.players[self.whoPlays].playMove()
                result = self.updateGame(move)

            returnCode, message = result

            player.event("getMoveResponse", { "returnCode": returnCode, "message": message, "move": move })

            if returnCode == LOSING_MOVE: # Game ended, bot lost
                self.active = False
                self.winner = self.players[1] if self.whoPlays == 0 else self.players[0]

            self.nextPlayerTurn()
        else:
            # TODO Real player
            pass

    def sendMove(self, player, moveData):
        # Print moveData move
        print(f"Player {player.name} sent move {moveData}")

        # Convert moveData to string
        # move = " ".join([str(moveData[x]) for x in moveData])

        move = moveData["actionData"]["move"]

        moveString = str(move)

        if int(move) == 5:
            moveString += " " + str(moveData["actionData"]["selectCard"][0]) + " " + str(moveData["actionData"]["selectCard"][1]) + " " + str(moveData["actionData"]["selectCard"][2])
        if int(move) == 1:
            moveString += " " + str(moveData["actionData"]["from"]) + " " + str(moveData["actionData"]["to"]) + " " + str(moveData["actionData"]["color"]) + " " + str(moveData["actionData"]["nbLocomotives"])
        if int(move) == 3:
            moveString += " " + str(moveData["actionData"]["card"])

        print(f"Formatted move string: {moveString}")

        returnCode, message = self.updateGame(moveString)
        player.event("sendMoveResponse", { "returnCode": returnCode, "message": message, "move": moveString })

        if int(str(move)) != 4:
            self.nextPlayerTurn()

        if returnCode == LOSING_MOVE: # Game ended, player lost
            self.active = False
            self.winner = self.players[1] if self.players[0].id == player.id else self.players[0]

    def sendComment(self, player, comment):
        """ TODO
			Called when a player send a comment
		Parameters:
		- player: player who sends the comment
		- comment: (string) comment
		"""

		# # log it
		# self.logger.info("[%s] : '%s'", player.name, comment)
		# for n in (0, 1):
		# 	self.players[n].logger.info("[%s] : %s" % (player.name, comment))

		# # append comment
		# nPlayer = 0 if player is self._players[0] else 1
		# self._comments.append(comment, nPlayer)

        pass

    def getBoardStateAction(self, player):
        boardState = self.getBoardState()

        player.event("getBoardStateResponse", { "boardState": boardState })

    def nextPlayerTurn(self):
        self.whoPlays = 1 if self.whoPlays == 0 else 0

    def playerQuitGame(self, player):
        self.active = False

        # Remove player from game
        self.players.remove(player)

        # If other players are bots, destroy them and close game
        if not self.remaininPlayer(): self.destroy()

    def playerDisconnected(self, player):
        # Timeout to wait for player to reconnect
        timer = Timer(2, self.reconnectTimeout, (player, ))
        timer.setDaemon(True)
        timer.start()

        self.timers.append({ "player": player, "timer": timer })

    def reconnectTimeout(self, player):        
        self.deleteTimer(player)
        self.playerQuitGame(player)

    def reconnectPlayer(self, user, index):
        self.players[index] = user
        self.deleteTimer(user)

    def event(self, event: str, data: dict):
        self.queue.put((event, data))

    def remaininPlayer(self):
        remainPlayers = False
        for p in self.players:
            if not isinstance(p, Bot): remainPlayers = True  

        return remainPlayers
    
    def deleteTimer(self, player):
        for t in self.timers:
            if t["player"] == player:
                t["timer"].cancel()
                self.timers.remove(t)
                break

    def destroy(self):
        for p in self.players: p.destroy()
        self.players = None
        
        self.winner = None
        
        for t in self.timers: 
            t["timer"].cancel()
            t["timer"] = None
            t["player"] = None

        self.queue.queue.clear()
        self.queue = None

        self.active = False

        GamesManager.getInstance().deleteGame(self)
        sys.exit()

    def __del__(self):
        logging.getLogger().debug("Game object instance have been garbage collected")
