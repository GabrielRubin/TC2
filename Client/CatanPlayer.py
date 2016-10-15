from CatanBoard import *
from CatanAction import *
import logging
import math

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
        self.numberOfPieces   = [ 15, 5, 4 ]
        self.knights          = 0
        self.playedDevCard    = False
        self.discardCardCount = 0

        self.firstSettlementBuild  = False
        self.secondSettlementBuild = False
        self.firstRoadBuild        = False
        self.secondRoadBuild       = False

        self.rolledTheDices        = False
        self.placedRobber          = False

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

    def GetStartingResources(self, gameState):

        for index in range(0, len(self.settlements)):

            settlement = gameState.boardNodes[self.settlements[index]]

            #its the second settlement
            if settlement.construction.index == 1:

                adjacentHexes = settlement.adjacentHexes

                for h in range(0, len(adjacentHexes)):

                    if adjacentHexes[h] is not None:

                        if gameState.boardHexes[adjacentHexes[h]].production is not None:

                            logging.info("{0} : STARTING RESOURCE >> GAIN 1 {1}".format(
                                self.name, gameState.boardHexes[adjacentHexes[h]].production))

                            self.resources[g_resources.index(gameState.boardHexes[adjacentHexes[h]].production)] += 1

    def UpdatePlayerResources(self, gameState, diceNumber = None):

        logging.info("UPDATING PLAYER {0} RESOURCES...".format(self.seatNumber))

        if diceNumber is not None:

            for s in range(0, len(self.settlements)):

                adjacentHexes = gameState.boardNodes[self.settlements[s]].adjacentHexes

                for h in range(0, len(adjacentHexes)):

                    if adjacentHexes[h] is not None and gameState.robberPos != adjacentHexes[h]:

                        if int(gameState.boardHexes[adjacentHexes[h]].number) == int(diceNumber):

                            if gameState.boardHexes[adjacentHexes[h]].production is not None:

                                logging.info("  >> GAIN 1 {0}".format(gameState.boardHexes[adjacentHexes[h]].production))

                                self.resources[g_resources.index(gameState.boardHexes[adjacentHexes[h]].production)] += 1

            for c in range(0, len(self.cities)):

                adjacentHexes = gameState.boardNodes[self.cities[c]].adjacentHexes

                for h in range(0, len(adjacentHexes)):

                    if adjacentHexes[h] is not None and gameState.robberPos != adjacentHexes[h]:

                        if int(gameState.boardHexes[adjacentHexes[h]].number) == int(diceNumber):

                            if gameState.boardHexes[adjacentHexes[h]].production is not None:

                                logging.info("  >> GAIN 2 {0}".format(gameState.boardHexes[adjacentHexes[h]].production))

                                self.resources[g_resources.index(gameState.boardHexes[adjacentHexes[h]].production)] += 2


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
                availablePorts[g_portType.index(portType)] = True

        return availablePorts

    def GetPossibleActions(self, game, player = None, gameState = None, ignoreTurn = False):
        pass

    def DoMove(self, game):
        pass

    def ChooseCardsToDiscard(self, game, player = None):
        pass

    def ChooseRobberPosition(self, game, player = None):
        pass

    def ChoosePlayerToStealFrom(self, game, player = None):
        pass

    def GetPossibleBankTrades(self, game, player = None):
        pass

    def GetMonopolyResource(self, game, player = None):
        pass

    def GetYearOfPlentyResource(self, game, player = None):
        pass

    def UpdateResourcesFromServer(self, action, element, value):

        if element in g_resources:  # RESOURCE

            if action == 'SET':
                self.resources[g_resources.index(element)] = value

            elif action == 'GAIN':
                self.resources[g_resources.index(element)] += value

            elif action == 'LOSE':

                if element == 'UNKNOWN':

                    resourceAmount = sum(self.resources) - value

                    self.resources[g_resources.index('UNKNOWN')] = resourceAmount

                    for index in range(len(self.resources) - 1):
                        self.resources[index] = 0
                else:
                    self.resources[g_resources.index(element)] -= value

            if self.resources[g_resources.index(element)] < 0:
                self.resources[g_resources.index('UNKNOWN')] += self.resources[g_resources.index(element)]
                self.resources[g_resources.index(element)] = 0

        elif element in g_pieces:  # PIECES

            if action == 'SET':
                self.numberOfPieces[g_pieces.index(element)] = value

            elif action == 'GAIN':
                self.numberOfPieces[g_pieces.index(element)] += value

            elif action == 'LOSE':
                self.numberOfPieces[g_pieces.index(element)] -= value

        elif element == 'KNIGHTS':  # KNIGHTS

            if action == 'SET':
                self.knights = value

            elif action == 'GAIN':
                self.knights += value

            elif action == 'LOSE':
                self.knights -= value

    def Build(self, gameState, pieceType, position):

        if pieceType == 'ROAD':

            newConstruction = Construction(g_constructionTypes[0],
                                           self.seatNumber, len(self.roads), position)

            gameState.boardEdges[position].construction = newConstruction

            gameState.constructableEdges.remove(gameState.boardEdges[position])

            self.roads.append(position)

            self.numberOfPieces[0] -= 1

        elif pieceType == 'SETTLEMENT':

            newConstruction = Construction(g_constructionTypes[1],
                                           self.seatNumber, len(self.settlements), position)

            gameState.boardNodes[position].construction = newConstruction

            gameState.constructableNodes.remove(gameState.boardNodes[position])

            self.settlements.append(position)

            self.numberOfPieces[1] -= 1

        elif pieceType == 'CITY':

            newConstruction = Construction(g_constructionTypes[2],
                                           self.seatNumber, len(self.cities), position)

            gameState.boardNodes[position].construction = newConstruction

            self.settlements.remove(position)

            self.cities.append(position)

            self.numberOfPieces[1] += 1

            self.numberOfPieces[2] -= 1

    def PlaceRobber(self, gameState, position):

        gameState.robberPos = position

        self.placedRobber = True

    def StartTurn(self):

        self.placedRobber   = False

        self.rolledTheDices = False

    def CountRoads(self, gameState):

        startingRoads = []

        for road in self.roads:

            isStartPos = False

            for adjacentEdge in gameState.boardEdges[road].adjacentEdges:

                if adjacentEdge is None:
                    continue

                if gameState.boardEdges[adjacentEdge].construction is None or \
                    gameState.boardEdges[adjacentEdge].construction.owner != self.seatNumber:
                        startingRoads.append(road)
                        isStartPos = True
                        break

            if isStartPos:
                continue

            for adjacentNode in gameState.boardEdges[road].adjacentNodes:

                if adjacentNode is None:
                    continue

                if gameState.boardNodes[adjacentNode].construction is not None and \
                    gameState.boardNodes[adjacentNode].construction.owner != self.seatNumber:
                    startingRoads.append(road)
                    break

        def DepthSearch(playerNumber, currRoad, length, visited):

            # Already visited?
            if currRoad in visited:
                return length
            # Is None or don't belong to the player?
            if gameState.boardEdges[currRoad].construction is None or \
                gameState.boardEdges[currRoad].construction.owner != playerNumber:
                return length
            # Is adjacent to another player's settlement/city?
            for node in gameState.boardEdges[currRoad].adjacentNodes:
                if gameState.boardNodes[node] is not None and \
                   gameState.boardNodes[node].construction is not None and \
                   gameState.boardNodes[node].construction.owner != playerNumber:
                    return length

            length += 1

            visited.append(currRoad)

            possiblePaths = [DepthSearch(playerNumber, nextRoad, length, visited) if
                             gameState.boardEdges[currRoad] is not None else -1 for
                             nextRoad in gameState.boardEdges[currRoad].adjacentEdges]

            if len(possiblePaths) <= 0:
                return 0

            return max(possiblePaths)

        results = []

        for startingRoad in startingRoads:
            for nextEdge in gameState.boardEdges[startingRoad].adjacentEdges:
                results.append(DepthSearch(self.seatNumber, nextEdge, 1, [startingRoad]))

        if len(results) <= 0:
            return 0

        return max(results)

    def DefaultDiscard(self):
        #ROBOT PLAYER DEFAULT DISCARD METHOD
        if sum(self.resources) > 7:
            # SET THE NEW RESOURCES AS UNKNOWN - (WE CANT KNOW WHAT RESOURCES THE ROBOT HAVE DISCARDED)
            self.resources = [0, 0, 0, 0, 0, int(math.ceil(sum(self.resources) / 2.0))]