/*

    Specific functions for the Ticket to Ride game.

    Require api.c, api.h, lib/json.h to works with.

    Authors: Valentin Le Lièvre
    Licence: GPL

    Copyright 2025 Valentin Le Lièvre

*/

#ifndef TICKET_TO_RIDE_H
#define TICKET_TO_RIDE_H

#include <stdio.h>
#include <stdlib.h>

// This define is used by the JSON library
#define JSMN_HEADER
#include "../lib/json.h"

/*

    Structs

*/

typedef enum {
    RANDOM_PLAYER = 0x1,
    NICE_BOT,

    BotsNamesMax // Keep as last element
} BotsNames;

typedef enum {
    CLAIM_ROUTE = 0x1,

    DRAW_BLIND_CARD, // Draw a card from the deck
    DRAW_CARD, // Draw a card from the visible cards

    DRAW_OBJECTIVES, // Draw 3 objectives
    CHOOSE_OBJECTIVES // Choose 1 to 3 objectives
} Action;

typedef enum {
	PURPLE,
	WHITE,
	BLUE,
	YELLOW,
	ORANGE,
	BLACK,
	RED,
	GREEN,
    
	LOCOMOTIVE
} CardColor;

typedef struct Objective_ {
    unsigned int from;
    unsigned int to;

    unsigned int score;
} Objective;

typedef struct ClaimRouteMove_ {
    unsigned int from;
    unsigned int to;

    CardColor color;
    unsigned int nbLocomotives;
} ClaimRouteMove;

typedef struct DrawCardMove_ {
    CardColor card;
} DrawCardMove;

typedef struct ChooseObjectiveMove_ {
    unsigned int selectCard[3]; // Set int to 0 to not take the i card or 1 take take it
} ChooseObjectiveMove;

typedef struct MoveData_ {
    Action action; // One of Actions values

    union {
        ClaimRouteMove claimRoute;
        DrawCardMove drawCard;
        ChooseObjectiveMove chooseObjectve;
    };
} MoveData;

typedef struct MoveResult_ {
    unsigned int state; // One of MoveState values

    union {
        CardColor card;
        Objective objectives[3];
    };

    char* opponentMessage; // String containing a message send by the opponent
    char* message; // String containing a message send by the server
} MoveResult;

/*

    Constants

*/

#define PACKED_DATA_MAX_SIZE 400

#define GET_MOVE_RESPONSE_JSON_SIZE 19
#define SEND_MOVE_RESPONSE_JSON_SIZE 29

/*

    Functions prototypes

*/

int unpackGetMoveData(char* string, jsmntok_t* tokens, MoveData* moveData, MoveResult* moveResult);
int packSendMoveData(char* data, MoveData* moveData);
int unpackSendMoveResult(char* string, jsmntok_t* tokens, MoveResult* moveResult);

/*

    Functions definitions

*/

#ifndef ONLY_HEADERS

int packSendMoveData(char* data, MoveData* moveData) {
    int dataLength = 0;

    switch (moveData->action) {
        case CLAIM_ROUTE:
            dataLength = sprintf(data, "{ 'action': 'sendMove', 'move': %d, 'from': %d, 'to': %d, 'color': %d, 'nbLocomotives': %d }",
                CLAIM_ROUTE, moveData->claimRoute.from, moveData->claimRoute.to, moveData->claimRoute.color, moveData->claimRoute.nbLocomotives);
            break;
        case DRAW_BLIND_CARD:
            dataLength = sprintf(data, "{ 'action': 'sendMove', 'move': %d }", DRAW_BLIND_CARD);
            break;
        case DRAW_CARD:
            dataLength = sprintf(data, "{ 'action': 'sendMove', 'move': %d, 'card': %d }", DRAW_CARD, moveData->drawCard.card);
            break;
        case DRAW_OBJECTIVES:
            dataLength = sprintf(data, "{ 'action': 'sendMove', 'move': %d }", DRAW_OBJECTIVES);
            break;
        case CHOOSE_OBJECTIVES:
            dataLength = sprintf(data, "{ 'action': 'sendMove', 'move': %d, 'selectCard': [%d, %d, %d] }",
                CHOOSE_OBJECTIVES, moveData->chooseObjectve.selectCard[0], moveData->chooseObjectve.selectCard[1], moveData->chooseObjectve.selectCard[2]);
            break;
        default:
            return -1;
    }

    return dataLength;
}

