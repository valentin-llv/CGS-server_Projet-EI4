#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "../../../client/src/api.h"

int main() {
    if(!connectToCGS("192.168.1.7", 8090)) return 1;
    if(!sendName("test")) return 1;

    while(1) {
        printf("Création d'une nouvelle partie\n");

        GameSettings gameSettings = GameSettingsDefaults;
        gameSettings.gameType = TRAINNING;
        gameSettings.botId = RANDOM_PLAYER;
        gameSettings.starter = 2;
        gameSettings.seed = 2002; // Seeds 2002 and 2003 are good seeds
        gameSettings.difficulty = 1;
        gameSettings.reconnect = 0;

        GameData gameData = GameDataDefaults;
        if(sendGameSettings(gameSettings, &gameData) != 0x40) {
            printf("Error while creating game\n");

            free(gameData.gameName);
            free(gameData.boardData);
            return 1;
        }

        printf("Game name: %s\n", gameData.gameName);

        int whoPlays = gameData.starter;
        srand(time(NULL));

        while(1) {
            if(whoPlays == 1) {
                MoveData moveData;
                MoveResult moveResult;
                if(getMove(&moveData, &moveResult) != 0x40) break;

                printf("Opponent action: %d\n", moveData.action);
                free(moveResult.opponentMessage);
                free(moveResult.message);

                if(moveResult.action != NORMAL_MOVE) {
                    printf("Opponent loose\n");
                    break;
                }

                whoPlays = 2;
            } else {
                printBoard();

                MoveData moveData;
                // moveData.action = (Action)(rand() % 5 + 1); // Random action between 1 and 5
                moveData.action = DRAW_CARD;

                printf("We play action %d\n", moveData.action);

                switch (moveData.action) {
                    case CLAIM_ROUTE:
                        moveData.claimRoute.from = rand() % 10;
                        moveData.claimRoute.to = rand() % 10;
                        moveData.claimRoute.color = (CardColor)(rand() % 9);
                        moveData.claimRoute.nbLocomotives = rand() % 3;
                        break;
                    case DRAW_BLIND_CARD:
                        // No additional data needed
                        break;
                    case DRAW_CARD:
                        moveData.drawCard.card = (CardColor)(rand() % 5);
                        break;
                    case DRAW_OBJECTIVES:
                        // No additional data needed
                        break;
                    case CHOOSE_OBJECTIVES:
                        moveData.chooseObjectve.selectCard[0] = rand() % 2;
                        moveData.chooseObjectve.selectCard[1] = rand() % 2;
                        moveData.chooseObjectve.selectCard[2] = rand() % 2;
                        break;
                    default:
                        break;
                }

                printf("Match case passed\n");

                MoveResult moveResult;
                if(sendMove(&moveData, &moveResult) != 0x40) break;
                printf("Send move\n");

                printf("We play action %d\n", moveData.action);

                if(moveResult.action != NORMAL_MOVE) {
                    printf("You loose\n");
                    break;
                }

                free(moveResult.opponentMessage);
                free(moveResult.message);

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