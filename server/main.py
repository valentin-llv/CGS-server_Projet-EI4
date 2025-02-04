import threading, logging

from argParser.argParser import parseCmdArgs, executeArgs, updateGlobalVars

from logger.constants import LOG_MODE_DEV, LOG_MODE_DEBUG, LOG_MODE_PROD
from logger.logger import configureLogger
from logger.handler import configureFileLogging

from sockets.constants import SERVER_PORT, SERVER_ADR
from sockets.sockets import createSocketServer

from gameRef.gameRef import GameRef
from gameRef.exceptions import UndefinedGameException

from user.user import User

from gamesManager.gamesManager import GamesManager

def main():
	args = parseCmdArgs()
	executeArgs(args)

	# Configure logger
	logLevel: int = LOG_MODE_DEV if args.dev else LOG_MODE_DEBUG if args.debug else LOG_MODE_PROD
	configureLogger(logLevel)

	# Get game name
	gameName: str
	if args.gameName != None: gameName = args.gameName
	else: UndefinedGameException() # Execute logger.error and will exit

	# Configure file logging
	logger = logging.getLogger()
	configureFileLogging(gameName, logLevel, logger)

	# Welcome message
	logger.welcomeMessage()

	# Update global vars
	updateGlobalVars(args)

	# Init game
	GameRef.init(gameName)

	# Create game manager, this runs in a separate thread
	GamesManager.getInstance()

	# Creating socket server, daemon = True to close the thread when the main thread is closed
	threading.Thread(target = createSocketServer, daemon = True, args = [SERVER_ADR, SERVER_PORT]).start()

	# Enter in a loop to keep the server running and register the commands
	loop()

def loop():
	while True:
		command = input("")

		# Available commands are: exit, listGames, listUsers, listRunningGames, listThreads, help, listAvailableBots, analyzeMemory
		if command == "exit":
			break
		elif command == "listGames":
			GameRef.listGames()
		elif command == "listUsers":
			User.listUsers()
		elif command == "listRunningGames":
			GamesManager.getInstance().listRunningGames()
		elif command == "listThreads":
			print(threading.enumerate())
		elif command == "help":
			print("Available commands are: exit, listGames, listUsers, listRunningGames, listThreads, help")
		elif command == "listAvailableBots":
			GameRef.listAvailableBots()
		elif command == "analyzeMemory":
			import objgraph # Required to be installed and Graphviz to be installed
			objgraph.show_backrefs(GamesManager, filename='../sample-backref-graph.png')
		else:
			print("Command not found")

		print(">> ", end = "")

if __name__ == "__main__":
	main()