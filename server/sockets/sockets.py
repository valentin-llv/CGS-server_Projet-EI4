import socket, threading, logging

from user.user import User

def createSocketServer(adress, port):
	logger = logging.getLogger()
	logger.debug("Starting socket server")

	# Configure socket server
	server: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((adress, port))

	server.listen()
	logger.message(f"Server listen at adress {adress} on port {port}")

	# Wait for new connections
	while True:
		con, adr = server.accept()

		# Create new thread for the user
		threading.Thread(target = User(con).start, daemon = True).start()
		logger.debug(f"New connection from {adr}, totaling to {threading.active_count() - 3} connections")