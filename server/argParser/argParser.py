import argparse, logging

from gameRef.gameRef import GameRef

def parseCmdArgs():
	parser = argparse.ArgumentParser(formatter_class= argparse.RawTextHelpFormatter)
	parser.add_argument("gameName", help = "Name of the game", type = str, nargs = "?")

	parser.add_argument("--listGames", "-lg", help = "List available games\n ", action = "store_true")

	parser.add_argument('--port', '-p', help = "Select port to use for socket server\n ", type = int)

	parser.add_argument("--debug", help = "Debug mode (log and display everything)", action = "store_true")
	parser.add_argument("--dev", help = "Development mode (log everything, display infos, warnings and errors)", action = "store_true")

	return parser.parse_args()

def executeArgs(args):
	if args.listGames: 
		GameRef.listGames()
		exit(0)

def updateGlobalVars(args):
	# Modify constants vars if needed
	global SERVER_PORT
	if args.port != None:
		SERVER_PORT = args.port
		logging.getLogger().debug(f"Port changed to {SERVER_PORT}")