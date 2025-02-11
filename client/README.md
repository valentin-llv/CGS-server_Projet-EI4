# Coding Game Server (CGS) Client

This is the API to allow you to connect to and play games on the Coding Game Server (CGS). The following guide will help you get started with the client API and provide a step-by-step guide on how to connect to the server, send and receive moves, and interact with the game.

Read the [Going Further](#going-further) section to know what you should do next after testing the API and having played a few games manually.

## Table of Contents

1. [General Information](#general-information)
2. [Getting Started](#getting-started)
3. [Step-by-Step Guide](#step-by-step-guide)
4. [Recommendations](#recommendations)
5. [Going Further](#going-further)

## General Information

The CGS client API is designed to work with various games by including specific game headers. The current implementation includes support for the "Ticket to Ride" and "Snake" game.

### Authors

- Valentin Le Lièvre
- Thibault Hilaire

### License: GPL

### Dependencies

- `api.c`, `api.h`
- `lib/json.h`
- `gameHeaders/ticketToRide.h` (if used, optional)
- `gameHeaders/snake.h` (if used, optional)

## Getting Started

### 1. Git

Create a git repository for your project. It will help you keep track of your changes and revert them if needed. You can even save them on a remote server like GitHub or GitLab to have a cloud backup.

*The usage of git will be taken into account in the evaluation of your project.*

### 2. Makefile

Create a makefile to automate the compiling steps. It will help you compile your project with a single command. You can also add commands to clean temporary files, run valgrind memory leak tests ...

*The usage of a makefile will be taken into account in the evaluation of your project.*

**Note :** Make sure api.c is in the selected sources to compile in your makefile.

## Step-by-Step Guide

### 1. Connect to the Server

Use the `connectToCGS` function to establish a connection to the server.

```c
ResultCode result = connectToCGS("server_address", port);
if (result != ALL_GOOD) {
    // Handle connection error
}
```

### 2. Send Your Name

Send your name to the server using the `sendName` function. This will act as a unique identifier during the game.

```c
ResultCode result = sendName("YourName");
if (result != ALL_GOOD) {
    // Handle error
}
```

### 3. Configure Game Settings

Connect to a game by creating the `GameSettings` struct and sending it to the server with `sendGameSettings`.
In response, you will receive the `GameData` struct containing the game information.

```c
GameSettings gameSettings = GameSettingsDefaults;
gameSettings.gameType = TRAINNING;
gameSettings.botId = RANDOM_PLAYER;
gameSettings.difficulty = EASY;

GameData gameData;
ResultCode result = sendGameSettings(gameSettings, &gameData);
if (result != ALL_GOOD) {
    // Handle error
}
```

### 4. Get Opponent's Move

During a game, retrieve the opponent's move using the `getMove` function.
In response, you will receive the `MoveData` struct containing the opponent's move. As well as the `MoveResult` struct containing the result of the move.

```c
MoveData moveData;
MoveResult moveResult;

ResultCode result = getMove(&moveData, &moveResult);
if (result != ALL_GOOD) {
    // Handle error
}
```

### 5. Send Your Move

During a game, send your move to the server using the `sendMove` function.
Use the `MoveData` struct to set up your move.
In response, you will receive the `MoveResult` struct containing the result of your move.

```c
MoveData moveData;
// Set up your move data

MoveResult moveResult;
ResultCode result = sendMove(&moveData, &moveResult);
if (result != ALL_GOOD) {
    // Handle error
}
```

### 6. Send a Message

Send a message to your opponent using the `sendMessage` function.

```c
ResultCode result = sendMessage("Hello, opponent!");
if (result != ALL_GOOD) {
    // Handle error
}
```

### 7. Display the Game Board

Display the game board using the `printBoard` function.
This will print, in color, the current state of the game board to the console. 

```c
ResultCode result = printBoard();
if (result != ALL_GOOD) {
    // Handle error
}
```

### 8. Quit the Game

Quit the game using the `quitGame` function.

```c
ResultCode result = quitGame();
if (result != ALL_GOOD) {
    // Handle error
}
```

## Recommendations

- **Error Handling:** Always check the return values of functions to handle errors appropriately.
- **Memory Management:** Free allocated memory to avoid memory leaks. Pay special attention to `opponentMessage` in `MoveData` and `gameName` in `GameData`.
- **Use Defaults:** Utilize the default values provided for `GameSettings`, `GameData`, and `MoveData` to reduce potential errors.
- **Documentation:** Refer to the comments in the header files for detailed information about each function and struct.

## Going Further

The real challenge begins when you start implementing your own AI to play games automatically. You can create a bot that plays the game based on specific strategies, algorithms.

### 1. Local representation of the game board

When starting a game, you will recieve a `GameData` struct containing the game information. The `board` field of this struct is a 2D array representing the game board. The array contain unstructured game data (See ticketToRide.h to know how to read the data). You will need to create a local representation of the game board to be able to manipulate it easily.

You should come up with a data structure that will later allow you to easily manipulate the game board and analyse it to make decisions. Exemple of data structure will be: matrix, lists, trees, etc.

### 2. Implementing a bot

You will need to implement a bot that will play the game automatically. The bot will need to analyze the game board, make decisions based on the game state, and send moves to the server.

For each turn, you will have to take into account the opponent's move and update your local representation of the game board accordingly. Then, you will have to decide on your move and send it to the server.

**Note :** Pay attention to the time you have to make a move. If you exceed the time limit, you will lose the game. During the tournament, the maximum time limit to make a move will be 15 second.

### 3. Testing your bot

You can test your bot by playing games against other bots or by playing games manually. This will help you identify potential issues and improve your bot's performance.

Each supported games provides multiple bots to train with. At first, you can play against the random bot to test your bot's basic functionalities. Then, you can play against the easy and intellingent bots to test your bot's strategy.

You can also play games against other students' bots to compare your bot's performance and improve it.

One way to improve your bot is by saving the game data of multiples games and analyzing it after the game to identify potential issues and improve your bot's strategy. (To save time, save the output of the printBoard function in a file. You will be able to replay the game with a visual representation of the game board).

**Good luck!**