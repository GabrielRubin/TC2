from CatanPlayer import *
import random
import logging
import math
from CatanUtils import GetRandomBankTrade

class AgentRandom(Player):

    def __init__(self, name, seatNumber, useModel = False):

        super(AgentRandom, self).__init__(name, seatNumber)

        self.agentName              = "RANDOM"
        self.preSelectMode          = None
        self.tradeLock              = False
        self.filterSetupSettlements = False
        self.filterEndTurnAction    = False
        self.useModel               = useModel
        if self.useModel:
            Player.LoadModel()

    def GetPossibleActions(self, gameState, player = None):

        if player is None:
            player = self

        if not gameState.setupDone:
            return self.GetPossibleActions_SetupTurns(gameState, player, self.filterSetupSettlements)
        elif gameState.currState == "PLAY":
            return self.GetPossibleActions_PreDiceRoll(player)
        elif gameState.currState == "PLAY1":
            return self.GetRandomAction_RegularTurns(gameState, player, self.preSelectMode, self.filterEndTurnAction)
        else:
            return self.GetPossibleActions_SpecialTurns(gameState, player)

    def GetPossibleActions_SetupTurns(self, gameState, player, filterSetupSettlements):

        if   gameState.currState == 'START1A':

            if player.firstSettlementBuild:
                return None

            if filterSetupSettlements:
                def IsNodeGood(node):
                    total = 0
                    for hexIndex in gameState.boardNodes[node].adjacentHexes:
                        if gameState.boardHexes[hexIndex].production is not None:
                            total += 1
                    return total > 1 or gameState.boardNodes[node].portType is not None

                bestSettlements = filter(IsNodeGood, gameState.GetPossibleSettlements(player, True))

                return [BuildSettlementAction(player.seatNumber, setNode, len(player.settlements))
                        for setNode in bestSettlements]
            else:
                return [BuildSettlementAction(player.seatNumber, setNode, len(player.settlements)) for setNode in
                        gameState.GetPossibleSettlements(player, True)]

        elif gameState.currState == 'START1B':

            if player.firstRoadBuild:
                return None

            possibleRoads = gameState.GetPossibleRoads(player, True)

            return [BuildRoadAction(player.seatNumber, roadEdge, len(player.roads)) for roadEdge in possibleRoads]

        elif gameState.currState == 'START2A':

            if player.secondSettlementBuild:
                return None

            if filterSetupSettlements:
                def IsNodeGood(node):
                    total = 0
                    for hexIndex in gameState.boardNodes[node].adjacentHexes:
                        if gameState.boardHexes[hexIndex].production is not None:
                            total += 1
                    return total > 1 or gameState.boardNodes[node].portType is not None

                bestSettlements = filter(IsNodeGood, gameState.GetPossibleSettlements(player, True))

                return [BuildSettlementAction(player.seatNumber, setNode, len(player.settlements))
                        for setNode in bestSettlements]
            else:
                return [BuildSettlementAction(player.seatNumber, setNode, len(player.settlements)) for setNode in
                        gameState.GetPossibleSettlements(player, True)]

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

    preSelectMode = ('citiesAndSettlements', 'citiesOverSettlements')

    def GetRandomAction_RegularTurns(self, gameState, player, preSelectMode, filterEndTurnAction):

        possibleActions     = []

        if player.settlements and\
            player.HavePiece(g_pieces.index('CITIES')) and\
            player.CanAfford(BuildCityAction.cost):

            possibleCities = gameState.GetPossibleCities(player)

            if possibleCities is not None and len(possibleCities) > 0:

                if preSelectMode is not None and preSelectMode == 'citiesOverSettlements':
                    choice = possibleCities[int(random.random() * len(possibleCities))]
                    return BuildCityAction(player.seatNumber, choice, len(player.cities))

                possibleActions.append('buildCity')

        possibleSettlements = gameState.GetPossibleSettlements(player)

        if player.HavePiece(g_pieces.index('SETTLEMENTS')) and \
            player.CanAfford(BuildSettlementAction.cost) and \
            possibleSettlements:

            if preSelectMode is not None and preSelectMode == 'citiesOverSettlements':
                choice = possibleSettlements[int(random.random() * len(possibleSettlements))]
                return BuildSettlementAction(player.seatNumber, choice, len(player.settlements))

            possibleActions.append('buildSettlement')

        if preSelectMode is None or not possibleActions:

            possibleRoads = gameState.GetPossibleRoads(player)

            if player.HavePiece(g_pieces.index('ROADS')) and \
                player.CanAfford(BuildRoadAction.cost)and \
                possibleRoads:
                possibleActions.append('buildRoad')

            if gameState.CanBuyADevCard(player) and not player.biggestArmy:
                possibleActions.append('buyDevCard')

            if not player.playedDevCard and sum(player.developmentCards[:-1]) > 0:
                possibleActions.append('useDevCard')

        if not possibleActions:

            possibleTrade = player.GetPossibleBankTrades(gameState, player)
            if possibleTrade is not None and possibleTrade:
                return possibleTrade[int(random.random() * len(possibleTrade))]

            return EndTurnAction(playerNumber=player.seatNumber)


        if not filterEndTurnAction:
            possibleActions.append('endTurn')

        chosenAction = random.choice(possibleActions)

        if chosenAction == 'buildRoad':

            choice = possibleRoads[int(random.random() * len(possibleRoads))]

            return BuildRoadAction(player.seatNumber, choice, len(player.roads))

        elif chosenAction == 'buildSettlement':

            choice = possibleSettlements[int(random.random() * len(possibleSettlements))]

            return BuildSettlementAction(player.seatNumber, choice, len(player.settlements))

        elif chosenAction == 'buildCity':

            choice = possibleCities[int(random.random() * len(possibleCities))]

            return BuildCityAction(player.seatNumber, choice, len(player.cities))

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

        elif chosenAction == 'endTurn':
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

        elif gameState.currState == "WAITING_FOR_TRADE":

            return self.GetPossiblePlayerTradeReactions(gameState, player)


    def DoMove(self, game):

        if game.gameState.currPlayer != self.seatNumber and \
            game.gameState.currState != "WAITING_FOR_DISCARDS":
            return None

        if self.useModel:
            possibleActions = Player.GetModelSelectedActions(game.gameState, self)
        else:
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

        selectedResources = random.sample(resourcesPopulation, discardCardCount)

        return DiscardResourcesAction(player.seatNumber, [selectedResources.count(0),
                                                          selectedResources.count(1),
                                                          selectedResources.count(2),
                                                          selectedResources.count(3),
                                                          selectedResources.count(4),
                                                          selectedResources.count(5)])

    def GetPossiblePlayerTradeReactions(self, gameState, player):

        canTrade = True

        for i in range(0, len(gameState.currTradeOffer.getResources)):
            if player.resources[i] < gameState.currTradeOffer.getResources[i]:
                canTrade = False
                break

        rejectTrade = RejectTradeOfferAction(playerNumber=player.seatNumber)

        if canTrade:
            acceptTrade = AcceptTradeOfferAction(playerNumber=player.seatNumber,
                                                 offerPlayerNumber=gameState.currTradeOffer.fromPlayerNumber)
            return [acceptTrade, rejectTrade]

        return [rejectTrade]

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

    def GetPossiblePlayerTrades(self, gameState, player):

        if player is None:
            player = self

        possibleTrades = []

        if sum(player.resources) > 0:
            for i in range(0, len(player.resources)-1):
                if player.resources[i] > 0:
                    giveResources    = [0, 0, 0, 0, 0]
                    giveResources[i] = 1
                    for j in range(0, len(player.resources)-1):
                        if j != i:
                            getResources    = [0, 0, 0, 0, 0]
                            getResources[j] = 1
                            tradeAction = MakeTradeOfferAction(fromPlayerNumber=player.seatNumber,
                                                               toPlayers=[(p != player.seatNumber)
                                                                          for p in range(0, len(gameState.players))],
                                                               giveResources=giveResources, getResources=getResources)
                            possibleTrades.append(tradeAction)

        return possibleTrades

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