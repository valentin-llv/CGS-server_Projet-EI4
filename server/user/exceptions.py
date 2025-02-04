import logging

class SocketClosedException(Exception):
	def __init__(self):
		logging.getLogger().debug("Socket connection has been closed in middle of communication")
		
class FirstSocketMessageIsNotInt(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} used wrong communication pattern, first socket messge is not an int")
		sendMsg({ "state": 0, "error": "Wrong communication pattern used" })

class MessageTooLong(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} send a message that is too long")
		sendMsg({ "state": 0, "error": "Message is too long" })

class MessageNotInJsonFormat(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} send a message not in json format")
		sendMsg({ "state": 0, "error": "Message is not in json format" })

class InvalidMessageFormat(Exception):
    def __init__(self):
        logging.getLogger().warning("Server trying to send incorrectly formated message to client")

class MessageDoesNotContainName(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} did not send username in first message")
		sendMsg({ "state": 0, "error": "You did not send name in first message" })

class UsernameAlreadyTaken(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} tried to use already taken username")
		sendMsg({ "state": 0, "error": "Username is already used" })

class UserDidNotSendGameSettings(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} did not send game settings during wait for game settings state")
		sendMsg({ "state": 0, "error": "You did not send game settings as second message" })

class InvalidGameSettings(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} send invalid game settings")
		sendMsg({ "state": 0, "error": "Invalid game settings" })

class ReconnectionToSessionFailed(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"Server unable to reconnect user {name} to his session, session not found")
		sendMsg({ "state": 0, "error": "Unable to reconnect to session" })

class UserSentInvalidInstruction(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} sent invalid instruction")
		sendMsg({ "state": 0, "error": "Invalid instruction" })

class UserSentWrongActionDuringHisTurn(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} sent wrong action during his turn")
		sendMsg({ "state": 0, "error": "It's your turn to play !" })

class UserSentInvalidMove(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} did not send valid instruction, invalid move")
		sendMsg({ "state": 0, "error": "Invalid move" })

class UserSentWrongActionDuringOpponentTurn(Exception):
	def __init__(self, sendMsg, name):
		logging.getLogger().debug(f"User {name} sent wrong action during opponent turn")
		sendMsg({ "state": 0, "error": "It's not your turn to play !" })