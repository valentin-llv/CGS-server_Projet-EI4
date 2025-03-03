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
#include <stdarg.h>
#include <errno.h>

// Socket headers
// Those libs are available on Linux (including WSL) and Mac but not Windows
// If you use windows you may want to use winsock.h and rename functions like inet_pton to match headers function names

#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>

// External JSON library
#include "lib/json.h"

// Game headers
#include "gameHeaders/ticketToRide.h"
#include "api.h"
/*

    Global vars

*/

int SOCKET = -1;     // socket descriptor
int DEBUG_LEVEL = NO_DEBUG;      // Set to 1 to enable debug mode, 0 to disable (use `extern int debug = 1;`)


/*

    Exposed functions

    Those are the function you can use to interact with the server

*/

// This is the first function you should call, it will connect you to the server.
// You need to provide the server address and the port to connect to.
// This is a blocking function, it will wait until the connection is established, it may take some time.

ResultCode connectToCGS(char* address, unsigned int port) {
    if(port<1000)
        return printError(__FUNCTION__, PARAM_ERROR, "Invalid port value");

    char* ipaddress = NULL;
    int adrType = 0;

    // Verify provided IP address and it's type: IPV4 or IPV6
    int ipVerificationResult = isValidIpAddress(address);

    if(ipVerificationResult <= 0) { 
        // Invalid IP, user might have used a domain name instead of an IP address
        ResultCode dnsResult = dnsSearch(address, &ipaddress, &adrType);

        if(dnsResult == ALL_GOOD) {
            char* addressTypeName = (char *) malloc(5 * sizeof(char));

            // Check if malloc failed
            if(addressTypeName == NULL)
                return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

            sprintf(addressTypeName, (adrType == AF_INET)? "IPv4": "IPv6");
            
            printDebugMessage(__FUNCTION__, MESSAGE, "Domain name %s resolved into an %s address: %s", address, addressTypeName, ipaddress);
            free(addressTypeName);
        } else {
            return printError(__FUNCTION__,PARAM_ERROR,  "Domain name %s failed to resolve into an IP address", address);
        }
    } else adrType = ipVerificationResult;

    /* connect to Socket */
    ResultCode res;
    if(ipaddress != NULL) {
        res = connectToSocket(ipaddress, port, adrType);
        free(ipaddress);
    }
    else {
        res = connectToSocket(address, port, adrType);
    }
    if (res == ALL_GOOD)
        printDebugMessage(__FUNCTION__, DEBUG, "Successfully connected to %s", address);
    return res;
}

// After connecting to the server you need to send your name to the server. It will be used to uniquely identify you.
// You need to provide your name as a string. It should be less than 90 characters long.

