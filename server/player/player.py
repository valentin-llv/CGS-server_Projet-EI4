import logging

class Player:
    players = []
    uidsCounter = 0

    def __init__(self):
        Player.players.append(self)

        self.id: int = Player.uidsCounter
        Player.uidsCounter += 1
        
    def destroy(self):
        Player.players.remove(self)

    def __del__(self):
        logging.getLogger().debug("Player object instance have been garbage collected")