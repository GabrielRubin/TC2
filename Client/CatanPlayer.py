from CatanBoard import *

class Player:

    def __init__(self, name, seatNumber):

        self.name                 = name
        self.seatNumber           = seatNumber
        self.resources            = [ 0 for i in range(0, len(g_resources) - 2)    ]
        self.developmentCards     = [ 0 for i in range(0, len(g_developmentCards)) ]
        self.constructions        = [ ]
        self.biggestRoad          = False
        self.biggestArmy          = False
        self.availableRoads       = 15
        self.availableSettlements = 5
        self.availableCities      = 4

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
