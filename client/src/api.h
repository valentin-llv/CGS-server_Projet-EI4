/*

    API for Coding Game Server

    Require api.c, lib/json.h ang gameHeaders/[game name].h to works with.

    Authors: Valentin Le Lièvre
    Licence: GPL

    Copyright 2025 Valentin Le Lièvre

*/

/*

    1. How to use:
        To connect to the server and play a game you have to call (in order):
            - int connectToCGS(char* adress, unsigned int port)
            - int sendName(char* name)
            - int sendGameSettings(GameSettings gameSettings, GameData* gameData)

        You will then be connected to a game and will be able to play by calling:
            - int getMove(MoveData *moveData)
            - int sendMove(unsigned int move, int* moveType)

    2. Constants:
        To communicate actions to the server you can use CONSTANTS variables, defined
        in enum types below, instead of hex code values.

        For exemple: use the TRAINNING constant instead of code 0x1. It will greatly improve code readability.

    3. Defaults values for struct:
        You can instanciate struct with pre-set default values by using:
            - GameSettings gameSettings = GameSettingsDefaults;
            - GameData gameData = GameDataDefaults;
            - MoveData moveData = MoveDataDefaults;

        This will reduce potential errors and unexpected behaviours.

    4. Every functions will return an int indicating the succes / failure of the function. 
        Possible error codes are:
            - 0x10: Param errors
            - 0x20: server / network errors
            - 0x30: other error
            - 0x40: all good

        Be sure to check return values of functions to handle errors. You may want to use the constants for better readability.

        Exemple: if(result == SERVER_ERROR) { ... }

    5. Memory management:
        Some functions are using malloc calls to allocate memory space. You will need
        to free thoses spaces.

        Variables that need to be freeed are:
            - gameName from GameData struct
            - board from GameData struct
            - opponentMessage from MoveData struct

        NOTE: you are likely to create multiple instance of MoveData, don't forget
        to free opponentMessage or you will likely encounter Segmentation fault error.

*/

// Usual .h stuff
#ifndef API_H
#define API_H

// This define is used by the JSON library
#define JSMN_HEADER
#include "lib/json.h"

// Game specific include
#define ONLY_HEADERS
#include "gameHeaders/ticketToRide.h"

/*

    Structs

*/
typedef enum {
    TRAINNING = 0x1, // Play against a bot
    MATCH = 0x2, // Play against a player
    TOURNAMENT = 0x3, // Enter a tournament

    GamesTypesMax // Keep as last element, is used for params checking
} GamesType;

typedef enum {
    EASY = 0x1,
    NORMAL = 0x2,
    HARD = 0x3,

    GameDifficultyMax // Keep as last element, is used for params checking
} GameDifficulty;

typedef struct GameSettings_ {
    GamesType gameType; // One of GamesTypes values
    BotsNames botId; // One of BotsName values (only if you play in training)

    GameDifficulty difficulty; // Game difficulty, higher is harder, values between 1 and 3, default is 1 (used only in training mode)
    unsigned int timeout; // Timeout in seconds, max value 60, default 15 (used only in training mode, tournament mode is set to 15)
    unsigned char starter; // Define who starts, 1 -> you or 2 -> opponent, set to 0 for random, default 0 (used only in training mode)
    unsigned int seed; // Seed for the board generation, usefull when debuging to play the same game again, max value 9999, default to 0 for random (used only in training mode)
    
    unsigned char reconnect; // Set 1 if you want to reconnect to a game you already started, default 0
} GameSettings;

typedef struct GameData_ {
    char* gameName; // String containing the game name
    int gameSeed; // Contain the seed used for the game board generation (if you didn't provide one)

    int starter; // Defines who start, 1 you and 2 opponent

    int boardWidth; // Length of board along X axis
    int boardHeight; // Length of board along Y axis

    int nbElements; // Total number of elements on the board
    int* boardData; // Board data, an array containing unformatted board data
} GameData;

typedef enum {
    NORMAL_MOVE = 0x1,
    LOOSING_MOVE = 0x2,
    WINNING_MOVE = 0x3,
    ILLEGAL_MOVE = 0x4,

    StateMax // Keep as last element
} MoveState;

typedef enum {
    PARAM_ERROR = 0x10,
    SERVER_ERROR = 0x20,
    OTHER_ERROR = 0x30,
    MEMORY_ALLOCATION_ERROR = 0x40,
    ALL_GOOD = 0x50
} ResultCode;

/*

    Constants

*/

static const unsigned int MAX_TIMEOUT = 60; // in seconds
static const unsigned int MIN_TIMEOUT = 5;
static const unsigned int MAX_SEED = 10000;

// Used to set defaults values to struct. The defintion are in api.c
extern const GameSettings GameSettingsDefaults;
extern const GameData GameDataDefaults;
extern const MoveData MoveDataDefaults;

/*

    Exposed functions

*/

ResultCode connectToCGS(char* adress, unsigned int port);

ResultCode sendName(char* name);
ResultCode sendGameSettings(GameSettings gameSettings, GameData* gameData);

ResultCode getMove(MoveData* moveData, MoveResult* moveResult);
ResultCode sendMove(MoveData* moveData, MoveResult* moveResult);

ResultCode sendMessage(char* message);
ResultCode printBoard();

ResultCode quitGame();

/*

    Hidden functions

*/

static ResultCode connectToSocket(char* adress, unsigned int port, unsigned int adrSize);
static ResultCode dnsSearch(char* domain, char** ipAdress, int* adrSize);

static int sendData(char* data, unsigned int dataLenght);

static int getServerResponse(char** string, int* stringLength, jsmntok_t* tokens, int nbTokens);
static int getData(char** string, int* stringLength);

/*

    Utils functions

*/

static int getIntegerLength(int value);
static int isValidIpAddress(char *ipAddress);

#endif