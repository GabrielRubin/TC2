from AgentRandom import *
from datetime import datetime
from datetime import timedelta
import copy
import cPickle

# * OPTION (for performance)*
#    implement nodes as a tuple (worse to read/understand)
# MCTS TREE NODE STRUCTURE:
# (gameState, action     , Q-value , N-value     , PARENT     , CHILDREN)
#  currState, from parent, reward  , n. of visits, parent node, children

class MCTSNode:

    def __init__(self, state, action, qValue, nValue, parent, children):

        self.gameState       = state    #current gameState
        self.action          = action   #action that led to this state
        self.QValue          = qValue   #node estimated reward value
        self.NValue          = nValue   #number of visits
        self.parent          = parent   #parent
        self.children        = children #children
        self.possibleActions = AgentMCTS.GetPossibleActions(state,
                                   state.players[state.currPlayer])

class AgentMCTS(AgentRandom):

    explorationConstant = 0.5

    def __init__(self, name, seatNumber, choiceTime):

        super(AgentMCTS, self).__init__(name, seatNumber)

        self.choiceTime = choiceTime

        self.agentName = "MONTE CARLO TREE SEARCH : {0} sec".format(choiceTime)

        self.numberOfSimulations = 0

    def DoMove(self, game):

        if game.gameState.currPlayer != self.seatNumber and \
            game.gameState.currState != "WAITING_FOR_DISCARDS":
            return None

        if game.gameState.currState == "WAITING_FOR_DISCARDS":
            return AgentMCTS.ChooseCardsToDiscard(self)

        if (game.gameState.currState == "START1A" and self.firstSettlementBuild) or \
           (game.gameState.currState == "START1B" and self.firstRoadBuild) or \
           (game.gameState.currState == "START2A" and self.secondSettlementBuild) or \
           (game.gameState.currState == "START2B" and self.secondRoadBuild):
            return None

        self.numberOfSimulations = 0

        state = cPickle.loads(cPickle.dumps(game.gameState, -1))

        self.PrepareGameStateForSimulation(state)

        return self.MonteCarloTreeSearch(state, timedelta(seconds=self.choiceTime))

    def MonteCarloTreeSearch(self, gameState, maxDuration):

        rootNode = MCTSNode(gameState, None, [0 for i in range(len(gameState.players))], 0, None, [])

        if rootNode.possibleActions is None:
            print("MCTS ERROR! POSSIBLE ACTIONS FROM ROOT NODE ARE NONE!!!!")
            return None

        elif len(rootNode.possibleActions) == 1:
            return rootNode.possibleActions[0]

        elif len(rootNode.possibleActions) <= 0:
            print("MCTS ERROR! NO POSSIBLE ACTIONS FROM ROOT NODE!")
            return None

        startTime = datetime.utcnow()

        while (datetime.utcnow() - startTime) < maxDuration:

            nextNode    = self.TreePolicy(rootNode)

            reward      = self.SimulationPolicy(cPickle.loads(cPickle.dumps(nextNode.gameState, -1)))

            self.BackUp(nextNode, reward)

            self.numberOfSimulations += 1

        print("TOTAL SIMULATIONS = {0}".format(self.numberOfSimulations))

        return self.BestChild(rootNode, 0).action

    def TreePolicy(self, node):

        while not node.gameState.IsTerminal():
            # There are still actions to try in this node...
            if len(node.possibleActions) > 0:
                return self.Expand(node)
            else:
                node = self.BestChild(node, AgentMCTS.explorationConstant)

        return node

    def Expand(self, node):

        chosenAction = random.choice(node.possibleActions)

        node.possibleActions.remove(chosenAction)

        nextGameState = cPickle.loads(cPickle.dumps(node.gameState, -1))

        chosenAction.ApplyAction(nextGameState)

        childNode = MCTSNode(state=nextGameState,
                             action=chosenAction,
                             qValue=[0 for i in range(len(nextGameState.players))],
                             nValue=0,
                             parent=node,
                             children=[])

        node.children.append(childNode)

        return childNode

    def BestChild(self, node, explorationValue):

        currPlayerNumber = node.gameState.currPlayer

        # Returns the Child Node with the max 'Q-Value'
        #return max(node.children, key=lambda child: child.QValue[currPlayerNumber])

        def UCTClassifier(childNode):

            evaluationPart  = childNode.QValue[currPlayerNumber] / childNode.NValue
            explorationPart = explorationValue * math.sqrt( (2 * math.log(node.NValue)) / childNode.NValue )
            return evaluationPart + explorationPart

        return max(node.children, key=lambda child : UCTClassifier(child))

    def SimulationPolicy(self, gameState):

        #startTime = datetime.utcnow()
        #print("starting simulation {0}".format(startTime))

        while not gameState.IsTerminal():

            possibleActions = AgentMCTS.GetPossibleActions(gameState,
                        gameState.players[gameState.currPlayer])

            if len(possibleActions) > 1:
                action = random.choice(possibleActions)
            else:

                if len(possibleActions) == 0:
                    print(gameState.currState)

                action = possibleActions[0]

            action.ApplyAction(gameState)

        #endTime = datetime.utcnow()
        #print("simulation ENDED {0} - deltaTime = {1}".format(endTime, (endTime - startTime).total_seconds()))

        return self.Utility(gameState, self.seatNumber)

    def BackUp(self, node, reward):

        currPlayer = node.gameState.currPlayer

        while node is not None:

            node.NValue             += 1
            node.QValue[currPlayer] += reward
            node = node.parent

    def Utility(self, gameState, playerNumber):

        # TEMP...
        return gameState.players[playerNumber].GetVictoryPoints()

    def PrepareGameStateForSimulation(self, gameState):

        for player in gameState.players:

            if player is None:
                continue

            quantity = player.resources[g_resources.index('UNKNOWN')]

            if quantity > 0:

                player.resources[g_resources.index('UNKNOWN')] = 0

                resources = [0, 0, 0, 0, 0, 0]

                for i in range(0, quantity):
                    resources[random.randint(0, 4)] += 1

                player.resources = player.resources + resources

    @staticmethod
    def GetPossibleActions(gameState, player):

        if   gameState.currState == 'START1A':

            if player.firstSettlementBuild:
                return None

            possibleSettlements = gameState.GetPossibleSettlements(player, True)

            def RateNode(node, uniqueness):

                possibleResources = [gameState.boardHexes[boardHex].production for boardHex in node.adjacentHexes
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

                goodNodes = [ setNode for setNode in possibleSettlements if RateNode(setNode, 2 - i) ]

                if len(goodNodes) > 0:
                    break

            possible = [BuildSettlementAction(player.seatNumber, setNode.index, len(player.settlements))
                        for setNode in goodNodes if setNode is not None]

            return possible

        elif gameState.currState == 'START1B':

            if player.firstRoadBuild:
                return None

            possibleRoads = gameState.GetPossibleRoads(player, True)

            #possibleRoads = [gameState.boardEdges[edge] for edge in self.possibleRoads]

            return [BuildRoadAction(player.seatNumber, roadEdge.index, len(player.roads)) for roadEdge in possibleRoads]

        elif gameState.currState == 'START2A':

            if player.secondSettlementBuild:
                return None

            possibleSettlements = gameState.GetPossibleSettlements(player, True)

            def RateNode(node, ownedResources, uniqueness):

                possibleResources = [gameState.boardHexes[boardHex].production for boardHex in node.adjacentHexes
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
                    for setNode in goodNodes if setNode is not None]

        elif gameState.currState == 'START2B':

            if player.secondRoadBuild:
                return None

            possibleRoads = gameState.GetPossibleRoads(player, True)

            #possibleRoads = self.possibleRoads

            filterRoads = filter(lambda x: x.index in gameState.boardNodes[player.settlements[1]].adjacentEdges, possibleRoads)

            #possibleRoadsFiltered = [gameState.boardEdges[edge] for edge in filterRoads]

            return [BuildRoadAction(player.seatNumber, roadEdge.index, len(player.roads))
                    for roadEdge in filterRoads]

        elif gameState.currState == 'PLAY':

            if not player.rolledTheDices and \
               not player.playedDevCard and \
                    player.mayPlayDevCards[KNIGHT_CARD_INDEX] and \
                            player.developmentCards[KNIGHT_CARD_INDEX] > 0:

                return [ UseKnightsCardAction( player.seatNumber, None, None ) ]

            if not player.rolledTheDices:

                return [ RollDicesAction( player.seatNumber ) ]

        elif gameState.currState == 'PLAY1':

            actions             = ['buildRoad', 'buildSettlement', 'buildCity',
                                   'buyDevCard', 'useDevCard']

            possibleActions     = []

            if player.CanAfford(BuildRoadAction.cost) and \
               player.HavePiece(g_pieces.index('ROADS')) > 0:

                possibleActions.append(actions[0])

            if player.CanAfford(BuildSettlementAction.cost) and \
               player.HavePiece(g_pieces.index('SETTLEMENTS')) > 0:

                possibleActions.append(actions[1])

            if player.CanAfford(BuildCityAction.cost) and \
               player.HavePiece(g_pieces.index('CITIES')) > 0 and \
               len(player.settlements) > 0:

                possibleActions.append(actions[2])

            if gameState.CanBuyADevCard(player) and not player.biggestArmy:
                possibleActions.append(actions[3])

            if not player.playedDevCard and sum(player.developmentCards[:-1]) > 0:
                possibleActions.append(actions[4])

            if len(possibleActions) == 0:

                possibleBankTrades = []

                if random.random() >= 0.5:

                    possibleBankTrades = AgentMCTS.GetPossibleBankTrades(gameState, player)

                if possibleBankTrades is None or len(possibleBankTrades) > 0:
                    return [EndTurnAction(player.seatNumber)]

            result = []

            for a in possibleActions:

                if a == 'buildRoad':

                    possibleRoads = gameState.GetPossibleRoads(player)

                    if possibleRoads is not None and len(possibleRoads) > 0:

                        result += [BuildRoadAction(player.seatNumber, roadEdge.index, len(player.roads))
                                   for roadEdge in possibleRoads]

                elif a == 'buildSettlement':

                    possibleSettlements = gameState.GetPossibleSettlements(player)

                    if possibleSettlements is not None and len(possibleSettlements) > 0:

                        result += [BuildSettlementAction(player.seatNumber, setNode.index, len(player.settlements))
                                   for setNode in possibleSettlements]

                elif a == 'buildCity':

                    possibleCities = gameState.GetPossibleCities(player)

                    if possibleCities is not None and len(possibleCities) > 0:

                        result += [BuildCityAction(player.seatNumber, setNode.index, len(player.cities))
                                   for setNode in possibleCities]

                elif a == 'buyDevCard':

                    result += [BuyDevelopmentCardAction(player.seatNumber)]

                elif a == 'useDevCard':

                    possibleCardsToUse = []

                    if not player.playedDevCard:

                        if player.developmentCards[MONOPOLY_CARD_INDEX] > 0 and \
                                player.mayPlayDevCards[MONOPOLY_CARD_INDEX]:
                            possibleCardsToUse += AgentMCTS.GetMonopolyResource(gameState, player)

                        if player.developmentCards[YEAR_OF_PLENTY_CARD_INDEX] > 0 and \
                                player.mayPlayDevCards[YEAR_OF_PLENTY_CARD_INDEX]:
                            possibleCardsToUse += AgentMCTS.GetYearOfPlentyResource(player)

                        if player.developmentCards[ROAD_BUILDING_CARD_INDEX] > 0 and \
                                player.mayPlayDevCards[ROAD_BUILDING_CARD_INDEX] and \
                                        player.numberOfPieces[0] > 0:
                            possibleCardsToUse += [UseFreeRoadsCardAction(player.seatNumber, None, None)]

                    result += possibleCardsToUse

            if len(result) == 0:
                result += [EndTurnAction(player.seatNumber)]

            return result

        elif gameState.currState == 'PLACING_ROBBER':

            # Rolled out 7  * or *  Used a knight card
            return AgentMCTS.ChooseRobberPosition(gameState, player)

        elif gameState.currState == 'WAITING_FOR_DISCARDS':

            return [AgentMCTS.ChooseCardsToDiscard(player)]

        elif gameState.currState == 'WAITING_FOR_CHOICE':

            return [AgentMCTS.ChoosePlayerToStealFrom(gameState, player)]

        elif gameState.currState == "PLACING_FREE_ROAD1":

            possibleRoads = gameState.GetPossibleRoads(player, freeRoad=True)

            if possibleRoads is None or len(possibleRoads) <= 0:
                return [ ChangeGameStateAction("PLAY1") ]

            return [BuildRoadAction(player.seatNumber, roadEdge.index,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        elif gameState.currState == "PLACING_FREE_ROAD2":

            possibleRoads = gameState.GetPossibleRoads(player, freeRoad=True)

            if possibleRoads is None or len(possibleRoads) <= 0:
                return [ ChangeGameStateAction("PLAY1") ]

            return [BuildRoadAction(player.seatNumber, roadEdge.index,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        return None

    @staticmethod
    def ChooseCardsToDiscard(player):

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
            # assert(player.discardCardCount == discardCardCount, "calculated cards to discard different from server!")
            player.discardCardCount = 0

        selectedResources = random.sample(resourcesPopulation, discardCardCount)

        return DiscardResourcesAction(player.seatNumber, [selectedResources.count(0),
                                                          selectedResources.count(1),
                                                          selectedResources.count(2),
                                                          selectedResources.count(3),
                                                          selectedResources.count(4),
                                                          selectedResources.count(5)])

    @staticmethod
    def ChooseRobberPosition(gameState, player):

        possiblePositions = gameState.possibleRobberPos + [gameState.robberPos]

        return [PlaceRobberAction(player.seatNumber, position)
                for position in possiblePositions]

    @staticmethod
    def ChoosePlayerToStealFrom(gameState, player):

        possiblePlayers = gameState.GetPossiblePlayersToSteal(player.seatNumber)

        if len(possiblePlayers) > 0:
            return ChoosePlayerToStealFromAction(player.seatNumber, random.choice(possiblePlayers))

        return None

    @staticmethod
    def GetPossibleBankTrades(gameState, player):

        availablePorts = player.GetPorts(gameState)

        if availablePorts[-1]:
            minTradeRate = 3
        else:
            minTradeRate = 4

        tradeRates = [minTradeRate, minTradeRate, minTradeRate, minTradeRate, minTradeRate]

        for i in range(0, len(tradeRates)):
            if availablePorts[i]:
                tradeRates[i] = 2

        possibleTradeAmount = [0, 0, 0, 0, 0]
        candidateForTrade = []

        minResourceAmount = min(player.resources[:-1])  # Don't count the 'UNKNOWN' resource

        for i in range(len(possibleTradeAmount)):
            possibleTradeAmount[i] = int(player.resources[i] / tradeRates[i])
            if player.resources[i] == minResourceAmount:
                candidateForTrade.append(i)

        tradeAmount = random.randint(0, sum(possibleTradeAmount))

        if tradeAmount > 0 and len(candidateForTrade) > 0:

            possibleTradePopulation = [0 for i in range(0, possibleTradeAmount[0])] + \
                                      [1 for j in range(0, possibleTradeAmount[1])] + \
                                      [2 for k in range(0, possibleTradeAmount[2])] + \
                                      [3 for l in range(0, possibleTradeAmount[3])] + \
                                      [4 for m in range(0, possibleTradeAmount[4])]

            # logging.debug("Player {0} is checking if he can trade...\n"
            #               " He have this resources: {1}\n"
            #               " And he thinks he can trade these: {2}".format(player.name, player.resources,
            #                                                               possibleTradeAmount))

            chosenResources = random.sample(possibleTradePopulation, tradeAmount)

            expectedResources = []
            for i in range(0, tradeAmount):
                expectedResources.append(random.choice(candidateForTrade))

            # logging.debug("Chosen: {0}\n Expected: {1}\n MaxTrades: {2}".format(
            #     chosenResources, expectedResources, tradeAmount
            # ))

            give = [chosenResources.count(0) * tradeRates[0], chosenResources.count(1) * tradeRates[1],
                    chosenResources.count(2) * tradeRates[2], chosenResources.count(3) * tradeRates[3],
                    chosenResources.count(4) * tradeRates[4]]

            get = [expectedResources.count(0), expectedResources.count(1),
                   expectedResources.count(2), expectedResources.count(3),
                   expectedResources.count(4)]

            # logging.debug("Player {0} will trade with the bank!\n"
            #               " GIVE = {1}\n"
            #               " GET  = {2}".format(player.name, give, get))

            return [BankTradeOfferAction(player.seatNumber, give, get)]

        return None

    @staticmethod
    def GetMonopolyResource(game, player):

        candidateResource = []

        minResourceAmount = min(player.resources[:-1])

        for i in range(0, len(player.resources) - 1):

            if player.resources[i] == minResourceAmount:
                candidateResource.append(i + 1)

        if len(candidateResource) <= 0:

            randomPick = random.choice([1, 2, 3, 4, 5])

            logging.critical("Monopoly pick FAILED!!!! Picking at random: {0}".format(randomPick))

            chosenResource = randomPick

        else:

            chosenResource = random.choice(candidateResource)

        return [UseMonopolyCardAction(player.seatNumber, chosenResource)]

    @staticmethod
    def GetYearOfPlentyResource(player):

        candidateResource = []

        chosenResources = [0, 0, 0, 0, 0]

        minResourceAmount = min(player.resources[:-1])

        for i in range(0, len(player.resources) - 1):

            if player.resources[i] == minResourceAmount:
                candidateResource.append(i)

        if len(candidateResource) == 1:

            chosenResources[i] = 2

        else:

            pick1 = random.choice(candidateResource)
            pick2 = random.choice(candidateResource)

            chosenResources[pick1] += 1
            chosenResources[pick2] += 1

        return [UseYearOfPlentyCardAction(player.seatNumber, chosenResources)]