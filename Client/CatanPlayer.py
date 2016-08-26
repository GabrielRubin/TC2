from CatanBoard import *

class Player:

    def __init__(self, name):

        self.name             = name
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
