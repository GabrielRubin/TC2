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

class Player:

    def __init__(self):

        self.resources        = [ 0 for i in range(0, len(g_resources) - 2)    ]
        self.developmentCards = [ 0 for i in range(0, len(g_developmentCards)) ]
        self.constructions    = [ ]
        self.biggestRoad      = False
        self.biggestArmy      = False

    def GetVictoryPoints(self):

        devCardPoints      = self.developmentCards[0]

        constructionPoints = 0
        for construction in self.constructions:
            constructionPoints += construction.victoryPoints

        achievementPoints = 0
        if self.biggestRoad:
            achievementPoints += 2
        if self.biggestArmy:
            achievementPoints += 2

        return devCardPoints + constructionPoints + achievementPoints

class Action:

    def __init__(self):
        pass