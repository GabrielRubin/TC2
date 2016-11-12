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
            return self.GetPossibleActions_SetupTurns(gameState, player)
        elif gameState.currState == "PLAY":
            return self.GetPossibleActions_PreDiceRoll(player)
        elif gameState.currState == "PLAY1":
            return self.GetRandomAction_RegularTurns(gameState, player)
        else:
            return self.GetPossibleActions_SpecialTurns(gameState, player)

    def GetPossibleActions_SetupTurns(self, gameState, player):

        if   gameState.currState == 'START1A':

            if player.firstSettlementBuild:
                return None

            def IsNodeGood(node):
                total = 0
                for hexIndex in gameState.boardNodes[node].adjacentHexes:
                    if gameState.boardHexes[hexIndex].production is not None:
                        total += 1
                return total > 1 or gameState.boardNodes[node].portType == '3for1'

            bestSettlements = filter(IsNodeGood, gameState.GetPossibleSettlements(player, True))

            possible = [BuildSettlementAction(player.seatNumber, setNode, len(player.settlements))
                        for setNode in bestSettlements]

            return possible

        elif gameState.currState == 'START1B':

            if player.firstRoadBuild:
                return None

            possibleRoads = gameState.GetPossibleRoads(player, True)

            return [BuildRoadAction(player.seatNumber, roadEdge, len(player.roads)) for roadEdge in possibleRoads]

        elif gameState.currState == 'START2A':

            if player.secondSettlementBuild:
                return None

            def IsNodeGood(node):
                total = 0
                for hexIndex in gameState.boardNodes[node].adjacentHexes:
                    if gameState.boardHexes[hexIndex].production is not None:
                        total += 1
                return total > 1 or gameState.boardNodes[node].portType == '3for1'

            bestSettlements = filter(IsNodeGood, gameState.GetPossibleSettlements(player, True))

            return [BuildSettlementAction(player.seatNumber, setNode, len(player.settlements))
                    for setNode in bestSettlements]

        elif gameState.currState == 'START2B':

            if player.secondRoadBuild:
                return None

            possibleRoads = gameState.GetPossibleRoads(player, True)

            return [BuildRoadAction(player.seatNumber, roadEdge, len(player.roads)) for roadEdge in possibleRoads]

    def GetPossibleActions_PreDiceRoll(self, player):

        if not player.rolledTheDices and \
           not player.playedDevCard and \
                player.mayPlayDevCards[KNIGHT_CARD_INDEX] and \
                        player.developmentCards[KNIGHT_CARD_INDEX] > 0:

            return [UseKnightsCardAction( player.seatNumber, None, None )]

        if not player.rolledTheDices:

            return [RollDicesAction( player.seatNumber )]

    actions = ('buildRoad', 'buildSettlement', 'buildCity',
               'buyDevCard', 'useDevCard', 'bankTrade', 'endTurn')

    # def GetPossibleActions_RegularTurns(self, gameState, player):
    #
    #     if gameState.currState == 'PLAY':
    #
    #         if not player.rolledTheDices and \
    #                 not player.playedDevCard and \
    #                 player.mayPlayDevCards[KNIGHT_CARD_INDEX] and \
    #                         player.developmentCards[KNIGHT_CARD_INDEX] > 0:
    #             return [UseKnightsCardAction(player.seatNumber, None, None)]
    #
    #         if not player.rolledTheDices:
    #             return [RollDicesAction(player.seatNumber)]
    #
    #     elif gameState.currState == 'PLAY1':
    #
    #         possibleActions     = []
    #         possibleSettlements = gameState.GetPossibleSettlements(player)
    #         possibleRoads       = gameState.GetPossibleRoads(player)
    #
    #         if player.settlements and \
    #                 player.HavePiece(g_pieces.index('CITIES')) and \
    #                 player.CanAfford(BuildCityAction.cost):
    #
    #             possibleCities = gameState.GetPossibleCities(player)
    #
    #             if possibleCities is not None and len(possibleCities) > 0:
    #
    #                 return [BuildCityAction(player.seatNumber, node, len(player.cities))
    #                         for node in possibleCities]
    #
    #         if player.HavePiece(g_pieces.index('SETTLEMENTS')) and \
    #                 player.CanAfford(BuildSettlementAction.cost) and \
    #                 possibleSettlements:
    #
    #             return [BuildSettlementAction(player.seatNumber, node, len(player.settlements))
    #                     for node in possibleSettlements]
    #
    #         if player.HavePiece(g_pieces.index('ROADS')) and \
    #                 player.CanAfford(BuildRoadAction.cost) and \
    #                 possibleRoads:
    #
    #             possibleActions.append(AgentRandom.actions[0])
    #
    #         if gameState.CanBuyADevCard(player) and not player.biggestArmy:
    #
    #             possibleActions.append(AgentRandom.actions[3])
    #
    #         if not player.playedDevCard and sum(player.developmentCards[:-1]) > 0 and \
    #                 not self.biggestArmy:
    #
    #             possibleActions.append(AgentRandom.actions[4])
    #
    #         if not possibleActions:
    #
    #             possibleTrade = player.GetPossibleBankTrades(gameState, player)
    #             if possibleTrade is not None and possibleTrade:
    #                 return possibleTrade
    #
    #             return [EndTurnAction(playerNumber=player.seatNumber)]
    #
    #         chosenAction = random.choice(possibleActions)
    #
    #         if chosenAction == 'buildRoad':
    #
    #             return [BuildRoadAction(player.seatNumber, edge, len(player.roads))
    #                     for edge in possibleRoads]
    #
    #         elif chosenAction == 'buyDevCard':
    #
    #             return [BuyDevelopmentCardAction(player.seatNumber)]
    #
    #         elif chosenAction == 'useDevCard':
    #
    #             possibleCardsToUse = []
    #
    #             if not player.playedDevCard:
    #
    #                 if player.developmentCards[MONOPOLY_CARD_INDEX] > 0 and \
    #                         player.mayPlayDevCards[MONOPOLY_CARD_INDEX]:
    #                     possibleCardsToUse += player.GetMonopolyResource(gameState, player)
    #
    #                 if player.developmentCards[YEAR_OF_PLENTY_CARD_INDEX] > 0 and \
    #                         player.mayPlayDevCards[YEAR_OF_PLENTY_CARD_INDEX]:
    #                     possibleCardsToUse += player.GetYearOfPlentyResource(gameState, player)
    #
    #                 if player.developmentCards[ROAD_BUILDING_CARD_INDEX] > 0 and \
    #                         player.mayPlayDevCards[ROAD_BUILDING_CARD_INDEX] and \
    #                                 player.numberOfPieces[0] > 0:
    #                     possibleCardsToUse += [UseFreeRoadsCardAction(player.seatNumber, None, None)]
    #
    #             if possibleCardsToUse:
    #                 return possibleCardsToUse
    #             else:
    #                 return [EndTurnAction(playerNumber=player.seatNumber)]

    def GetRandomAction_RegularTurns(self, gameState, player):

        if gameState.currState == 'PLAY':

            if not player.rolledTheDices and \
               not player.playedDevCard and \
                    player.mayPlayDevCards[KNIGHT_CARD_INDEX] and \
                            player.developmentCards[KNIGHT_CARD_INDEX] > 0:

                return [UseKnightsCardAction( player.seatNumber, None, None )]

            if not player.rolledTheDices:

                return [RollDicesAction( player.seatNumber )]

        elif gameState.currState == 'PLAY1':

            possibleActions     = []
            possibleSettlements = gameState.GetPossibleSettlements(player)
            possibleRoads       = gameState.GetPossibleRoads(player)

            if player.settlements and\
                player.HavePiece(g_pieces.index('CITIES')) and\
                player.CanAfford(BuildCityAction.cost):

                possibleCities = gameState.GetPossibleCities(player)

                if possibleCities is not None and len(possibleCities) > 0:

                    choice = possibleCities[int(random.random() * len(possibleCities))]

                    return BuildCityAction(player.seatNumber, choice, len(player.cities))

            if player.HavePiece(g_pieces.index('SETTLEMENTS')) and \
                player.CanAfford(BuildSettlementAction.cost) and \
                possibleSettlements:

                choice = possibleSettlements[int(random.random() * len(possibleSettlements))]

                return BuildSettlementAction(player.seatNumber, choice, len(player.settlements))

            if player.HavePiece(g_pieces.index('ROADS')) and \
                player.CanAfford(BuildRoadAction.cost)and \
                possibleRoads:

                possibleActions.append(AgentRandom.actions[0])

            if gameState.CanBuyADevCard(player) and not player.biggestArmy:
                possibleActions.append(AgentRandom.actions[3])

            if not player.playedDevCard and sum(player.developmentCards[:-1]) > 0 and\
                    not self.biggestArmy:
                possibleActions.append(AgentRandom.actions[4])

            if not possibleActions:

                possibleTrade = player.GetPossibleBankTrades(gameState, player)
                if possibleTrade is not None and possibleTrade:
                    return possibleTrade[0]

                return EndTurnAction(playerNumber=player.seatNumber)

            chosenAction = random.choice(possibleActions)

            if chosenAction == 'buildRoad':

                choice = possibleRoads[int(random.random() * len(possibleRoads))]

                return BuildRoadAction(player.seatNumber, choice, len(player.roads))

            elif chosenAction == 'buyDevCard':

                return BuyDevelopmentCardAction(player.seatNumber)

            elif chosenAction == 'useDevCard':

                possibleCardsToUse = []

                if not player.playedDevCard:

                    if player.developmentCards[MONOPOLY_CARD_INDEX] > 0 and \
                            player.mayPlayDevCards[MONOPOLY_CARD_INDEX]:
                        possibleCardsToUse += player.GetMonopolyResource(gameState, player)

                    if player.developmentCards[YEAR_OF_PLENTY_CARD_INDEX] > 0 and \
                            player.mayPlayDevCards[YEAR_OF_PLENTY_CARD_INDEX]:
                        possibleCardsToUse += player.GetYearOfPlentyResource(gameState, player)

                    if player.developmentCards[ROAD_BUILDING_CARD_INDEX] > 0 and \
                            player.mayPlayDevCards[ROAD_BUILDING_CARD_INDEX] and \
                                    player.numberOfPieces[0] > 0:
                        possibleCardsToUse += [UseFreeRoadsCardAction(player.seatNumber, None, None)]

                if possibleCardsToUse:
                    return possibleCardsToUse[int(random.random() * len(possibleCardsToUse))]
                else:
                    return EndTurnAction(playerNumber=player.seatNumber)

    def GetPossibleActions_SpecialTurns(self, gameState, player):

        if gameState.currState == 'PLACING_ROBBER':

            # Rolled out 7  * or *  Used a knight card
            return self.ChooseRobberPosition(gameState, player)

        elif gameState.currState == 'WAITING_FOR_DISCARDS':

            return [player.ChooseCardsToDiscard(player)]

        elif gameState.currState == 'WAITING_FOR_CHOICE':

            return [player.ChoosePlayerToStealFrom(gameState, player)]

        elif gameState.currState == "PLACING_FREE_ROAD1":

            possibleRoads = gameState.GetPossibleRoads(player)

            if possibleRoads is None or not possibleRoads or self.numberOfPieces[0] <= 0:
                return [ ChangeGameStateAction("PLAY1") ]

            return [BuildRoadAction(player.seatNumber, roadEdge,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        elif gameState.currState == "PLACING_FREE_ROAD2":

            possibleRoads = gameState.GetPossibleRoads(player)

            if possibleRoads is None or not possibleRoads or self.numberOfPieces[0] <= 0:
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

        if possibleActions is not None and possibleActions:
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

    def ChooseRobberPosition(self, gameState, player):

        possiblePositions = gameState.possibleRobberPos[:]

        possiblePositions.remove(gameState.robberPos)

        choice = possiblePositions[int(random.random() * len(possiblePositions))]

        return [PlaceRobberAction(player.seatNumber, choice)]

    def ChoosePlayerToStealFrom(self, gameState, player):

        if player is None:
            player = self

        possiblePlayers = gameState.GetPossiblePlayersToSteal(player.seatNumber)

        if len(possiblePlayers) > 0:
            return ChoosePlayerToStealFromAction(player.seatNumber, possiblePlayers[int(random.random() * len(possiblePlayers))])

        return None

    def GetPossibleBankTrades(self, gameState, player):

        if player is None:
            player = self

        result = GetRandomBankTrade(player.resources, self.tradeRates)

        if result is not None:
            return [ BankTradeOfferAction(player.seatNumber, result[0], result[1]) ]

        return None

    def GetMonopolyResource(self, game, player):

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

    def GetYearOfPlentyResource(self, game, player):

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