/*

    API for the Coding Game Server

    Require api.h, json.h ang [game name].h

*/

/*

    See api.h for documentation

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Those libs are available on Linux (including WSL) and Mac but not Windows
// If you use windows you may want to use winsock.h and rename functions
// like inet_pton to match header functions name

#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>

// External JSON library
#include "lib/json.h"

// Game headers
#include "gamesHeaders/ticketToRide.h"

// API base headers
#include "api.h"

/*

    Default values for struct

*/

const GameSettings GameSettingsDefaults = { TRAINNING, RANDOM_PLAYER, 0, 60, 0, 0, 0 };
const GameData GameDataDefaults = { "", 0, 0, 0, 0, 0, 0 };

/*

    Global vars

*/

int SOCKET;

/*

    Exposed functions

*/

ResultCode connectToCGS(char* adress, unsigned int port) {
    if(!isValidIpAddress(adress)) return PARAM_ERROR;
    if(!port) return PARAM_ERROR;

    return connectToSocket(adress, port);
}

ResultCode sendName(char* name) {
    // Check user's provided data
    if(strlen(name) >= 90) return PARAM_ERROR;

    // Parse data into json string
    char* data = (char *) malloc(100 * sizeof(char));
    int dataLenght = sprintf(data, "{ 'name': '%s' }", name);

    // Send data and check for succes
    if(!sendData(data, dataLenght)) return SERVER_ERROR;
    free(data);
    
    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(5 * sizeof(jsmntok_t));

    if(!getServerResponse(&string, stringLength, tokens, 5)) return SERVER_ERROR;

    free(string);
    free(stringLength);
    free(tokens);

    // Return succes
    return ALL_GOOD;
}

ResultCode sendGameSettings(GameSettings gameSettings, GameData* gameData) {
    // Check user's provided data
    if(gameSettings.gameType >= GamesTypesMax || gameSettings.gameType < 0) return PARAM_ERROR;
    if(gameSettings.botId >= BotsNamesMax || gameSettings.botId < 0) return PARAM_ERROR;

    if(gameSettings.difficulty > GameDifficultyMax || gameSettings.difficulty < 0) return PARAM_ERROR;
    if(gameSettings.timeout > MAX_TIMEOUT || gameSettings.timeout < MIN_TIMEOUT) return PARAM_ERROR;

    if(gameSettings.starter != 0 && gameSettings.starter != 1 && gameSettings.starter != 2) return PARAM_ERROR;
    if(gameSettings.seed > MAX_SEED || gameSettings.seed < 0) return PARAM_ERROR;
    
    // Parse data into json string
    char* data = (char *) malloc(250 * sizeof(char));
    int dataLenght = sprintf(data, "{ 'gameType': '%d', 'botId': '%d', 'difficulty': '%d', 'timeout': '%d', 'start': '%d', 'seed': '%d', 'reconnect': '%d'}",
    gameSettings.gameType, gameSettings.botId, gameSettings.difficulty, gameSettings.timeout, gameSettings.starter, gameSettings.seed, gameSettings.reconnect);

    // Send data and check for succes
    if(!sendData(data, dataLenght)) return SERVER_ERROR;
    free(data);

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(19 * sizeof(jsmntok_t));

    if(!getServerResponse(&string, stringLength, tokens, 19)) return SERVER_ERROR;

    // Set struct from param to defaults values
    *gameData = GameDataDefaults;

    // Load recieved data into struct
    int blockLength = tokens[4].end - tokens[4].start + 1;
    char* gameName = (char *) malloc(blockLength * sizeof(char));
    sprintf(gameName, "%.*s", blockLength - 1, &string[tokens[4].start]);
    gameData->gameName = gameName;

    // Data is in specific order
    gameData->starter = atoi(&string[tokens[6].start]);
    gameData->gameSeed = atoi(&string[tokens[8].start]);
    gameData->boardWidth = atoi(&string[tokens[10].start]);
    gameData->boardHeight = atoi(&string[tokens[12].start]);
    gameData->nbElements = atoi(&string[tokens[14].start]);

    int blockLength2 = tokens[16].end - tokens[16].start + 1;
    int* boardData = (int *) malloc(blockLength2 * sizeof(int));

    int i = 0; int j = 0;
    while((j + i) < blockLength2 - 1) {
        boardData[i] = atoi(&string[tokens[16].start + j + i]);

        j = j + getIntegerLength(boardData[i]);
        i ++;
    }
    gameData->boardData = boardData;

    free(string);
    free(stringLength);
    free(tokens);

    // Return succes
    return ALL_GOOD;
}

