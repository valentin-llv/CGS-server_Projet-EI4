/*

    API for the Coding Game Server

    Require api.h, lib/json.h ang gameHeaders/[game name].h to works with.

    Authors: Valentin Le Lièvre
    Licence: GPL

    Copyright 2025 Valentin Le Lièvre

    ---------------------------------

    Note: See api.h for documentation

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Socket headers
// Those libs are available on Linux (including WSL) and Mac but not Windows
// If you use windows you may want to use winsock.h and rename functions like inet_pton to match headers function names

#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>

// External JSON library
#include "lib/json.h"

// Game headers
#include "gameHeaders/ticketToRide.h"

// API base headers
#include "api.h"

/*

    Default values for struct

    You can use those variables to initialize struct with default values

*/

const GameSettings GameSettingsDefaults = { TRAINNING, RANDOM_PLAYER, 1, 15, 0, 0, 0 };
const GameData GameDataDefaults = { "", 0, 0, 0, 0, 0, 0 };

/*

    Global vars

*/

int SOCKET;

/*

    Exposed functions

    Those are the function you can use to interact with the server

*/

// This is the first function you should call, it will connect you to the server.
// You need to provide the server address and the port to connect to.
// This is a blocking function, it will wait until the connection is established, it may take some time.

ResultCode connectToCGS(char* adress, unsigned int port) {
    if(!isValidIpAddress(adress)) return PARAM_ERROR;
    if(!port) return PARAM_ERROR;

    return connectToSocket(adress, port);
}

// After connecting to the server you need to send your name to the server. It will be used to uniquely identify you.
// You need to provide your name as a string. It should be less than 90 characters long.

ResultCode sendName(char* name) {
    // Check user's provided data
    if(strlen(name) >= 90) return PARAM_ERROR;

    // Parse data into json string
    char* data = (char *) malloc(100 * sizeof(char));

    // Check if malloc failed
    if(data == NULL) return MEMORY_ALLOCATION_ERROR;

    // Fill data with name
    int dataLenght = sprintf(data, "{ 'name': '%s' }", name);

    // Send data and check for succes
    if(!sendData(data, dataLenght)) return SERVER_ERROR;
    free(data);
    
    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(5 * sizeof(jsmntok_t));

    // Check if malloc failed
    if(stringLength == NULL) return MEMORY_ALLOCATION_ERROR;
    if(tokens == NULL) return MEMORY_ALLOCATION_ERROR;

    if(!getServerResponse(&string, stringLength, tokens, 5)) return SERVER_ERROR;

    free(string);
    free(stringLength);
    free(tokens);

    // Return succes
    return ALL_GOOD;
}

// After sending your name you need to send game settings to the server to start a game.
// You need to provide a GameSettings struct and a GameData struct to store the game data returned by the server.
// You can use the GameSettingsDefaults and GameDataDefaults variables to initialize the struct with default values.
// To fill the GameSettings struct you may want to use predefined constants available in api.h.

