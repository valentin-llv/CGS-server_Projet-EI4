/*

    API for Coding Game Server

    Goes alongside api.c and require json.h

*/

/*

    1. How to use:
        To connect to the server and play a game you have to call (in order):
            - int connectToCGS(char* adress, unsigned int port)
            - int sendName(char* name)
            - int sendGameSettings(GameSettings gameSettings, GameData* gameData)

    2. Constants:
        To communicate actions to the server will can use CONSTANTS variables, defined
        in enums types below, instead of hex code values.

    3. Defaults values for struct:
        You can instanciate struct with pre-set default values by using:
            - GameSettings gameSettings = GameSettingsDefaults;
            - GameData gameData = GameDataDefaults;
            - MoveData moveData = MoveDataDefaults;

    4. Every functions will return an int indicating the succes / failure of the function. 
        Possible error codes are:
            - 0x10: Param errors
            - 0x20: server / network errors
            - 0x30: other error
            - 0x40: all good

    5. Memory management:
        Some functions are using mallocs calls to allocate memory space. You will need
        to free thoses spaces.

        Variables that need to be freeed are:
            - gameName from GameData struct
            - map from GameData struct
            - opponentMessage from MoveData struct

        NOTE: you are likely to create multiple instance of MoveData, don't forget
        to free opponentMessage or you will likely encounter Segmentation fault error.

*/

#ifndef API_h
#define API_h

#define JSMN_HEADER
#include "json.h"

/*

    Structs

*/

enum GamesTypes {
    TRAINNING = 0x1,
    MATCH = 0x2,
    TOURNAMENT = 0x3,
    DEMO = 0x4,

    GamesTypesMax // Keep as last element
};

enum BotsNames {
    RANDOM_PLAYER = 0x1,
    SUPER_PLAYER = 0x2,

    BotsNamesMax // Keep as last element
};

typedef struct GameSettings_ {
    char gameType; // One of GamesTypes values
    char botName; // One of BotsName values

    unsigned char difficulty; // Difficulty higher is harder, values between 0 and 3, default 0
    unsigned int timeout; // Timeout in seconds, max value 300, default 60
    unsigned char start; // Define who starts, 1 you and 2 opponent, set to 0 for random, default 0
    unsigned int seed; // Set seed of the game, usefull when debuging, max value 9999, default 0 (not used)
    unsigned char reconnect; // Set 1 to enable reconnection to game, default 0
} GameSettings;
extern const GameSettings GameSettingsDefaults;

typedef struct GameData_ {
    char* gameName; // String containing the game name
    int gameSeed; // Contain the seed used for the game board generation

    int firstPlayer; // Defines who start, 1 you and 2 opponent

    int boardX; // Length of board along X axis
    int boardY; // Length of board along Y axis

    int nbWalls; // Total number of walls
    int* map; // Board data
} GameData;
extern const GameData GameDataDefaults;

enum MoveState { // TODO check values
    NORMAL_MOVE = 0x1,
    LOOSING_MOVE = 0x2,
    WIN = 0x3,
    OPPONENT_DISCONNECTED = 0x4,

    StateMax // Keep as last element
};

enum MoveDirections {
    UP = 0x0,
    RIGHT = 0x1,
    DOWN = 0x2,
    LEFT = 0x3,

    MovesMax // Keep as last element
};

typedef struct MoveData_ {
    int action; // One of MoveState values
    int direction; // One of MoveDirections values
    char* opponentMessage; // String containing message send by the opponent
    char* message; // String containing message send by the server
} MoveData;
extern const MoveData MoveDataDefaults;

/*

    Exposed functions

*/

int connectToCGS(char* adress, unsigned int port);

int sendName(char* name);
int sendGameSettings(GameSettings gameSettings, GameData* gameData);

int getMove(MoveData *moveData);
int sendMove(unsigned int move, int* moveType);

int sendMessage();

int printBoard();

int quitGame();

/*

    Hidden functions

*/

static int connectToSocket(char* adress, unsigned int port);

static int sendData(char* data, unsigned int dataLenght);

static int getServerResponse(char** string, int* stringLength, jsmntok_t* tokens, int nbTokens);
static int getData(char** string, int* stringLength);

/*

    Utils

*/

static int getIntegerLength(int value);
static int isValidIpAddress(char *ipAddress);

#endif