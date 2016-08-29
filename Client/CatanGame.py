import random
from CatanBoard import *
from JSettlersMessages import *

class Game:

    def __init__(self, gameState):

        self.gameState = gameState

    def CreateBoard(self, message):

        self.gameState.boardHexes[0x37].resource = message.hexes[5]
        self.gameState.boardHexes[0x37].number   = messageNumberToGameNumber[message.numbers[5]]
        self.gameState.boardHexes[0x59].resource = message.hexes[6]
        self.gameState.boardHexes[0x59].number   = messageNumberToGameNumber[message.numbers[6]]
        self.gameState.boardHexes[0x7b].resource = message.hexes[7]
        self.gameState.boardHexes[0x7b].number   = messageNumberToGameNumber[message.numbers[7]]
        self.gameState.boardHexes[0x35].resource = message.hexes[10]
        self.gameState.boardHexes[0x35].number   = messageNumberToGameNumber[message.numbers[10]]
        self.gameState.boardHexes[0x57].resource = message.hexes[11]
        self.gameState.boardHexes[0x57].number   = messageNumberToGameNumber[message.numbers[11]]
        self.gameState.boardHexes[0x79].resource = message.hexes[12]
        self.gameState.boardHexes[0x79].number   = messageNumberToGameNumber[message.numbers[12]]
        self.gameState.boardHexes[0x9b].resource = message.hexes[13]
        self.gameState.boardHexes[0x9b].number   = messageNumberToGameNumber[message.numbers[13]]
        self.gameState.boardHexes[0x33].resource = message.hexes[16]
        self.gameState.boardHexes[0x33].number   = messageNumberToGameNumber[message.numbers[16]]
        self.gameState.boardHexes[0x55].resource = message.hexes[17]
        self.gameState.boardHexes[0x55].number   = messageNumberToGameNumber[message.numbers[17]]
        self.gameState.boardHexes[0x77].resource = message.hexes[18]
        self.gameState.boardHexes[0x77].number   = messageNumberToGameNumber[message.numbers[18]]
        self.gameState.boardHexes[0x99].resource = message.hexes[19]
        self.gameState.boardHexes[0x99].number   = messageNumberToGameNumber[message.numbers[19]]
        self.gameState.boardHexes[0xbb].resource = message.hexes[20]
        self.gameState.boardHexes[0xbb].number   = messageNumberToGameNumber[message.numbers[20]]
        self.gameState.boardHexes[0x53].resource = message.hexes[23]
        self.gameState.boardHexes[0x53].number   = messageNumberToGameNumber[message.numbers[23]]
        self.gameState.boardHexes[0x75].resource = message.hexes[24]
        self.gameState.boardHexes[0x75].number   = messageNumberToGameNumber[message.numbers[24]]
        self.gameState.boardHexes[0x97].resource = message.hexes[25]
        self.gameState.boardHexes[0x97].number   = messageNumberToGameNumber[message.numbers[25]]
        self.gameState.boardHexes[0xb9].resource = message.hexes[26]
        self.gameState.boardHexes[0xb9].number   = messageNumberToGameNumber[message.numbers[26]]
        self.gameState.boardHexes[0x73].resource = message.hexes[29]
        self.gameState.boardHexes[0x73].number   = messageNumberToGameNumber[message.numbers[29]]
        self.gameState.boardHexes[0x95].resource = message.hexes[30]
        self.gameState.boardHexes[0x95].number   = messageNumberToGameNumber[message.numbers[30]]
        self.gameState.boardHexes[0xb7].resource = message.hexes[31]
        self.gameState.boardHexes[0xb7].number   = messageNumberToGameNumber[message.numbers[31]]

    def GetDiceRoll(self):

        return random.randint(1, 6) + random.randint(1, 6)

    def GetPossibleActions(self, player):
        pass

class GameState:

    def __init__(self):

        self.boardHexes = [ BoardHex(hexIndex)   for hexIndex  in g_boardHexes ]
        self.boardNodes = [ BoardNode(nodeIndex) for nodeIndex in g_boardNodes ]
        self.boardEdges = [ BoardEdge(edgeIndex) for edgeIndex in g_boardEdges ]

        self.currPlayer = 0
        self.currRound  = 0
        self.players    = []

    def GetNextState(self, action):
        pass

class Action:

    def __init__(self):
        pass