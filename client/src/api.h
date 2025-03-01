#ifndef API_H
#define API_H


#include "gameHeaders/ticketToRide.h"


/*

    Constants

*/

#define MAX_TIMEOUT 60 // in seconds
#define MIN_TIMEOUT 5

#define MAX_SEED 10000

#define MAX_USERNAME_LENGTH 100
#define MAX_MESSAGE_LENGTH 256

#define GAME_SETTINGS_MAX_JSON_LENGTH 250
#define PACKED_DATA_MAX_SIZE 400

#define GET_MOVE_RESPONSE_JSON_SIZE 19
#define SEND_MOVE_RESPONSE_JSON_SIZE 29

#define BOARD_STATE_RESPONSE_JSON_SIZE 13

#define FIRST_MSG_LENGTH 6

// Json messages size, (nb of key * 2) + 1
#define SERVER_ACKNOWLEDGEMENT_JSON_SIZE 5
#define GAME_SETTINGS_ACKNOWLEDGEMENT_JSON_SIZE 19

/*

    Game specific functions prototypes

*/

int verifyAndPackGameSettings(char* data, GameSettings gameSettings);
int unpackGameSettingsData(char* string, jsmntok_t* tokens, GameData* gameData);

int unpackGetMoveData(char* string, jsmntok_t* tokens, MoveData* moveData, MoveResult* moveResult);

int packSendMoveData(char* data, MoveData* moveData);
int unpackSendMoveResult(char* string, jsmntok_t* tokens, MoveResult* moveResult);

int unpackGetBoardState(char* string, jsmntok_t* tokens, BoardState* boardState);

/*

    Hidden functions

*/

static ResultCode connectToSocket(const char *adress, unsigned int port, unsigned int adrSize);
static ResultCode dnsSearch(const char *domain, char** ipAdress, int* adrSize);

static int sendData(char* data, unsigned int dataLength);

static int getServerResponse(char** string, jsmntok_t* tokens, int nbTokens);
static int getData(char** string, int* stringLength);

static int readNByte(char** buffer, int nbByte);

/*

    Utils functions

*/

static int getIntegerLength(int value);
static int isValidIpAddress(char *ipAddress);

/*

    Debug functions

*/

ResultCode printError(const char* function, ResultCode code, const char* message, ...);
void printDebug(const char* function, const char* message, ...);



#endif