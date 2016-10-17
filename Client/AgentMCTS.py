from AgentRandom import *
from datetime import datetime
from datetime import timedelta
import copy


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

    def __init__(self, name, seatNumber):

        super(AgentMCTS, self).__init__(name, seatNumber)

        self.agentName = "MONTE CARLO TREE SEARCH"

    def DoMove(self, game):

        return self.MonteCarloTreeSearch(copy.deepcopy(game.gameState),
                                         timedelta(seconds=5))

    def MonteCarloTreeSearch(self, gameState, maxDuration):

        rootNode = MCTSNode(gameState, None, [0 for i in range(len(gameState.players))], 0, None, [])

        startTime = datetime.utcnow()

        while (datetime.utcnow() - startTime) < maxDuration:

            nextNode    = self.TreePolicy(rootNode)

            reward      = self.SimulationPolicy(copy.deepcopy(nextNode.gameState))

            self.BackUp(nextNode, reward)

        return self.BestChild(rootNode).action

    def TreePolicy(self, node):

        while not node.gameState.IsTerminal():
            # There are still actions to try in this node...
            if len(node.possibleActions) > 0:
                return self.Expand(node)
            else:
                node = self.BestChild(node)

        return node

    def Expand(self, node):

        chosenAction = random.choice(node.possibleActions)

        node.possibleActions.remove(chosenAction)

        nextGameState = copy.deepcopy(node.gameState)

        chosenAction.ApplyAction(nextGameState)

        childNode = MCTSNode(state=nextGameState,
                             action=chosenAction,
                             qValue=[0 for i in range(len(nextGameState.players))],
                             nValue=0,
                             parent=node,
                             children=[])

        node.children.append(childNode)

        return childNode

    def BestChild(self, node):

        currPlayerNumber = node.gameState.currPlayer

        # Returns the Child Node with the max 'Q-Value'
        return max(node.children, key=lambda child: child.QValue[currPlayerNumber])

    def SimulationPolicy(self, gameState):

        while not gameState.IsTerminal():

            possibleActions = AgentMCTS.GetPossibleActions(gameState,
                        gameState.players[gameState.currPlayer])

            if len(possibleActions) > 1:
                action = random.choice(possibleActions)
            else:
                action = possibleActions[0]

            action.ApplyAction(gameState)

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

                goodNodes = [ setNode for setNode in possibleSettlements if RateNode(setNode, 3 - i) ]

                if len(goodNodes) > 0:
                    break

            return [BuildSettlementAction(player.seatNumber, setNode.index, len(player.settlements))
                    for setNode in goodNodes]

        elif gameState.currState == 'START1B':

            if player.firstRoadBuild:
                return None

            possibleRoads = gameState.GetPossibleRoads(player, True)

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
                    for setNode in goodNodes]

        elif gameState.currState == 'START2B':

            if player.secondRoadBuild:
                return None

            possibleRoads = gameState.GetPossibleRoads(player, True)

            return [BuildRoadAction(player.seatNumber, roadEdge.index, len(player.roads))
                    for roadEdge in possibleRoads]

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

                    possibleBankTrades = player.GetPossibleBankTrades(gameState, player)

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
                            possibleCardsToUse += player.GetMonopolyResource(player)

                        if player.developmentCards[YEAR_OF_PLENTY_CARD_INDEX] > 0 and \
                                player.mayPlayDevCards[YEAR_OF_PLENTY_CARD_INDEX]:
                            possibleCardsToUse += player.GetYearOfPlentyResource(player)

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
            return player.ChooseRobberPosition(gameState, player)

        elif gameState.currState == 'WAITING_FOR_DISCARDS':

            return [player.ChooseCardsToDiscard(player)]

        elif gameState.currState == 'WAITING_FOR_CHOICE':

            return [player.ChoosePlayerToStealFrom(gameState)]

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