from CatanBoard import *
import random
import logging

class Player:

    def __init__(self, name, seatNumber):

        self.name                 = name
        self.seatNumber           = seatNumber
        self.resources            = [ 0 for i in range(0, len(g_resources))        ]
        self.developmentCards     = [ 0 for i in range(0, len(g_developmentCards)) ]
        self.roads                = [ ]
        self.settlements          = [ ]
        self.cities               = [ ]
        self.biggestRoad          = False
        self.biggestArmy          = False
        self.numberOfPieces       = [ 0 for i in range(0, len(g_pieces))]
        self.knights              = 0
        self.canPlayDevCard       = False

    def GetVictoryPoints(self):

        devCardPoints      = self.developmentCards[0]

        constructionPoints = 0
        for settlement in self.settlements:
            constructionPoints += settlement.victoryPoints

        for city in self.cities:
            constructionPoints += city.victoryPoints

        achievementPoints = 0
        if self.biggestRoad:
            achievementPoints += 2
        if self.biggestArmy:
            achievementPoints += 2

        return devCardPoints + constructionPoints + achievementPoints

    def DoMove(self, game):
        pass


class AgentRandom(Player):

    def DoMove(self, game):

        possibleActions = game.GetPossibleActions(self)

        logging.debug("possible actions = {0}".format(possibleActions))

        if possibleActions is not None and len(possibleActions) > 0:
            return random.choice(possibleActions)

        return None