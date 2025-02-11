from typing import TypedDict

class GameSettings(TypedDict):
    gameType: int
    botId: int

    starter: int
    seed: int
    difficulty: int
    timeout: int

    reconnect: int