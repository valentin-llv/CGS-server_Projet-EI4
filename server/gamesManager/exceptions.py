import logging

class InvalidGameSettings(Exception):
    def __init__(self, message: str):
        logging.getLogger().debug(message)

class InvalidBotName(Exception):
    def __init__(self): pass

class PlayerReconnectFailed(Exception):
    def __init__(self):
        pass