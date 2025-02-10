#ifndef SNAKE_H
#define SNAKE_H

// This define is used by the JSON library
#define JSMN_HEADER
#include "../lib/json.h"

/*

    Structs

*/

enum BotsNames {
    RANDOM_PLAYER = 0x1,
    TEST_PLAYER = 0x2,
    INTELLIGENT_PLAYER = 0x3,

    BotsNamesMax // Keep as last element
} BotsNames;

enum MoveDirections {
    UP = 0x0,
    RIGHT = 0x1,
    DOWN = 0x2,
    LEFT = 0x3,

    MovesMax // Keep as last element
};

typedef struct ActionData_ {
    unsigned int move;
} ActionData;

typedef struct MoveData_ {
    int action; // One of MoveState values
    int direction; // One of MoveDirections values
    char* opponentMessage; // String containing message send by the opponent
    char* message; // String containing message send by the server
} MoveData;

/*

    Constants

*/

static const unsigned int PACKED_DATA_MAX_SIZE = 400;

/*

    Functions prototypes

*/

extern void unpackGetMoveData(char* string, jsmntok_t* tokens, MoveData* moveData);
extern int packSendActionData(char* data, ActionData* actionData);

/*

    Functions definitions

*/

#ifndef ONLY_HEADERS

const MoveData MoveDataDefaults = { 0, 0, "", "" };

extern void unpackGetMoveData(char* string, jsmntok_t* tokens, MoveData* moveData) {
    // Load recieved data into struct
    moveData->action = atoi(&string[tokens[4].start]);
    moveData->direction = atoi(&string[tokens[6].start]);

    int blockLength = tokens[8].end - tokens[8].start + 1;
    char* opponentMessage = (char *) malloc(blockLength * sizeof(char));
    sprintf(opponentMessage, "%.*s", blockLength - 1, &string[tokens[8].start]);
    moveData->opponentMessage = opponentMessage;

    int blockLength2 = tokens[10].end - tokens[10].start + 1;
    char* message = (char *) malloc(blockLength2 * sizeof(char));
    sprintf(message, "%.*s", blockLength2 - 1, &string[tokens[10].start]);
    moveData->message = message;
}

extern int packSendActionData(char* data, ActionData* actionData) {
    if(actionData->move >= MovesMax) return -1;

    // Parse data into json string
    int dataLenght = sprintf(data, "{ 'action': 'sendMove', 'move': %d }", actionData->move);

    // Return succes
    return dataLenght;
}

#endif

#endif