import os, sys, importlib, logging

from gameRef.exceptions import UndefinedGameException, BadGameFolderStructure, ErrorStartingGame
from gameRef.constants import REQUIRED_FOLDERS

class GameRef():
	game = None
	gameClass = None
	
	@classmethod
	def init(cls, gameName: str):
		# Check if game folder exist
		if not os.path.isdir('../games/%s' % (gameName)):
			raise UndefinedGameException()
		
		# Check if required folders exist
		for folder in REQUIRED_FOLDERS:
			if not os.path.isdir('../games/%s/%s' % (gameName, folder)):
				raise BadGameFolderStructure()

		try:
			sys.path.append('../games/%s/server' % (gameName))

			cls.game = importlib.import_module('%s' % (gameName))
			cls.gameClass = getattr(cls.game, gameName)

			logging.getLogger().debug(f"Game {gameName} imported successfully")
		except ModuleNotFoundError as e:
			logging.getLogger().error(f"Error importing game {gameName}: {e}")
			raise ErrorStartingGame()

		# cls.game.init() # TODO
		
	@classmethod
	def listGames(cls):
		print("Available games are:")

		games = os.listdir('../games')
		for game in games:
			print("-", game)

	@classmethod
	def listAvailableBots(cls):
		print("Available bots are:")

		bots = cls.game.BOTS
		for bot in bots: print("-", bots[bot])