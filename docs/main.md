# Coding game server - CGS

This project is split into 4 parts:

- the server handling user connections and games management
- multiple games
- a web interface to interact with the server
- a base code in C to act as a client for the server

## Server

The server is coded in Python and uses `sockets` library to handle connections. It then connect users to the supported games based on the game settings they've sent.

Server logic is as follow:

