#include <stdio.h>
#include <stdlib.h>

#include "../../../client/src/api.h"

int main() {
    if(!connectToCGS("192.168.1.7", 8090)) return 1;
    if(!sendName("Valentin")) return 1;

    while(1) {
        printf("Création d'une nouvelle partie\n");

        GameSettings gameSettings = GameSettingsDefaults;
        gameSettings.gameType = TRAINNING;
        gameSettings.botName = RANDOM_PLAYER;
        gameSettings.start = 2;
        gameSettings.seed = 2002; // Seeds 2002 and 2003 are good seeds
        gameSettings.difficulty = 1;
        gameSettings.reconnect = 0;

        GameData gameData = GameDataDefaults;
        if(sendGameSettings(gameSettings, &gameData) != 0x40) {
            printf("Error while creating game\n");

            free(gameData.gameName);
            free(gameData.map);
            return 1;
        }

        printf("Game name: %s\n", gameData.gameName);

        int whoPlays = gameData.firstPlayer;

        while(1) {
            if(whoPlays == 1) {
                MoveData moveData = MoveDataDefaults;
                if(!getMove(&moveData)) break;

                printf("Opponent action: %d, opponent move: %d\n", moveData.action, moveData.direction);
                free(moveData.opponentMessage);

                if(moveData.action != NORMAL_MOVE) {
                    printf("Opponent loose\n");
                    break;
                }

                whoPlays = 2;
            } else {
                printBoard();

                unsigned int move;
                scanf("%d", &move);

                int moveType;
                if(!sendMove(move, &moveType)) break;
                printf("We play %d move\n", moveType);

                if(moveType != NORMAL_MOVE) {
                    printf("You loose\n");
                    break;
                }

                whoPlays = 1;
            }
        }

        free(gameData.gameName);
        free(gameData.map);

        printf("La partie est finie, le joueur quitte la partie\n");
        if(!quitGame()) return 1;
    }

    return 0;
}