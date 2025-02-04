import logging

logger = logging.getLogger()

class UndefinedGameException(Exception):
	def __init__(self):
		logger.error("Game name is undefined or incorrectly formatted, please set valid game name as command argument")

class BadGameFolderStructure(Exception):
	def __init__(self):
		logger.error("Game folder structure is invalid, please check game data")
		
class ErrorStartingGame(Exception):
	def __init__(self):
		logger.error("An error occured during game startup")