from AgentRandom import *
import random
import logging
import math
import copy
import datetime

class AgentAlphabeta(AgentRandom):

    def __init__(self, name, seatNumber):

        super(AgentAlphabeta, self).__init__(name, seatNumber)

        self.agentName = "ALPHA-BETA"

    @staticmethod
    def GetPossibleActions(gameState, player):

        if gameState.currState == 'START1A':

            if player.firstSettlementBuild:
                return None

            possibleSettlements = gameState.GetPossibleSettlements(player, True)

            def RateNode(node, uniqueness):

                possibleResources = [gameState.boardHexes[boardHex].production for boardHex in node.adjacentHexes
                                     if boardHex is not None]

                if len(possibleResources) < 2:
                    return False

                seen = []
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

                goodNodes = [setNode for setNode in possibleSettlements if RateNode(setNode, 3 - i)]

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

                goodNodes = [setNode for setNode in possibleSettlements if RateNode(setNode, player.resources, 3 - i)]

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
                return [UseKnightsCardAction(player.seatNumber, None, None)]

            if not player.rolledTheDices:
                return [RollDicesAction(player.seatNumber)]

        elif gameState.currState == 'PLAY1':

            actions = ['buildRoad', 'buildSettlement', 'buildCity',
                       'buyDevCard', 'useDevCard']

            possibleActions = []

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
                return [ChangeGameStateAction("PLAY1")]

            return [BuildRoadAction(player.seatNumber, roadEdge.index,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        elif gameState.currState == "PLACING_FREE_ROAD2":

            possibleRoads = gameState.GetPossibleRoads(player, freeRoad=True)

            if possibleRoads is None or len(possibleRoads) <= 0:
                return [ChangeGameStateAction("PLAY1")]

            return [BuildRoadAction(player.seatNumber, roadEdge.index,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        return None

    def DoMove(self, game):

        if game.gameState.currPlayer != self.seatNumber and \
            game.gameState.currState != "WAITING_FOR_DISCARDS":
            return None

        #return self.Max_N(game, [0, 0, 0, 0], -1, 2)[1]

        chosenMove = self.Alphabeta(game)[1]

        print("{0} he chose this> {1}".format(datetime.datetime.utcnow(),
                                              chosenMove))

        return [chosenMove, EndTurnAction(self.seatNumber)]

    # TODO: ALPHABETA
    def Alphabeta(self, game, depth=2, alpha=float('-inf'), beta=float('inf'), player_turn=True):

        playerNumber = game.gameState.currPlayer

        score = self.GetGameStateReward(game.gameState, playerNumber)

        possibleActions = self.GetPossibleActions(game.gameState, game.gameState.players[playerNumber])

        if depth == 2 and possibleActions is not None:
            if len(possibleActions) == 1:
                return (None, possibleActions[0])

        #has_available_moves = len(possibleActions) > 0
        someone_wins = (game.gameState.currState == "OVER")
        max_depth_reached = depth <= 0

        if max_depth_reached or someone_wins: #or not has_available_moves:
            return (score, None)

        best = None

        if possibleActions is not None and len(possibleActions) > 0:

            for i in range(0, len(possibleActions)):

                copyGame = copy.deepcopy(game)

                possibleActions[i].ApplyAction(copyGame.gameState)

                if copyGame.gameState.currPlayer != playerNumber:
                    currentDepth = depth - 1
                else:
                    currentDepth = depth

                if player_turn:

                    result = self.Alphabeta(copyGame, currentDepth, alpha, beta, player_turn=False)
                    value = result[0]
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break
                    best = possibleActions[i]

                else:

                    result = self.Alphabeta(copyGame, currentDepth, alpha, beta, player_turn=True)
                    value = result[0]
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
                    best = possibleActions[i]

        return (value, best)

    # def Max_N(self, game, values, depth, maxDepth):
    #
    #     if depth >= maxDepth:
    #
    #         return ([
    #                     self.GetGameStateReward(game.gameState, 0),
    #                     self.GetGameStateReward(game.gameState, 1),
    #                     self.GetGameStateReward(game.gameState, 2),
    #                     self.GetGameStateReward(game.gameState, 3)
    #                 ],
    #                 None)
    #
    #     playerNumber = game.gameState.currPlayer
    #
    #     possibleActions = self.GetPossibleActions(game, game.gameState.players[playerNumber])
    #
    #     if depth == -1 and possibleActions is not None:
    #
    #         if len(possibleActions) == 1:
    #
    #             return (values, possibleActions[0])
    #
    #         elif game.gameState.currState == "PLAY1":
    #
    #             for i in range(0, len(possibleActions)):
    #
    #                 if possibleActions[i] is not None and len(possibleActions[i]) > 0:
    #                     break
    #                 if i == 6: # EndTurnAction
    #                     return (values, possibleActions[i][0])
    #
    #         depth = 0
    #
    #     logging.debug("possible actions = {0}".format(possibleActions))
    #
    #     best = None
    #
    #     # FOR "PROPER" TURNS
    #     if game.gameState.currState == "PLAY1":
    #
    #         if possibleActions is not None and len(possibleActions) > 0:
    #
    #             for i in range(0, len(possibleActions)):
    #
    #                 if possibleActions[i] is not None:
    #
    #                     for j in range(0, len(possibleActions[i])):
    #
    #                         copyGame = copy.deepcopy(game)
    #
    #                         possibleActions[i][j].ApplyAction(copyGame.gameState)
    #
    #                         if copyGame.gameState.currPlayer != playerNumber:
    #                             currentDepth = depth + 1
    #                         else:
    #                             currentDepth = depth
    #
    #                         result = self.Max_N(copyGame, list(values), currentDepth, maxDepth)
    #
    #                         value = result[0][playerNumber]
    #
    #                         if value > values[playerNumber]:
    #
    #                             values[playerNumber] = value
    #
    #                             best = possibleActions[i][j]
    #
    #                             #print("Turn: best! {0}".format(best))
    #
    #                             values = result[0]
    #
    #     # FOR SETUP TURNS AND OTHER EVENTS
    #     else:
    #
    #         if possibleActions is not None and len(possibleActions) > 0:
    #
    #             for i in range(0, len(possibleActions)):
    #
    #                 copyGame = copy.deepcopy(game)
    #
    #                 possibleActions[i].ApplyAction(copyGame.gameState)
    #
    #                 if copyGame.gameState.currPlayer != playerNumber:
    #                     currentDepth = depth + 1
    #                 else:
    #                     currentDepth = depth
    #
    #                 result = self.Max_N(copyGame, list(values), currentDepth, maxDepth)
    #
    #                 value = result[0][playerNumber]
    #
    #                 if value > values[playerNumber]:
    #
    #                     values[playerNumber] = value
    #
    #                     best = possibleActions[i]
    #
    #                     #print("N-turn: best! {0}".format(best))
    #
    #                     values = result[0]
    #
    #     return (values, best)

    def GetGameStateReward(self, gameState, playerNumber):

        playerPoints   = gameState.players[playerNumber].GetVictoryPoints()

        longestRoadPts = 0

        largestArmyPts = 0

        numRoads       = len(gameState.players[playerNumber].roads)

        numSettlements = len(gameState.players[playerNumber].settlements)

        numCities      = len(gameState.players[playerNumber].cities)

        if gameState.longestRoadPlayer == playerNumber:
            longestRoadPts = 3

        if gameState.largestArmyPlayer == playerNumber:
            largestArmyPts = 3

        return playerPoints * 0.5 + numRoads * 1 + numSettlements * 2 + numCities * 3 + \
                largestArmyPts + longestRoadPts

'''
REFERENCE: (alpha-beta for tictactoe
availCells = find_empty_cells(board)

if len(availCells) == 0:
 if find_winner(board) == O:
   return (-1, None)
 elif find_winner(board) is None:
   return (0, None)
 elif find_winner(board) == X:
   return (1, None)
best = None
for move in availCells:
    board[move] = player
    if player == X:
        val = self.alphabeta(board, O, alpha, beta)[0]
        if val > alpha:
            alpha = val
            best = move
    else:
        val = self.alphabeta(board, X, alpha, beta)[0]
        if val < beta:
            beta = val
            best = move

    board[move] = 0
    if alpha >= beta:
        break

if player == X:
    return (alpha, best)
else:
    return (beta, best)
'''