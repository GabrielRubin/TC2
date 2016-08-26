import random
from CatanBoard import *

class Game:

    def __init__(self, gameState):

        self.gameState = gameState

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