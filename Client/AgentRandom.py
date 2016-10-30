from CatanPlayer import *
import random
import logging
import math
from CatanUtils import GetRandomBankTrade

class AgentRandom(Player):

    def __init__(self, name, seatNumber):

        super(AgentRandom, self).__init__(name, seatNumber)

        self.agentName = "RANDOM"

    def GetPossibleActions(self, gameState, player = None):

        if player is None:
            player = self

        if not gameState.setupDone:
            return self.PossibleActionsSetupTurns(gameState, player)
        elif gameState.currState == "PLAY" or gameState.currState == "PLAY1":
            return self.PossibleActionsRegularTurns(gameState, player)
        else:
            return self.PossibleActionsSpecial(gameState, player)

        return None

    def PossibleActionsSetupTurns(self, gameState, player = None):

        if   gameState.currState == 'START1A':

            if player.firstSettlementBuild:
                return None

            def IsNodeGood(node):
                total = 0
                for hexIndex in gameState.boardNodes[node].adjacentHexes:
                    if gameState.boardHexes[hexIndex].production is not None:
                        total += 1
                return total > 1

            bestSettlements = filter(IsNodeGood, gameState.GetPossibleSettlements(player, True))

            possible = [BuildSettlementAction(player.seatNumber, setNode, len(player.settlements))
                        for setNode in bestSettlements]

            return possible

        elif gameState.currState == 'START1B':

            if player.firstRoadBuild:
                return None

            possibleRoads = gameState.GetPossibleRoads(player, True)

            #possibleRoads = [gameState.boardEdges[edge] for edge in self.possibleRoads]

            return [BuildRoadAction(player.seatNumber, roadEdge, len(player.roads)) for roadEdge in possibleRoads]

        elif gameState.currState == 'START2A':

            if player.secondSettlementBuild:
                return None

            def IsNodeGood(node):
                total = 0
                for hexIndex in gameState.boardNodes[node].adjacentHexes:
                    if gameState.boardHexes[hexIndex].production is not None:
                        total += 1
                return total > 1

            bestSettlements = filter(IsNodeGood, gameState.GetPossibleSettlements(player, True))

            return [BuildSettlementAction(player.seatNumber, setNode, len(player.settlements))
                    for setNode in bestSettlements]

        elif gameState.currState == 'START2B':

            if player.secondRoadBuild:
                return None

            possibleRoads = gameState.GetPossibleRoads(player, True)

            return [BuildRoadAction(player.seatNumber, roadEdge, len(player.roads)) for roadEdge in possibleRoads]

    actions = ('buildRoad', 'buildSettlement', 'buildCity',
               'buyDevCard', 'useDevCard')

    def PossibleActionsRegularTurns(self, gameState, player):

        if gameState.currState == 'PLAY':

            # FIXME: TRYING TO USE KNIGHT 2 TIMES!!! WHAT??? (fixed?)

            if not player.rolledTheDices and \
               not player.playedDevCard and \
                    player.mayPlayDevCards[KNIGHT_CARD_INDEX] and \
                            player.developmentCards[KNIGHT_CARD_INDEX] > 0:

                return [UseKnightsCardAction( player.seatNumber, None, None )]

            if not player.rolledTheDices:

                return [RollDicesAction( player.seatNumber )]

        elif gameState.currState == 'PLAY1':

            possibleActions     = []

            if player.HavePiece(g_pieces.index('ROADS')) and \
                player.CanAfford(BuildRoadAction.cost):

                possibleActions.append(AgentRandom.actions[0])

            if player.HavePiece(g_pieces.index('SETTLEMENTS')) and \
                player.CanAfford(BuildSettlementAction.cost):

                possibleActions.append(AgentRandom.actions[1])

            if len(player.settlements) > 0 and\
                player.HavePiece(g_pieces.index('CITIES')) and\
                player.CanAfford(BuildCityAction.cost):

                possibleActions.append(AgentRandom.actions[2])

            if gameState.CanBuyADevCard(player) and not player.biggestArmy:
                possibleActions.append(AgentRandom.actions[3])

            if not player.playedDevCard and sum(player.developmentCards[:-1]) > 0:
                possibleActions.append(AgentRandom.actions[4])

            if len(possibleActions) == 0:
                return player.GetPossibleBankTrades(gameState, player)

            chosenAction = random.choice(possibleActions)

            if chosenAction == 'buildRoad':

                possibleRoads = gameState.GetPossibleRoads(player)

                #possibleRoads = [gameState.boardEdges[edge] for edge in self.possibleRoads]

                if possibleRoads is not None and len(possibleRoads) > 0:

                    choice = possibleRoads[int(random.random() * len(possibleRoads))]

                    return BuildRoadAction(player.seatNumber, choice, len(player.roads))

            elif chosenAction == 'buildSettlement':

                possibleSettlements = gameState.GetPossibleSettlements(player)

                #possibleSettlements = [gameState.boardNodes[node] for node in self.possibleSettlements]

                if possibleSettlements is not None and len(possibleSettlements) > 0:

                    choice = possibleSettlements[int(random.random() * len(possibleSettlements))]

                    return BuildSettlementAction(player.seatNumber, choice, len(player.settlements))

            elif chosenAction == 'buildCity':

                possibleCities = gameState.GetPossibleCities(player)

                if possibleCities is not None and len(possibleCities) > 0:

                    choice = possibleCities[int(random.random() * len(possibleCities))]

                    return BuildCityAction(player.seatNumber, choice, len(player.cities))

            elif chosenAction == 'buyDevCard':

                return BuyDevelopmentCardAction(player.seatNumber)

            elif chosenAction == 'useDevCard':

                possibleCardsToUse = []

                if not player.playedDevCard:

                    if player.developmentCards[MONOPOLY_CARD_INDEX] > 0 and \
                            player.mayPlayDevCards[MONOPOLY_CARD_INDEX]:
                        possibleCardsToUse += player.GetMonopolyResource(player)

                    if player.developmentCards[YEAR_OF_PLENTY_CARD_INDEX] > 0 and \
                            player.mayPlayDevCards[YEAR_OF_PLENTY_CARD_INDEX]:
                        possibleCardsToUse += player.GetYearOfPlentyResource(player)

                    if player.developmentCards[ROAD_BUILDING_CARD_INDEX] > 0 and \
                            player.mayPlayDevCards[ROAD_BUILDING_CARD_INDEX] and \
                                    player.numberOfPieces[0] > 0:
                        possibleCardsToUse += [UseFreeRoadsCardAction(player.seatNumber, None, None)]

                if len(possibleCardsToUse) > 0:
                    return possibleCardsToUse[int(random.random() * len(possibleCardsToUse))]

    def PossibleActionsSpecial(self, gameState, player):

        if gameState.currState == 'PLACING_ROBBER':

            # Rolled out 7  * or *  Used a knight card
            return player.ChooseRobberPosition(gameState, player)

        elif gameState.currState == 'WAITING_FOR_DISCARDS':

            return [player.ChooseCardsToDiscard(player)]

        elif gameState.currState == 'WAITING_FOR_CHOICE':

            return [player.ChoosePlayerToStealFrom(gameState)]

        elif gameState.currState == "PLACING_FREE_ROAD1":

            possibleRoads = gameState.GetPossibleRoads(player, freeRoad=True)

            if possibleRoads is None or len(possibleRoads) <= 0:
                return [ ChangeGameStateAction("PLAY1") ]

            return [BuildRoadAction(player.seatNumber, roadEdge,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        elif gameState.currState == "PLACING_FREE_ROAD2":

            possibleRoads = gameState.GetPossibleRoads(player, freeRoad=True)

            if possibleRoads is None or len(possibleRoads) <= 0:
                return [ ChangeGameStateAction("PLAY1") ]

            return [BuildRoadAction(player.seatNumber, roadEdge,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

    def DoMove(self, game):

        if game.gameState.currPlayer != self.seatNumber and \
            game.gameState.currState != "WAITING_FOR_DISCARDS":
            return None

        possibleActions = self.GetPossibleActions(game.gameState)

        #logging.debug("possible actions = {0}".format(possibleActions))

        if game.gameState.currState == "PLAY1":

            if possibleActions is not None:

                return possibleActions

            return EndTurnAction(self.seatNumber)

        if possibleActions is not None and len(possibleActions) > 0:
            #return random.choice(possibleActions)
            return possibleActions[int(random.random() * len(possibleActions))]
        elif possibleActions is None:
            print("NONE!!!")

        return None

    def ChooseCardsToDiscard(self, player = None):

        if player is None:
            player = self

        if sum(player.resources) <= 7:
            return DiscardResourcesAction(player.seatNumber, [0, 0, 0, 0, 0, 0])

        resourcesPopulation = [0 for i in range(0, player.resources[0])] + \
                              [1 for j in range(0, player.resources[1])] + \
                              [2 for k in range(0, player.resources[2])] + \
                              [3 for l in range(0, player.resources[3])] + \
                              [4 for m in range(0, player.resources[4])] + \
                              [5 for n in range(0, player.resources[5])]

        discardCardCount = int(math.floor(len(resourcesPopulation) / 2.0))

        if discardCardCount > 0:
            #assert(player.discardCardCount == discardCardCount, "calculated cards to discard different from server!")
            player.discardCardCount = 0

        selectedResources = random.sample(resourcesPopulation, discardCardCount)

        return DiscardResourcesAction(player.seatNumber, [selectedResources.count(0),
                                                          selectedResources.count(1),
                                                          selectedResources.count(2),
                                                          selectedResources.count(3),
                                                          selectedResources.count(4),
                                                          selectedResources.count(5)])

    def ChooseRobberPosition(self, gameState, player = None):

        #possiblePositions = gameState.possibleRobberPos.append(gameState.robberPos)

        possiblePositions = gameState.possibleRobberPos

        choice = gameState.robberPos

        while choice == gameState.robberPos:
            choice = possiblePositions[int(random.random() * len(possiblePositions))]

        return [PlaceRobberAction(player.seatNumber, choice)]

    def ChoosePlayerToStealFrom(self, gameState, player = None):

        if player is None:
            player = self

        possiblePlayers = gameState.GetPossiblePlayersToSteal(player.seatNumber)

        if len(possiblePlayers) > 0:
            return ChoosePlayerToStealFromAction(player.seatNumber, possiblePlayers[int(random.random() * len(possiblePlayers))])

        return None

    def GetPossibleBankTrades(self, gameState, player = None):

        if player is None:
            player = self

        result = GetRandomBankTrade(player.resources, self.tradeRates)

        if result is not None:
            return [ BankTradeOfferAction(player.seatNumber, result[0], result[1]) ]

        return None

    def GetMonopolyResource(self, game, player = None):

        if player is None:
            player = self

        candidateResource = []

        minResourceAmount = min(player.resources[:-1])

        for i in xrange(0, len(player.resources) - 1):

            if player.resources[i] == minResourceAmount:
                candidateResource.append(i + 1)

        if len(candidateResource) <= 0:

            possible = [1,2,3,4,5]

            randomPick = possible[int(random.random() * 5)]

            logging.critical("Monopoly pick FAILED!!!! Picking at random: {0}".format(randomPick))

            chosenResource = randomPick

        else:
            chosenResource = candidateResource[int(random.random() * len(candidateResource))]

        return [ UseMonopolyCardAction(player.seatNumber, chosenResource) ]

    def GetYearOfPlentyResource(self, game, player = None):

        if player is None:
            player = self

        candidateResource = []

        chosenResources = [0, 0, 0, 0, 0]

        minResourceAmount = min(player.resources[:-1])

        for i in xrange(0, len(player.resources) - 1):

            if player.resources[i] == minResourceAmount:
                candidateResource.append(i)

        if len(candidateResource) == 1:

            chosenResources[i] = 2

        else:

            # pick1 = random.choice(candidateResource)
            # pick2 = random.choice(candidateResource)

            pick1 = candidateResource[int(random.random() * len(candidateResource))]
            pick2 = candidateResource[int(random.random() * len(candidateResource))]

            chosenResources[pick1] += 1
            chosenResources[pick2] += 1

        return [ UseYearOfPlentyCardAction(player.seatNumber, chosenResources) ]

    def UpdateResourcesFromServer(self, action, element, value):

        if element in g_resources:  # RESOURCE

            if action == 'SET':
                self.resources[g_resources.index(element)] = value

            elif action == 'GAIN':
                self.resources[g_resources.index(element)] += value

            elif action == 'LOSE':
                self.resources[g_resources.index(element)] -= value

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