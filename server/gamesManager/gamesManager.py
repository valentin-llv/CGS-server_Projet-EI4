from __future__ import annotations
from typing import TYPE_CHECKING

import logging, threading
from queue import Queue

if TYPE_CHECKING:
    from user.user import User
    from game.game import Game

from gamesManager.exceptions import InvalidBotName, InvalidGameSettings, PlayerReconnectFailed
from gamesManager.typing import GameSettings
from gamesManager.constants import gameTypes

from gameRef.gameRef import GameRef

class GamesManager:
    _instance = None

    @classmethod
    def getInstance(cls):
        if not cls._instance: threading.Thread(target = cls, daemon = True).start()
        return cls._instance
        
    def __init__(self):
        self.__class__._instance = self

        self.queue = Queue()

        self.games: list[Game] = []
        self.gameUidsCounter = 0

        self.waitingPool: list[User] = []

        self.logger = logging.getLogger()

        self.loop()

    def loop(self):
        while True:
            event, data = self.queue.get()

            if event == "registerPlayer":
                try: data["user"].event("joinedGame", {"game": self.registerPlayer(data["user"], data["gameSettings"])})
                except InvalidBotName: data["user"].event("invalidBotName", {})
                except InvalidGameSettings: pass # TODO
                except PlayerReconnectFailed: data["user"].event("playerReconnectFailed", {})
            else: self.logger.message(f"Unknown event {event}")

    def registerPlayer(self, user: User, gameSettings: GameSettings):
        # If user wants to reconnect, try reconnecting to his session
        if int(gameSettings["reconnect"]): return self.reconnectUser(user)
        else: # Check if user is already in a game, if so remove him from the game
            for game in self.games:
                for i in range(0, len(game.players)):
                    if game.players[i].name == user.name:
                        game.event("playerQuitGame", { "player": user })
                        break

        # TODO check game settings validity

        match int(gameSettings["gameType"]):
            case gameTypes.TRAINING:
                # Create new game session in training mode, need bot name
                try: bot = GameRef.game.BOTS[int(gameSettings["botId"])]() # Instantiate bot
                except KeyError: raise InvalidBotName()
                
                botName = gameSettings["botId"]
                self.logger.message(f"Arrived in trainning with selected bot {botName}")

                # In training mode, user can choose who starts
                starter = 0 if int(gameSettings["starter"]) == 2 else (1 if int(gameSettings["starter"]) == 1 else None)

                # Creating new game
                newGame = GameRef.gameClass(user, bot, self.gameUidsCounter, start = starter, seed = int(gameSettings["seed"]), difficulty = int(gameSettings["difficulty"]))
                newGame.start()

                # Register the game to the bot
                bot.registerGame(newGame)

                # Add game to the list and assign an uid
                self.games.append(newGame)
                self.gameUidsCounter += 1

                return newGame

            case gameTypes.MATCH: pass
            case gameTypes.TOURNAMENT: pass

            case _: raise InvalidGameSettings(user)
            
    def reconnectUser(self, user: User):
        userGame = False

        for game in self.games:
            for i in range(0, len(game.players)):
                if game.players[i].name == user.name:
                    userGame = game
                    game.event("reconnectPlayer", { "player": user, "index": i })

                    break
                
        if userGame != False: 
            self.logger.message(f"User {user.name} was reconnected to his session")
            return userGame
        else: raise PlayerReconnectFailed()
        
    def listRunningGames(self):
        print("Running games:")
        for game in self.games:
            print(f"Game {game.id}: {game.players[0].name} vs {game.players[1].name}")
    
    def deleteGame(self, game: Game):
        self.games.remove(game)

    @classmethod
    def event(cls, event: str, data: dict):
        cls._instance.queue.put_nowait((event, data))