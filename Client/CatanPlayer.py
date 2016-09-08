from CatanBoard import *
from CatanAction import *
import random
import logging
import math

class Player:

    def __init__(self, name, seatNumber):

        self.name             = name
        self.seatNumber       = seatNumber
        self.resources        = [ 0 for i in range(0, len(g_resources))        ]
        self.developmentCards = [ 0 for i in range(0, len(g_developmentCards)) ]
        self.roads            = [ ]
        self.settlements      = [ ]
        self.cities           = [ ]
        self.biggestRoad      = False
        self.biggestArmy      = False
        self.numberOfPieces   = [ 0 for i in range(0, len(g_pieces))]
        self.knights          = 0
        self.canPlayDevCard   = False
        self.discardCardCount = 0

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

    def CanAfford(self, price):

        for i in range(0, len(g_resources)):
            if price[i] > self.resources[i]:
                return False

        return True

    def HavePiece(self, pieceIndex):

        if self.numberOfPieces[pieceIndex] > 0:
            return True

        return False

    def DoMove(self, game):
        pass

    def ChooseCardsToDiscard(self, game):
        pass

    def ChoosePlayerToStealFrom(self, game):
        pass

class AgentRandom(Player):

    def DoMove(self, game):

        if game.gameState.currPlayer != self.seatNumber:
            return None

        possibleActions = game.GetPossibleActions(self)

        logging.debug("possible actions = {0}".format(possibleActions))

        if possibleActions is not None and len(possibleActions) > 0:
            return random.choice(possibleActions)

        if game.gameState.currState == "PLAY1":
            return EndTurnAction(self.seatNumber)

        return None

    def ChooseCardsToDiscard(self, game):

        resourcesPopulation = [0 for i in range(0, self.resources[0])] + [1 for j in range(0, self.resources[1])] + \
                              [2 for k in range(0, self.resources[2])] + [3 for l in range(0, self.resources[3])] + \
                              [4 for m in range(0, self.resources[4])] + [5 for n in range(0, self.resources[5])]

        discardCardCount = int(math.floor(len(resourcesPopulation) / 2))

        if discardCardCount > 0:
            assert (self.discardCardCount == discardCardCount, "calculated cards to discard different from server!")
            self.discardCardCount = 0

        selectedResources = random.sample(resourcesPopulation, discardCardCount)

        return DiscardResourcesAction(self.seatNumber, [selectedResources.count(0), selectedResources.count(1),
                                                        selectedResources.count(2), selectedResources.count(3),
                                                        selectedResources.count(4), selectedResources.count(5)])

    def ChoosePlayerToStealFrom(self, game):

        robberHex       = game.gameState.boardHexes[game.gameState.robberPos]

        possibleNodes   = robberHex.GetAdjacentNodes()

        possiblePlayers = []

        for node in possibleNodes:
            if node.construction is not None and node.construction.owner not in possiblePlayers:
                possiblePlayers.append(node.construction.owner)

        if len(possiblePlayers) > 0:
            return random.choice(possiblePlayers)

        return None