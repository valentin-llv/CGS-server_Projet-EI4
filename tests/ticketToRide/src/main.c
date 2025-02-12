#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "../../../client/src/api.h"

int main() {
    // cgs.valentin-lelievre.com
    int result = connectToCGS("cgs.valentin-lelievre.com", 15001);

    if(!result) return 1;

    if(!sendName("test")) return 1;

    while(1) {
        printf("Création d'une nouvelle partie\n");

        GameSettings gameSettings = GameSettingsDefaults;
        gameSettings.gameType = TRAINNING;
        gameSettings.botId = RANDOM_PLAYER;
        gameSettings.difficulty = 1;
        gameSettings.timeout = 15;
        gameSettings.starter = 2;
        gameSettings.seed = 0;
        gameSettings.reconnect = 0;

        GameData gameData = GameDataDefaults;
        int result = sendGameSettings(gameSettings, &gameData);
        if(result != ALL_GOOD) {
            printf("Error while creating game, error code: %d\n", result);

            return 1;
        }

        int whoPlays = gameData.starter;

        while(1) {
            if(whoPlays == 1) {
                printf("Waiting for opponent action\n");

                MoveData moveData;
                MoveResult moveResult;

                if(getMove(&moveData, &moveResult) != ALL_GOOD) break;

                printf("Opponent action: %d\n", moveData.action);

                free(moveResult.opponentMessage);
                free(moveResult.message);

                if(moveResult.state != NORMAL_MOVE) {
                    printf("Opponent loose\n");
                    break;
                }

                whoPlays = 0;
            } else {
                printBoard();

                MoveData moveData;
                
                // Ask user for action
                printf("Enter action: (0: CLAIM_ROUTE, 1: DRAW_BLIND_CARD, 2: DRAW_CARD, 3: DRAW_OBJECTIVES, 4: CHOOSE_OBJECTIVES)\n");
                scanf("%d", &moveData.action);

                moveData.action ++;

                switch (moveData.action) {
                    case CLAIM_ROUTE:
                        moveData.claimRoute.from = rand() % 10;
                        moveData.claimRoute.to = rand() % 10;
                        moveData.claimRoute.color = (CardColor)(rand() % 9);
                        moveData.claimRoute.nbLocomotives = rand() % 3;

                        printf("Claim route from %d to %d with color %d and %d locomotives\n", moveData.claimRoute.from, moveData.claimRoute.to, moveData.claimRoute.color, moveData.claimRoute.nbLocomotives);

                        break;
                    case DRAW_BLIND_CARD:
                        // No additional data needed
                        break;
                    case DRAW_CARD:
                        moveData.drawCard.card = (CardColor)(rand() % 5);

                        printf("Draw card %d\n", moveData.drawCard.card);

                        break;
                    case DRAW_OBJECTIVES:
                        // No additional data needed
                        break;
                    case CHOOSE_OBJECTIVES:
                        moveData.chooseObjectve.selectCard[0] = rand() % 2;
                        moveData.chooseObjectve.selectCard[1] = rand() % 2;
                        moveData.chooseObjectve.selectCard[2] = rand() % 2;

                        printf("Choose objectives %d %d %d\n", moveData.chooseObjectve.selectCard[0], moveData.chooseObjectve.selectCard[1], moveData.chooseObjectve.selectCard[2]);

                        break;
                    default:
                        break;
                }

                MoveResult moveResult;
                if(sendMove(&moveData, &moveResult) != ALL_GOOD) break;

                if(moveResult.state != NORMAL_MOVE) {
                    printf("You loose\n");
                    break;
                }

                if(moveResult.opponentMessage != NULL) {
                    printf("Opponent message: %s\n", moveResult.opponentMessage);
                    free(moveResult.opponentMessage);
                }

                free(moveResult.message);

                if(moveData.action == DRAW_OBJECTIVES) {
                    moveData.action = CHOOSE_OBJECTIVES;

                    moveData.chooseObjectve.selectCard[0] = rand() % 2;
                    moveData.chooseObjectve.selectCard[1] = rand() % 2;
                    moveData.chooseObjectve.selectCard[2] = rand() % 2;

                    printf("Choose objectives %d %d %d\n", moveData.chooseObjectve.selectCard[0], moveData.chooseObjectve.selectCard[1], moveData.chooseObjectve.selectCard[2]);

                    MoveResult moveResult;
                    if(sendMove(&moveData, &moveResult) != ALL_GOOD) break;

                    if(moveResult.state != NORMAL_MOVE) {
                        printf("You loose\n");
                        break;
                    }
                }
                
                whoPlays = 1;
            }
        }

        free(gameData.gameName);
        free(gameData.boardData);

        printf("La partie est finie, le joueur quitte la partie\n");
        if(!quitGame()) return 1;
    }

    return 0;
}