int unpackGetMoveData(char* string, jsmntok_t* tokens, MoveData* moveData, MoveResult* moveResult) {
    // Load received data into struct
    moveData->action = (Action) atoi(&string[tokens[4].start]);
    moveResult->state = (unsigned int) atoi(&string[tokens[6].start]);

    int blockLength = tokens[8].end - tokens[8].start + 1;
    char* opponentMessage = (char *) malloc(blockLength * sizeof(char));

    // Check if malloc failed
    if(opponentMessage == NULL) return -1;

    sprintf(opponentMessage, "%.*s", blockLength - 1, &string[tokens[8].start]);
    moveResult->opponentMessage = opponentMessage;;

    int blockLength2 = tokens[10].end - tokens[10].start + 1;
    char* message = (char *) malloc(blockLength2 * sizeof(char));

    // Check if malloc failed
    if(message == NULL) return -1;

    sprintf(message, "%.*s", blockLength2 - 1, &string[tokens[10].start]);
    moveResult->message = message;

    switch (moveData->action) {
        case CLAIM_ROUTE:
            moveData->claimRoute.from = atoi(&string[tokens[12].start]);
            moveData->claimRoute.to = atoi(&string[tokens[14].start]);
            moveData->claimRoute.color = (CardColor) atoi(&string[tokens[16].start]);
            moveData->claimRoute.nbLocomotives = atoi(&string[tokens[18].start]);
            break;
        case DRAW_CARD:
            moveData->drawCard.card = (CardColor) atoi(&string[tokens[12].start]);
            break;
        case CHOOSE_OBJECTIVES:
            moveData->chooseObjectve.selectCard[0] = (unsigned int) atoi(&string[tokens[12].start]);
            moveData->chooseObjectve.selectCard[1] = (unsigned int) atoi(&string[tokens[14].start]);
            moveData->chooseObjectve.selectCard[2] = (unsigned int) atoi(&string[tokens[16].start]);
            break;
        case DRAW_BLIND_CARD:
            // No additional data to unpack
            break;
        case DRAW_OBJECTIVES:
            // No additional data to unpack
            break;
        default:
            return -1;
    }

    // TODO: Fill the opponent move result data

    return 1;
}

int unpackSendMoveResult(char* string, jsmntok_t* tokens, MoveResult* moveResult) {
    moveResult->state = (Action) atoi(&string[tokens[2].start]);

    int blockLength = tokens[6].end - tokens[6].start + 1;
    char* opponentMessage = (char *) malloc(blockLength * sizeof(char));

    // Check if malloc failed
    if(opponentMessage == NULL) return -1;

    sprintf(opponentMessage, "%.*s", blockLength - 1, &string[tokens[6].start]);
    moveResult->opponentMessage = opponentMessage;

    int blockLength2 = tokens[8].end - tokens[8].start + 1;
    char* message = (char *) malloc(blockLength2 * sizeof(char));

    // Check if malloc failed
    if(message == NULL) return -1;

    sprintf(message, "%.*s", blockLength2 - 1, &string[tokens[8].start]);
    moveResult->message = message;

    switch (moveResult->state) {
        case DRAW_BLIND_CARD:
            moveResult->card = (CardColor) atoi(&string[tokens[10].start]);
            break;
        case DRAW_OBJECTIVES:
            for(int i = 0; i < 3; i++) {
                moveResult->objectives[i].from = atoi(&string[tokens[10 + (i * 6)].start]);
                moveResult->objectives[i].to = atoi(&string[tokens[12 + (i * 6)].start]);
                moveResult->objectives[i].score = atoi(&string[tokens[14 + (i * 6)].start]);
            }
            break;
        case CLAIM_ROUTE:
            // No additional data to unpack
            break;
        case CHOOSE_OBJECTIVES:
            // No additional data to unpack
            break;
        case DRAW_CARD:
            // No additional data to unpack
            break;
        default:
            return -1;
    }

    return 1;
}

#endif

#endif