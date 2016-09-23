from CatanBoard import *
from CatanAction import *

class Player:

    def __init__(self, name, seatNumber):

        self.name             = name
        self.seatNumber       = seatNumber
        self.resources        = [ 0 for i in range(0, len(g_resources))           ]
        self.developmentCards = [ 0 for i in range(0, len(g_developmentCards))    ]
        self.mayPlayDevCards  = [ False for i in range(0, len(g_developmentCards))]
        self.roads            = [ ]
        self.settlements      = [ ]
        self.cities           = [ ]
        self.biggestRoad      = False
        self.biggestArmy      = False
        self.numberOfPieces   = [ 0 for i in range(0, len(g_pieces))]
        self.knights          = 0
        self.playedDevCard    = False
        self.discardCardCount = 0

        self.firstSettlementBuild = False
        self.secondSettlementBuild = False
        self.firstRoadBuild = False
        self.secondRoadBuild = False

        self.rolledTheDices = False

    def GetVictoryPoints(self):

        devCardPoints = self.developmentCards[VICTORY_POINT_CARD_INDEX]

        constructionPoints = 0

        for i in range(0, len(self.settlements)):
            constructionPoints += 1

        for i in range(0, len(self.cities)):
            constructionPoints += 2

        achievementPoints = 0
        if self.biggestRoad:
            achievementPoints += 2
        if self.biggestArmy:
            achievementPoints += 2

        return devCardPoints + constructionPoints + achievementPoints

    def UpdateMayPlayDevCards(self, recentlyCardIndex = None, canUseAll = False):

        if canUseAll:

            for i in range(0, len(self.developmentCards)):

                self.mayPlayDevCards[i] = self.developmentCards[i] > 0

        else:

            if recentlyCardIndex is not None:

                for i in range(0, len(self.developmentCards)):

                    if int(recentlyCardIndex) == int(i):

                        self.mayPlayDevCards[i] = self.developmentCards[i] > 1

                    else:

                        self.mayPlayDevCards[i] = self.developmentCards[i] > 0

    def CanAfford(self, price):

        for i in range(0, len(g_resources)):
            if price[i] > self.resources[i]:
                return False

        return True

    def HavePiece(self, pieceIndex):

        if self.numberOfPieces[pieceIndex] > 0:
            return True

        return False

    def GetPorts(self, game):

        availablePorts = [ False for i in g_portType ]

        for settlementIndex in self.settlements:

            portType = game.gameState.boardNodes[settlementIndex].portType
            if portType is not None:
                availablePorts[g_portType.index(portType)] = True

        for cityIndex in self.cities:

            portType = game.gameState.boardNodes[cityIndex].portType
            if portType is not None:
                availablePorts[g_portType(portType)] = True

        return availablePorts

    def GetPossibleActions(self, game, player = None, gameState = None, ignoreTurn = False):
        pass

    def DoMove(self, game):
        pass

    def ChooseCardsToDiscard(self, game, player = None):
        pass

    def ChoosePlayerToStealFrom(self, game, player = None):
        pass

    def GetPossibleBankTrades(self, game, player = None):
        pass

    def GetMonopolyResource(self, game, player = None):
        pass

    def GetYearOfPlentyResource(self, game, player = None):
        pass