ResultCode getMove(MoveData* moveData, MoveResult* moveResult) {
    // Parse data into json string
    char* data = "{ 'action': 'getMove' }";

    // Send data and check for success
    if(!sendData(data, strlen(data))) return SERVER_ERROR;

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(11 * sizeof(jsmntok_t));

    if(!getServerResponse(&string, stringLength, tokens, 9)) return SERVER_ERROR;

    // Call the function related to the selected game to properly unpack the data
    unpackGetMoveData(string, tokens, moveData, moveResult);

    free(string);
    free(stringLength);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

ResultCode sendMove(MoveData* moveData, MoveResult* moveResult) {
    // Parse data into json string
    char* data = (char *) malloc(PACKED_DATA_MAX_SIZE * sizeof(char));

    printf("Before pack\n");

    // Call the function related to the selected game to properly pack the data
    int dataLength = packSendMoveData(data, moveData);

    printf("After pack\n");

    // Send data and check for success
    if(!sendData(data, dataLength)) return SERVER_ERROR;
    free(data);

    printf("Data sent\n");

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(9 * sizeof(jsmntok_t));

    printf("Before get response\n");

    if(!getServerResponse(&string, stringLength, tokens, 9)) return SERVER_ERROR;

    printf("After get response\n");

    // If returnCode is NORMAL_MOVE, unpack the data
    if(moveResult->action == NORMAL_MOVE) unpackSendMoveResult(string, tokens, moveResult);

    printf("After unpack\n");

    free(string);
    free(stringLength);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

ResultCode sendMessage(char* message) {
    // Check user's provided data
    if(strlen(message) >= 256) return PARAM_ERROR;

    // Parse data into json string
    char* data = (char *) malloc(300 * sizeof(char));
    int dataLength = sprintf(data, "{ 'message': '%s' }", message);

    // Send data and check for success
    if(!sendData(data, dataLength)) return SERVER_ERROR;
    free(data);

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(5 * sizeof(jsmntok_t));

    if(!getServerResponse(&string, stringLength, tokens, 5)) return SERVER_ERROR;

    free(string);
    free(stringLength);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

ResultCode printBoard() {
    // Parse data into json string
    char* data = "{ 'action': 'displayGame' }";

    // Send data and check for succes
    if(!sendData(data, strlen(data))) return SERVER_ERROR;

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(5 * sizeof(jsmntok_t));

    if(!getServerResponse(&string, stringLength, tokens, 5)) return SERVER_ERROR;

    int blockLength = atoi(&string[tokens[4].start]) + 1;
    char buffer[blockLength];
    memset(buffer, 0, (blockLength) * sizeof(char));

    int res = read(SOCKET, buffer, blockLength - 1);
    if(res == -1) return SERVER_ERROR;

    printf("%s\n\n", buffer);

    free(string);
    free(stringLength);
    free(tokens);

    // Return succes
    return ALL_GOOD;
}

ResultCode quitGame() {
    // Parse data into json string
    char* data = "{ 'action': 'quitGame' }";

    // Send data and check for succes
    if(!sendData(data, strlen(data))) return SERVER_ERROR;

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(5 * sizeof(jsmntok_t));

    if(!getServerResponse(&string, stringLength, tokens, 5)) return SERVER_ERROR;

    free(string);
    free(stringLength);
    free(tokens);

    // Return succes
    return ALL_GOOD;
}

/*

    Hidden constants

*/

#define FIRST_MSG_LENGTH 6

/*

    Hidden functions

*/

static int connectToSocket(char* adress, unsigned int port) {
    int soc = socket(AF_INET, SOCK_STREAM, 0);
    if (soc < 0) {
        printf("Socket creation error\n");
        return 0x30;
    }

    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    int res = inet_pton(AF_INET, adress, &serv_addr.sin_addr);
    if (res <= 0) {
        printf("\x1b[1;31mInvalid address or address not supported\x1b[0m\n");
        return 0x10;
    }


    int status = connect(soc, (struct sockaddr*) &serv_addr, sizeof(serv_addr));
    if (status < 0) {
        printf("\x1b[1;31mConnection to server failed\x1b[0m\n");
        return 0x20;
    }

    SOCKET = soc;
    return 0x40;
}

static int sendData(char* data, unsigned int dataLenght) {
    // Allocate data block for first message containing next message length
    char* dataBlock1 = (char *) malloc(FIRST_MSG_LENGTH * sizeof(char));

    // Fill string with spaces
    for(int i = 0; i < FIRST_MSG_LENGTH; i++) dataBlock1[i] = ' ';

    // Fill string with the length of the next message
    sprintf(dataBlock1, "%d", dataLenght);

    // Send first message over the socket wire
    int res = send(SOCKET, dataBlock1, FIRST_MSG_LENGTH, 0);
    if(res == -1) return 0;

    free(dataBlock1);

    // Send data over the socket wire
    int res2 = send(SOCKET, data, dataLenght, 0);
    if(res2 == -1) return 0;

    // Return succes
    return 1;
}

static int getServerResponse(char** string, int* stringLength, jsmntok_t* tokens, int nbTokens) {
    // Get data
    if(!getData(string, stringLength)) return 0;
    
    // Instanciate json parser
    jsmn_parser parser;
    jsmn_init(&parser);

    // Parse json string
    jsmn_parse(&parser, *string, *stringLength, tokens, nbTokens);

    // Get state infos
    int state = atoi(&(*string)[tokens[2].start]);

    printf("State: %d\n", state);
    
    // Print error if needed
    if(!state) {
        int blockLength = tokens[4].end - tokens[4].start;
        printf("\x1b[1;31mServer responded with following error:\x1b[0m \x1b[3m%.*s\x1b[23m\n", blockLength, (*string + tokens[4].start));
        return 0;
    }

    printf("Server response: %s\n", *string);

    // Return succes
    return 1;
}

static int getData(char** string, int* stringLength) {
    // Allocate buffer to store data from read
    char buffer[FIRST_MSG_LENGTH] = { 0 };

    // Read incoming data on socket wire
    int res = read(SOCKET, buffer, FIRST_MSG_LENGTH - 1);
    if(res == -1) return 0;

    // First message contain the length of the next one
    *stringLength = atoi(buffer) + 1;

    // Allocate buffer of 0 based on the next message length
    char buffer2[*stringLength];
    memset(buffer2, 0, (*stringLength) * sizeof(char));

    // Read new incomming message on the socket wire
    int res2 = read(SOCKET, buffer2, *stringLength - 1);
    if(res2 == -1) return 0;
    
    // Copy recieved data to **string param to effectivly return the recieved string
    *string = (char *) malloc(*stringLength * sizeof(char));
    strcpy(*string, buffer2);

    // Return succes
    return 1;
}

/*

    Utils

*/

static int getIntegerLength(int value) {
    int l = !value;
    while(value) { l++; value /= 10; }
    return l;
}

static int isValidIpAddress(char *ipAddress) {
    struct sockaddr_in sa;
    int result = inet_pton(AF_INET, ipAddress, &(sa.sin_addr));
    return result != 0;
}