ResultCode sendName(char* name) {
    // Check user's provided data, max name length is 90 characters
    if(strlen(name) >= MAX_USERNAME_LENGTH)
        return printError(__FUNCTION__, PARAM_ERROR, "Name too long");

    // Parse data into json string
    char* data = (char *) malloc((MAX_USERNAME_LENGTH + 20) * sizeof(char));
    if(data == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    // Fill data with name
    int dataLength = sprintf(data, "{ 'name': '%s' }", name);

    // Send data and check for success
    if(sendData(data, dataLength) != ALL_GOOD)
        return printError(__FUNCTION__, SERVER_ERROR, "Failed to send data");

    free(data);
    
    // Get server acknowledgement
    char* string;
    jsmntok_t* tokens = (jsmntok_t *) malloc(SERVER_ACKNOWLEDGEMENT_JSON_SIZE * sizeof(jsmntok_t));

    // Check if malloc failed
    if(tokens == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    if(!getServerResponse(&string, tokens, SERVER_ACKNOWLEDGEMENT_JSON_SIZE))
        return printError(__FUNCTION__, SERVER_ERROR, "Server response failed");

    free(string);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

// After sending your name you need to send game settings to the server to start a game.
// You need to provide a GameSettings struct and a GameData struct to store the game data returned by the server.
// You can use the GameSettingsDefaults and GameDataDefaults variables to initialize the struct with default values.
// To fill the GameSettings struct you may want to use predefined constants available in api.h.

ResultCode sendGameSettings(GameSettings gameSettings, GameData* gameData) {
    // Check user's provided data
    if(gameSettings.gameType >= GamesTypesMax || gameSettings.gameType <= 0)
        return printError(__FUNCTION__, PARAM_ERROR, "Invalid game type");
    if(gameSettings.botId >= BotsNamesMax || gameSettings.botId <= 0)
        return printError(__FUNCTION__, PARAM_ERROR, "Invalid bot id");
    if(gameSettings.timeout > MAX_TIMEOUT || gameSettings.timeout < MIN_TIMEOUT)
        return printError(__FUNCTION__, PARAM_ERROR, "Invalid timeout value");
    if(gameSettings.starter != 0 && gameSettings.starter != 1 && gameSettings.starter != 2)
        return printError(__FUNCTION__, PARAM_ERROR, "Invalid starter value");
    if(gameSettings.seed > MAX_SEED)
        return printError(__FUNCTION__, PARAM_ERROR, "Invalid seed value");
    
    // Parse data into json string
    char* data = (char *) malloc(GAME_SETTINGS_MAX_JSON_LENGTH * sizeof(char));
    if(data == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR,"");

    int dataLength = verifyAndPackGameSettings(data, gameSettings);

    // Send data and check for success
    if(!sendData(data, dataLength))
        return printError(__FUNCTION__, SERVER_ERROR, "");
    free(data);

    // Get server acknowledgement
    char* string;
    jsmntok_t* tokens = (jsmntok_t *) malloc(GAME_SETTINGS_ACKNOWLEDGEMENT_JSON_SIZE * sizeof(jsmntok_t));
    if(tokens == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    if(!getServerResponse(&string, tokens, GAME_SETTINGS_ACKNOWLEDGEMENT_JSON_SIZE))
        return printError(__FUNCTION__, SERVER_ERROR, "Server response failed");

    // TODO create special unpack game settings function

    // Set struct from param to defaults values
    *gameData = GameDataDefaults;

    // Load received data into struct
    int blockLength = tokens[4].end - tokens[4].start + 1;
    char* gameName = (char *) malloc(blockLength * sizeof(char));
    if(gameName == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    sprintf(gameName, "%.*s", blockLength - 1, &string[tokens[4].start]);
    gameData->gameName = gameName;

    // Data is in specific order
    gameData->gameSeed = atoi(&string[tokens[6].start]);
    gameData->starter = atoi(&string[tokens[8].start]);
    gameData->nbElements = atoi(&string[tokens[14].start]);

    blockLength = tokens[16].end - tokens[16].start + 1;
    int* boardData = (int *) malloc(blockLength * sizeof(int));
    if(boardData == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    int i = 0; int j = 0;
    while((j + i) < blockLength - 1) {
        boardData[i] = atoi(&string[tokens[16].start + j + i]);
        j += getIntegerLength(boardData[i]);
        i ++;
    }

    gameData->boardData = boardData;

    int result = unpackGameSettingsData(string, tokens, gameData);
    if(result == -1)
        return printError(__FUNCTION__, OTHER_ERROR, "Failed to unpack game settings");

    free(string);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

// During a game this function is used to know what your opponent did during his turn.
// You need to provide an empty MoveData struct and an empty MoveResult struct to store the move data returned by the server.
// MoveData struct store the move your opponent did and MoveResult struct store the result of the move.

ResultCode getMove(MoveData* moveData, MoveResult* moveResult) {
    // Parse data into json string
    char* data = "{ 'action': 'getMove' }";

    // Send data and check for success
    if(!sendData(data, strlen(data)))
        return printError(__FUNCTION__, SERVER_ERROR, "Failed to send data");

    // Get server acknowledgement
    char* string;
    jsmntok_t* tokens = (jsmntok_t *) malloc(SEND_MOVE_RESPONSE_JSON_SIZE * sizeof(jsmntok_t));
    if(tokens == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    if(!getServerResponse(&string, tokens, SEND_MOVE_RESPONSE_JSON_SIZE))
        return printError(__FUNCTION__, SERVER_ERROR, "Server response failed");

    // Call the function related to the selected game to properly unpack the data
    int result = unpackGetMoveData(string, tokens, moveData, moveResult);

    if(result == -1)
        return printError(__FUNCTION__, OTHER_ERROR, "Failed to unpack move data");

    free(string);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

// During a game this function is used to send your move to the server.
// You need to provide a MoveData struct containing your move and an empty MoveResult struct to store the result of the move returned by the server.

ResultCode sendMove(MoveData* moveData, MoveResult* moveResult) {
    // Parse data into json string
    char* data = (char *) malloc(PACKED_DATA_MAX_SIZE * sizeof(char));
    if(data == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    // Call the function related to the selected game to properly pack the data
    int dataLength = packSendMoveData(data, moveData);
    if(dataLength == -1)
        return printError(__FUNCTION__, OTHER_ERROR, "Failed to send move data");

    // Send data and check for success
    if(!sendData(data, dataLength))
        return printError(__FUNCTION__, SERVER_ERROR, "Failed to send data");
    free(data);

    // Get server acknowledgement
    char* string;
    jsmntok_t* tokens = (jsmntok_t *) malloc(SEND_MOVE_RESPONSE_JSON_SIZE * sizeof(jsmntok_t));
    if(tokens == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    if(!getServerResponse(&string, tokens, SEND_MOVE_RESPONSE_JSON_SIZE))
        return printError(__FUNCTION__, SERVER_ERROR, "Server response failed");

    int result = unpackSendMoveResult(string, tokens, moveResult);
    if(result == -1)
        return printError(__FUNCTION__, OTHER_ERROR, "Failed to unpack move data");

    free(string);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

ResultCode getBoardState(BoardState* boardState) {
    // Parse data into json string
    char* data = "{ 'action': 'getBoardState' }";

    // Send data and check for success
    if(!sendData(data, strlen(data)))
        return printError(__FUNCTION__, SERVER_ERROR, "Failed to send data");

    // Get server acknowledgement
    char* string;
    jsmntok_t* tokens = (jsmntok_t *) malloc(BOARD_STATE_RESPONSE_JSON_SIZE * sizeof(jsmntok_t));
    if(tokens == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    if(!getServerResponse(&string, tokens, BOARD_STATE_RESPONSE_JSON_SIZE))
        return printError(__FUNCTION__, SERVER_ERROR, "Server response failed");

    // Call the function related to the selected game to properly unpack the data
    int result = unpackGetBoardState(string, tokens, boardState);
    if(result == -1)
        return printError(__FUNCTION__, OTHER_ERROR, "Failed to unpack board state");

    free(string);
    free(tokens);

    // Return success
    return ALL_GOOD;

}

// This function is used to send a message to your opponent during a game.
// You need to provide the message as a string. It should be less than 256 characters long.

ResultCode sendMessage(char* message) {
    // Check user's provided data
    if(strlen(message) >= MAX_MESSAGE_LENGTH)
        return printError(__FUNCTION__, PARAM_ERROR, "Message too long");

    // Parse data into json string
    char* data = (char *) malloc((MAX_MESSAGE_LENGTH + 50) * sizeof(char));
    if(data == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    int dataLength = sprintf(data, "{ 'action': 'sendMessage', 'message': '%s' }", message);

    // Send data and check for success
    if(!sendData(data, dataLength))
        return printError(__FUNCTION__, SERVER_ERROR, "Failed to send data");
    free(data);

    // Get server acknowledgement
    char* string;
    jsmntok_t* tokens = (jsmntok_t *) malloc(SERVER_ACKNOWLEDGEMENT_JSON_SIZE * sizeof(jsmntok_t));
    if(tokens == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    if(!getServerResponse(&string, tokens, SERVER_ACKNOWLEDGEMENT_JSON_SIZE))
        return printError(__FUNCTION__, SERVER_ERROR, "Server response failed");

    free(string);
    free(tokens);

    // Return success
    return ALL_GOOD;
}

// This function is used to display the game board during a game.
// It will print the colored board in the console.

ResultCode printBoard() {
    // Parse data into json string
    char* data = "{ 'action': 'displayGame' }";

    // Send data and check for success
    if(!sendData(data, strlen(data)))
        return printError(__FUNCTION__, SERVER_ERROR, "Failed to send data");

    // Get server acknowledgement
    char* string;
    jsmntok_t* tokens = (jsmntok_t *) malloc(SERVER_ACKNOWLEDGEMENT_JSON_SIZE * sizeof(jsmntok_t));
    if(tokens == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    if(!getServerResponse(&string, tokens, SERVER_ACKNOWLEDGEMENT_JSON_SIZE))
        return printError(__FUNCTION__, SERVER_ERROR, "Server response failed");

    int blockLength = atoi(&string[tokens[4].start]) + 1;
    char* buffer = (char *) malloc(blockLength * sizeof(char));
    if(buffer == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    // Fill buffer with 0
    memset(buffer, 0, blockLength * sizeof(char));

    // Read new incoming message on the socket wire
    int res = readNByte(&buffer, blockLength - 1);

    // Check for error
    if(res == -1)
        return printError(__FUNCTION__, OTHER_ERROR, "Failed to read data");

    // Print the board
    printf("%s\n", buffer);

    free(buffer);
    free(string);
    free(tokens);

    // Return success
    return ALL_GOOD;
}


// This function is used to quit the currently running game.
ResultCode quitGame() {
    // Parse data into json string
    char* data = "{ 'action': 'quitGame' }";

    // Send data and check for success
    if(!sendData(data, strlen(data)))
        return printError(__FUNCTION__, SERVER_ERROR, "Failed to send data");

    // Get server acknowledgement
    char* string;
    jsmntok_t* tokens = (jsmntok_t *) malloc(SERVER_ACKNOWLEDGEMENT_JSON_SIZE * sizeof(jsmntok_t));
    if(tokens == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    if(!getServerResponse(&string, tokens, SERVER_ACKNOWLEDGEMENT_JSON_SIZE))
        return printError(__FUNCTION__, SERVER_ERROR, "Server response failed");

    free(string);
    free(tokens);

    //TODO: close the socket !

    // Return success
    return ALL_GOOD;
}



/*

    Hidden functions

    Those are the functions used by the exposed functions to interact with the server
    You are not supposed to use them directly

*/

static ResultCode connectToSocket(const char *address, unsigned int port, unsigned int adrType) {
    int soc = socket(adrType, SOCK_STREAM, 0); // Use TCP socket
    if (soc < 0)
        return printError(__FUNCTION__, OTHER_ERROR, "Socket creation failed");

    struct sockaddr_in serv_addr;
    serv_addr.sin_family = adrType;
    serv_addr.sin_port = htons(port);

    int res = inet_pton(adrType, address, &serv_addr.sin_addr);
    if (res <= 0)
        return printError(__FUNCTION__, PARAM_ERROR, "Invalid address / address not supported");

    int status = connect(soc, (struct sockaddr*) &serv_addr, sizeof(serv_addr));
    if (status < 0)
        return printError(__FUNCTION__, SERVER_ERROR, "Connection to server failed: %s [code = %d]", strerror(errno), errno);

    SOCKET = soc;
    return ALL_GOOD;
}

static ResultCode dnsSearch(const char *domain, char** ipaddress, int* adrType) {
    // Do a DNS search to resolve domain name
    struct addrinfo* dnsResult = NULL;
    int result = getaddrinfo(domain, 0, 0, &dnsResult);

    if(result != 0)
        return printError(__FUNCTION__, OTHER_ERROR, "DNS search failed");

    // Get IP address type
    *adrType = dnsResult->ai_addr->sa_family;

    int adrSize = *adrType == AF_INET ? INET_ADDRSTRLEN : INET6_ADDRSTRLEN;
    *ipaddress = (char *) malloc(adrSize * sizeof(char));
    if(*ipaddress == NULL)
        return printError(__FUNCTION__, MEMORY_ALLOCATION_ERROR, "");

    // Convert IP address to string
    if(dnsResult->ai_addr->sa_family == AF_INET) { // IPV4 address found
        struct sockaddr_in *p = (struct sockaddr_in *) dnsResult->ai_addr;
        inet_ntop(AF_INET, &p->sin_addr, *ipaddress, adrSize);
    } else if (dnsResult->ai_addr->sa_family == AF_INET6) { // IPV6 address found
        struct sockaddr_in6 *p = (struct sockaddr_in6 *) dnsResult->ai_addr;
        inet_ntop(AF_INET6, &p->sin6_addr, *ipaddress, adrSize);
    }

    freeaddrinfo(dnsResult);
    return ALL_GOOD;
}

// return ALL_GOOD or OTHER_ERROR
static ResultCode sendData(const char *data, unsigned int dataLength) {
    // Allocate data block for first message containing next message length
    char* dataBlock1 = (char *) malloc(FIRST_MSG_LENGTH * sizeof(char));

    // Check if malloc failed
    if(dataBlock1 == NULL) return MEMORY_ALLOCATION_ERROR;

    // Fill string with spaces
    for(int i = 0; i < FIRST_MSG_LENGTH; i++)
        dataBlock1[i] = ' ';

    // Fill string with the length of the next message
    sprintf(dataBlock1, "%d", dataLength);

    // Send first message over the socket wire
    if(send(SOCKET, dataBlock1, FIRST_MSG_LENGTH, 0) == -1)
        return OTHER_ERROR;

    free(dataBlock1);

    // Send data over the socket wire
    if(send(SOCKET, data, dataLength, 0) == -1)
        return OTHER_ERROR;

    // Return success
    return ALL_GOOD;
}

static int getServerResponse(char** string, jsmntok_t* tokens, int nbTokens) {
    int stringLength;

    // Get data
    if(!getData(string, &stringLength)) return -1;
    
    // Instantiate json parser
    jsmn_parser parser;
    jsmn_init(&parser);

    // Parse json string
    jsmn_parse(&parser, *string, stringLength, tokens, nbTokens);

    // Get state infos
    int state = atoi(&(*string)[tokens[2].start]);
    
    // Print error if needed
    if(!state) {
        int blockLength = tokens[4].end - tokens[4].start;
        printError(__FUNCTION__, SERVER_ERROR, "Server responded with following error: %.*s\n", blockLength, (*string + tokens[4].start));
        return -1;
    }

    // Return success
    return 1;
}

static int getData(char** string, int* stringLength) {
    // Allocate buffer to store data from read
    char buffer[FIRST_MSG_LENGTH] = { 0 };

    // Read incoming data on socket wire
    int res = read(SOCKET, buffer, FIRST_MSG_LENGTH - 1);
    if(res <= 0) return -1; // Ensure it reads the correct amount of data

    // First message contain the length of the next one
    *stringLength = atoi(buffer) + 1;

    // Allocate buffer of 0 based on the next message length
    char* buffer2 = (char *) malloc(*stringLength * sizeof(char));

    // Check if malloc failed
    if(buffer2 == NULL) return -1;

    // Fill buffer with 0
    memset(buffer2, 0, (*stringLength) * sizeof(char));

    // Read new incoming message on the socket wire
    res = readNByte(&buffer2, *stringLength - 1);

    // Check for error
    if(res == -1) return -1;
    
    // Copy received data to **string param to effectively return the received string
    *string = (char *) malloc(*stringLength * sizeof(char));

    // Check if malloc failed
    if(*string == NULL) return -1;

    strcpy(*string, buffer2);

    // Return success
    return 1;
}

static int readNByte(char** buffer, int nbByte) {
    int totalRead = 0;
    while (totalRead < nbByte) {
        int res2 = read(SOCKET, *buffer + totalRead, nbByte - totalRead);
        totalRead += res2;

        // Check for error
        if (res2 <= 0) return -1;
    }

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

    // Assume IPV 4
    int result = inet_pton(AF_INET, ipAddress, &(sa.sin_addr));

    if(result == 1) return AF_INET;
    else if(result == 0) { // Incorrect IP address family
        // Try IPV 6
        result = inet_pton(AF_INET6, ipAddress, &(sa.sin_addr));

        if(result <= 0) return result; // Invalid IP
        else return AF_INET6;
    } else return result; // Invalid IP address format (IPV 4 or IPV 6)
}

/*

    Debug tools

*/

ResultCode printError(const char* function, ResultCode code, const char* message, ...) {
    /* print error code */
    switch(code) {
        case PARAM_ERROR:
            printf("\x1b[1;31m[%s] Invalid parameters\x1b[0m\n", function);
            break;
        case SERVER_ERROR:
            printf("\x1b[1;31m[%s] Server error\x1b[0m\n", function);
            break;
        case MEMORY_ALLOCATION_ERROR:
            printf("\x1b[1;31m[%s] Memory allocation failed\x1b[0m\n", function);
            break;
        case OTHER_ERROR:
            printf("\x1b[1;31m[%s] Unknown error\x1b[0m\n", function);
            break;
        default:
            printf("\x1b[1;31m[%s] Unknown error code\x1b[0m\n", function);
            break;
    }
    /* and extra message if given */
    if (*message) {
        va_list args;
        va_start(args, message);
        printf("\x1b[1;31m  > ");
        vprintf(message, args);
        printf("\x1b[0m\n");
        va_end(args);
    }
    /* stop on error */
    if (DEBUG_LEVEL < STOP_ON_ERROR)
        return code;
    exit(code);
}

void printDebugMessage(const char* function, const unsigned int level, const char* message, ...) {
    const static char* levelString[] = {"\x1b[1;30m", "\x1b[1;31m", "\x1b[1;32m", "\x1b[1;35m"};
    if(DEBUG_LEVEL>=level) {
        va_list args;
        va_start(args, message);
        printf("%s[%s] ", levelString[level], function);
        vprintf(message, args);
        printf("\x1b[0m\n");
        va_end(args);
    }
}