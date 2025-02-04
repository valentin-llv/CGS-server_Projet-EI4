from __future__ import annotations
from typing import TYPE_CHECKING

import abc, logging

if TYPE_CHECKING:
    from game.game import Game

from player.player import Player

class Bot(Player):
    bots = []
    uidsCounter = 0

    def __init__(self):
        Player.__init__(self)

        Bot.bots.append(self)
        self.botId = Bot.uidsCounter
        Bot.uidsCounter += 1

        self.game = None

    def registerGame(self, game: Game):
        self.game = game

    @abc.abstractmethod
    def playMove(self): pass

    def destroy(self):
        super().destroy()

        self.game = None
        Bot.bots.remove(self)

    def __del__(self):
        logging.getLogger().debug("Bot object instance have been garbage collected")