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

    def GetPossibleActions(self, game, playerNumber, gameState, ignoreTurn = False):
        pass

    def DoMove(self, game):
        pass

    def ChooseCardsToDiscard(self, game):
        pass

    def ChoosePlayerToStealFrom(self, game):
        pass

class AgentRandom(Player):

    def GetPossibleActions(self, game, player = None, gameState = None, ignoreTurn = False):

        if player is None:
            player = self

        if gameState is None:
            gameState = game.gameState

        #if player not in gameState.players:
        #    logging.critical("PLAYER NOT IN GAME!!!!!\n CurrentPlayers : {0}\n I am: {1}".format(gameState.players, player))
        #    return None

        if not ignoreTurn and gameState.currPlayer != player.seatNumber:
            logging.critical("ITS NOT THIS PLAYER'S TURN!!!!")
            return None

        if   gameState.currState == 'START1A':

            possibleSettlements = game.GetPossibleSettlements(gameState, player, True)

            def RateNode(node, uniqueness):

                possibleResources = [gameState.boardHexes[boardHex].production for boardHex in node.GetAdjacentHexes()
                                     if boardHex is not None]

                if len(possibleResources) < 2:
                    return False

                seen   = []
                unique = 0

                for i in range(0, len(possibleResources)):
                    if possibleResources[i] is not None:
                        if possibleResources[i] not in seen:
                            unique += 1
                        seen.append(possibleResources[i])

                if unique < uniqueness:
                    return False

                return True

            for i in range(0, 3):

                goodNodes = [ setNode for setNode in possibleSettlements if RateNode(setNode, 3 - i) ]

                if len(goodNodes) > 0:
                    break

            return [BuildSettlementAction(player.seatNumber, setNode.index, len(player.settlements))
                    for setNode in goodNodes]

        elif gameState.currState == 'START1B':

            possibleRoads = game.GetPossibleRoads(gameState, player, True)

            return [BuildRoadAction(player, roadEdge.index, len(player.roads)) for roadEdge in possibleRoads]

        elif gameState.currState == 'START2A':

            possibleSettlements = game.GetPossibleSettlements(gameState, player, True)

            def RateNode(node, ownedResources, uniqueness):

                possibleResources = [gameState.boardHexes[boardHex].production for boardHex in node.GetAdjacentHexes()
                                     if boardHex is not None]

                if len(possibleResources) < 2:
                    return False

                seen = []
                unique = 0

                for i in range(0, len(possibleResources)):
                    if possibleResources[i] is not None:
                        if possibleResources[i] not in seen \
                                and possibleResources[i] not in ownedResources:
                            unique += 1
                        seen.append(possibleResources[i])

                if unique < uniqueness:
                    return False

                return True

            for i in range(0, 3):

                goodNodes = [ setNode for setNode in possibleSettlements if RateNode(setNode, player.resources, 3 - i) ]

                if len(goodNodes) > 0:
                    break

            return [BuildSettlementAction(player.seatNumber, setNode.index, len(player.settlements))
                    for setNode in goodNodes]

        elif gameState.currState == 'START2B':

            possibleRoads = game.GetPossibleRoads(gameState, player, True)

            return [BuildRoadAction(player, roadEdge.index, len(player.roads)) for roadEdge in possibleRoads]

        elif gameState.currState == 'PLAY':

            # roll the dices!
            return [ RollDicesAction(player) ]

        elif gameState.currState == 'PLAY1':

            # TODO > here is agent gameplay...

            possibleActions = []

            # TODO > all actions have a request message, implement that...
            possibleRoads       = game.GetPossibleRoads(gameState, player)
            possibleSettlements = game.GetPossibleSettlements(gameState, player)
            possibleCities      = game.GetPossibleCities(gameState, player)

            if possibleRoads is not None:
                possibleActions += [BuildRoadAction(player, roadEdge.index, len(player.roads))
                                    for roadEdge in possibleRoads]
            if possibleSettlements is not None and len(possibleSettlements) > 0:
                possibleActions = [BuildSettlementAction(player.seatNumber, setNode.index, len(player.settlements))
                                    for setNode in possibleSettlements]
            if possibleCities is not None and len(possibleCities) > 0:
                possibleActions = [ BuildCityAction(player.seatNumber, setNode.index, len(player.cities))
                                     for setNode in possibleCities]

            return possibleActions

        elif gameState.currState == 'PLACING_ROBBER':

            # Rolled out 7  * or *  Used a knight card
            return game.GetPossibleRobberPositions(gameState, player)

        elif gameState.currState == 'WAITING_FOR_DISCARDS':

            return [self.ChooseCardsToDisard(game, player)]

        elif gameState.currState == 'WAITING_FOR_CHOICE':

            pass

        elif gameState.currState == 'WAITING_FOR_DISCOVERY':

            pass

        elif gameState.currState == 'WAITING_FOR_MONOPOLY':

            pass

        return None

    def DoMove(self, game):

        if game.gameState.currPlayer != self.seatNumber:
            return None

        possibleActions = self.GetPossibleActions(game)

        logging.debug("possible actions = {0}".format(possibleActions))

        if game.gameState.currState == "PLAY1":

            if possibleActions is not None and len(possibleActions) > 0:
                return random.choice(possibleActions)

            return EndTurnAction(self.seatNumber)

        if possibleActions is not None and len(possibleActions) > 0:
            return random.choice(possibleActions)

        return None

    def ChooseCardsToDiscard(self, game, player = None):

        if player is None:
            player = self

        if len(player.resources) > 7:
            return None

        resourcesPopulation = [0 for i in range(0, player.resources[0])] + [1 for j in range(0, player.resources[1])] + \
                              [2 for k in range(0, player.resources[2])] + [3 for l in range(0, player.resources[3])] + \
                              [4 for m in range(0, player.resources[4])] + [5 for n in range(0, player.resources[5])]

        discardCardCount = int(math.floor(len(resourcesPopulation) / 2))

        if discardCardCount > 0:
            assert (player.discardCardCount == discardCardCount, "calculated cards to discard different from server!")
            player.discardCardCount = 0

        selectedResources = random.sample(resourcesPopulation, discardCardCount)

        return DiscardResourcesAction(player.seatNumber, [selectedResources.count(0), selectedResources.count(1),
                                                          selectedResources.count(2), selectedResources.count(3),
                                                          selectedResources.count(4), selectedResources.count(5)])

    def ChoosePlayerToStealFrom(self, game, player = None):

        if player is None:
            player = self

        robberHex       = game.gameState.boardHexes[game.gameState.robberPos]

        possibleNodes   = [game.gameState.boardNodes[nodeIndex] for nodeIndex in robberHex.GetAdjacentNodes()]

        possiblePlayers = []

        for node in possibleNodes:
            if node.construction is not None and node.construction.owner not in possiblePlayers:
                possiblePlayers.append(node.construction.owner)

        if len(possiblePlayers) > 0:
            return ChoosePlayerToStealFromAction(player.seatNumber, random.choice(possiblePlayers))

        return None