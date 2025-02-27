import socket

# Socket server
try:
    SERVER_ADR = socket.gethostbyname(socket.gethostname())
except socket.gaierror:
    SERVER_ADR = '127.0.0.1'


#SERVER_ADR = "0.0.0.0"
SERVER_PORT = 15001