ResultCode sendGameSettings(GameSettings gameSettings, GameData* gameData) {
    // Check user's provided data
    if(gameSettings.gameType >= GamesTypesMax || gameSettings.gameType <= 0) return PARAM_ERROR;
    if(gameSettings.botId >= BotsNamesMax || gameSettings.botId <= 0) return PARAM_ERROR;

    if(gameSettings.difficulty > GameDifficultyMax || gameSettings.difficulty <= 0) return PARAM_ERROR;
    if(gameSettings.timeout > MAX_TIMEOUT || gameSettings.timeout < MIN_TIMEOUT) return PARAM_ERROR;

    if(gameSettings.starter != 0 && gameSettings.starter != 1 && gameSettings.starter != 2) return PARAM_ERROR;
    if(gameSettings.seed > MAX_SEED || gameSettings.seed < 0) return PARAM_ERROR;
    
    // Parse data into json string
    char* data = (char *) malloc(250 * sizeof(char));

    // Check if malloc failed
    if(data == NULL) return MEMORY_ALLOCATION_ERROR;

    int dataLenght = sprintf(data, "{ 'gameType': '%d', 'botId': '%d', 'difficulty': '%d', 'timeout': '%d', 'starter': '%d', 'seed': '%d', 'reconnect': '%d'}",
    gameSettings.gameType, gameSettings.botId, gameSettings.difficulty, gameSettings.timeout, gameSettings.starter, gameSettings.seed, gameSettings.reconnect);

    // Send data and check for succes
    if(!sendData(data, dataLenght)) return SERVER_ERROR;
    free(data);

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(19 * sizeof(jsmntok_t));

    // Check if malloc failed
    if(stringLength == NULL) return MEMORY_ALLOCATION_ERROR;
    if(tokens == NULL) return MEMORY_ALLOCATION_ERROR;

    if(!getServerResponse(&string, stringLength, tokens, 19)) return SERVER_ERROR;

    // Set struct from param to defaults values
    *gameData = GameDataDefaults;

    // Load recieved data into struct
    int blockLength = tokens[4].end - tokens[4].start + 1;
    char* gameName = (char *) malloc(blockLength * sizeof(char));

    // Check if malloc failed
    if(gameName == NULL) return MEMORY_ALLOCATION_ERROR;

    sprintf(gameName, "%.*s", blockLength - 1, &string[tokens[4].start]);
    gameData->gameName = gameName;

    // Data is in specific order
    gameData->gameSeed = atoi(&string[tokens[6].start]);
    gameData->starter = atoi(&string[tokens[8].start]);
    gameData->boardWidth = atoi(&string[tokens[10].start]);
    gameData->boardHeight = atoi(&string[tokens[12].start]);
    gameData->nbElements = atoi(&string[tokens[14].start]);

    blockLength = tokens[16].end - tokens[16].start + 1;
    int* boardData = (int *) malloc(blockLength * sizeof(int));

    // Check if malloc failed
    if(boardData == NULL) return MEMORY_ALLOCATION_ERROR;

    int i = 0; int j = 0;
    while((j + i) < blockLength - 1) {
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

// During a game this function is used to know what your opponent did during his turn.
// You need to provide an empty MoveData struct and an empty MoveResult struct to store the move data returned by the server.
// MoveData struct store the move your opponent did and MoveResult struct store the result of the move.

ResultCode getMove(MoveData* moveData, MoveResult* moveResult) {
    // Parse data into json string
    char* data = "{ 'action': 'getMove' }";

    // Send data and check for success
    if(!sendData(data, strlen(data))) return SERVER_ERROR;

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(19 * sizeof(jsmntok_t));

    // Check if malloc failed
    if(stringLength == NULL) return MEMORY_ALLOCATION_ERROR;
    if(tokens == NULL) return MEMORY_ALLOCATION_ERROR;

    if(!getServerResponse(&string, stringLength, tokens, 19)) return SERVER_ERROR;

    // Call the function related to the selected game to properly unpack the data
    int result = unpackGetMoveData(string, tokens, moveData, moveResult);

    if(result == -1) return OTHER_ERROR;

    free(string);
    free(stringLength);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

// During a game this function is used to send your move to the server.
// You need to provide a MoveData struct containing your move and an empty MoveResult struct to store the result of the move returned by the server.

ResultCode sendMove(MoveData* moveData, MoveResult* moveResult) {
    // Parse data into json string
    char* data = (char *) malloc(PACKED_DATA_MAX_SIZE * sizeof(char));

    // Check if malloc failed
    if(data == NULL) return MEMORY_ALLOCATION_ERROR;

    // Call the function related to the selected game to properly pack the data
    int dataLength = packSendMoveData(data, moveData);

    // Check if pack failed
    if(dataLength == -1) return OTHER_ERROR;

    // Send data and check for success
    if(!sendData(data, dataLength)) return SERVER_ERROR;
    free(data);

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(33 * sizeof(jsmntok_t));

    // Check if malloc failed
    if(stringLength == NULL) return MEMORY_ALLOCATION_ERROR;
    if(tokens == NULL) return MEMORY_ALLOCATION_ERROR;

    if(!getServerResponse(&string, stringLength, tokens, 33)) return SERVER_ERROR;

    moveResult->state = atoi(&string[tokens[2].start]);

    // If returnCode is NORMAL_MOVE, unpack the data
    if(moveResult->state == NORMAL_MOVE) {
        int result = unpackSendMoveResult(string, tokens, moveResult);
        if(result == -1) return OTHER_ERROR;
    }

    free(string);
    free(stringLength);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

// This function is used to send a message to your opponent during a game.
// You need to provide the message as a string. It should be less than 256 characters long.

ResultCode sendMessage(char* message) {
    // Check user's provided data
    if(strlen(message) >= 256) return PARAM_ERROR;

    // Parse data into json string
    char* data = (char *) malloc(300 * sizeof(char));

    // Check if malloc failed
    if(data == NULL) return MEMORY_ALLOCATION_ERROR;

    int dataLength = sprintf(data, "{ 'action': 'sendMessage', 'message': '%s' }", message);

    // Send data and check for success
    if(!sendData(data, dataLength)) return SERVER_ERROR;
    free(data);

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(5 * sizeof(jsmntok_t));

    // Check if malloc failed
    if(stringLength == NULL) return MEMORY_ALLOCATION_ERROR;
    if(tokens == NULL) return MEMORY_ALLOCATION_ERROR;

    if(!getServerResponse(&string, stringLength, tokens, 5)) return SERVER_ERROR;

    free(string);
    free(stringLength);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

// This function is used to display the game board during a game.
// It will print the colored board in the console.

ResultCode printBoard() {
    // Parse data into json string
    char* data = "{ 'action': 'displayGame' }";

    // Send data and check for succes
    if(!sendData(data, strlen(data))) return SERVER_ERROR;

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(5 * sizeof(jsmntok_t));

    // Check if malloc failed
    if(stringLength == NULL) return MEMORY_ALLOCATION_ERROR;
    if(tokens == NULL) return MEMORY_ALLOCATION_ERROR;

    if(!getServerResponse(&string, stringLength, tokens, 5)) return SERVER_ERROR;

    int blockLength = atoi(&string[tokens[4].start]) + 1;
    char buffer[blockLength];
    memset(buffer, 0, (blockLength) * sizeof(char));

    int res = read(SOCKET, buffer, blockLength - 1);
    if(res == -1) return SERVER_ERROR;

    printf("%s\n", buffer);

    free(string);
    free(stringLength);
    free(tokens);

    // Return succes
    return ALL_GOOD;
}

// This function is used to quit the currently running game.

ResultCode quitGame() {
    // Parse data into json string
    char* data = "{ 'action': 'quitGame' }";

    // Send data and check for succes
    if(!sendData(data, strlen(data))) return SERVER_ERROR;

    // Get server acknowledgement
    char* string; int* stringLength = (int *) malloc(sizeof(int));
    jsmntok_t* tokens = (jsmntok_t *) malloc(5 * sizeof(jsmntok_t));

    // Check if malloc failed
    if(stringLength == NULL) return MEMORY_ALLOCATION_ERROR;
    if(tokens == NULL) return MEMORY_ALLOCATION_ERROR;

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

    Those are the functions used by the exposed functions to interact with the server
    You are not supposed to use them directly

*/

static ResultCode connectToSocket(char* adress, unsigned int port) {
    int soc = socket(AF_INET, SOCK_STREAM, 0);
    if (soc < 0) {
        printf("\x1b[1;31mSocket creation failed\x1b[0m\n");
        return OTHER_ERROR;
    }

    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    int res = inet_pton(AF_INET, adress, &serv_addr.sin_addr);

    int status = connect(soc, (struct sockaddr*) &serv_addr, sizeof(serv_addr));
    if (status < 0) {
        printf("\x1b[1;31mConnection to server failed\x1b[0m\n");
        return SERVER_ERROR;
    }

    SOCKET = soc;
    return ALL_GOOD;
}

static int sendData(char* data, unsigned int dataLenght) {
    // Allocate data block for first message containing next message length
    char* dataBlock1 = (char *) malloc(FIRST_MSG_LENGTH * sizeof(char));

    // Check if malloc failed
    if(dataBlock1 == NULL) return -1;

    // Fill string with spaces
    for(int i = 0; i < FIRST_MSG_LENGTH; i++) dataBlock1[i] = ' ';

    // Fill string with the length of the next message
    sprintf(dataBlock1, "%d", dataLenght);

    // Send first message over the socket wire
    int res = send(SOCKET, dataBlock1, FIRST_MSG_LENGTH, 0);
    if(res == -1) return -1;

    free(dataBlock1);

    // Send data over the socket wire
    int res2 = send(SOCKET, data, dataLenght, 0);
    if(res2 == -1) return -1;

    // Return succes
    return 1;
}

static int getServerResponse(char** string, int* stringLength, jsmntok_t* tokens, int nbTokens) {
    // Get data
    if(!getData(string, stringLength)) return -1;
    
    // Instanciate json parser
    jsmn_parser parser;
    jsmn_init(&parser);

    // Parse json string
    jsmn_parse(&parser, *string, *stringLength, tokens, nbTokens);

    // Get state infos
    int state = atoi(&(*string)[tokens[2].start]);
    
    // Print error if needed
    if(!state) {
        int blockLength = tokens[4].end - tokens[4].start;
        printf("\x1b[1;31mServer responded with following error:\x1b[0m \x1b[3m%.*s\x1b[23m\n", blockLength, (*string + tokens[4].start));
        return -1;
    }

    // Return succes
    return 1;
}

static int getData(char** string, int* stringLength) {
    // Allocate buffer to store data from read
    char buffer[FIRST_MSG_LENGTH] = { 0 };

    // Read incoming data on socket wire
    int res = read(SOCKET, buffer, FIRST_MSG_LENGTH - 1);
    if(res == -1) return -1;

    // First message contain the length of the next one
    *stringLength = atoi(buffer) + 1;

    // Allocate buffer of 0 based on the next message length
    char buffer2[*stringLength];
    memset(buffer2, 0, (*stringLength) * sizeof(char));

    // Read new incomming message on the socket wire
    int res2 = read(SOCKET, buffer2, *stringLength - 1);
    if(res2 == -1) return -1;
    
    // Copy recieved data to **string param to effectivly return the recieved string
    *string = (char *) malloc(*stringLength * sizeof(char));

    // Check if malloc failed
    if(*string == NULL) return -1;

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

    if(result == 0) {
        printf("\x1b[1;31mInvalid IP address\x1b[0m\n");
        return 0;
    } else if(result == -1) {
        printf("\x1b[1;31mAddress not supported\x1b[0m\n");
        return 0;
    } else return 1;
}