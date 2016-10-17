from AgentRandom import *
import random
import logging
import math
import copy
import time

class AgentAlphabeta(AgentRandom):

    def GetPossibleActions(self, game, player = None, gameState = None):

        if player is None:
            player = self

        if gameState is None:
            gameState = game.gameState

        if   gameState.currState == 'START1A':

            if player.firstSettlementBuild:
                return None

            possibleSettlements = game.GetPossibleSettlements(gameState, player, True)

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

            possibleRoads = game.GetPossibleRoads(gameState, player, True)

            return [BuildRoadAction(player.seatNumber, roadEdge.index, len(player.roads)) for roadEdge in possibleRoads]

        elif gameState.currState == 'START2A':

            if player.secondSettlementBuild:
                return None

            possibleSettlements = game.GetPossibleSettlements(gameState, player, True)

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

            possibleRoads = game.GetPossibleRoads(gameState, player, True)

            return [BuildRoadAction(player.seatNumber, roadEdge.index, len(player.roads))
                    for roadEdge in possibleRoads]

        elif gameState.currState == 'PLAY':

            # FIXME: TRYING TO USE KNIGHT 2 TIMES!!! WHAT??? (fixed?)

            if not player.rolledTheDices and \
               not player.playedDevCard and \
                    player.mayPlayDevCards[KNIGHT_CARD_INDEX] and \
                            player.developmentCards[KNIGHT_CARD_INDEX] > 0:

                return [ UseKnightsCardAction( player.seatNumber, None, None ) ]

            if not player.rolledTheDices:

                return [ RollDicesAction( player.seatNumber ) ]

        elif gameState.currState == 'PLAY1':

            possibleActions     = [[], [], [], [], [], [], []]

            possibleRoads       = game.GetPossibleRoads(gameState, player)        # 0 - possibleRoads

            possibleSettlements = game.GetPossibleSettlements(gameState, player)  # 1 - possibleSettlements

            possibleCities      = game.GetPossibleCities(gameState, player)       # 2 - possibleCities

            canBuyADevCard      = game.CanBuyADevCard(gameState, player)          # 3 - buyDevCard

            possibleCardsToUse  = []                                              # 4 - useDevCard

            bankTrade           = player.GetPossibleBankTrades(game, player)      # 5 - bankTrade

            if not player.playedDevCard:

                if player.developmentCards[MONOPOLY_CARD_INDEX] > 0 and player.mayPlayDevCards[MONOPOLY_CARD_INDEX]:
                    possibleCardsToUse += player.GetMonopolyResource(player)

                if player.developmentCards[YEAR_OF_PLENTY_CARD_INDEX] > 0 and player.mayPlayDevCards[YEAR_OF_PLENTY_CARD_INDEX]:
                    possibleCardsToUse += player.GetYearOfPlentyResource(player)

                if player.developmentCards[ROAD_BUILDING_CARD_INDEX] > 0 and player.mayPlayDevCards[ROAD_BUILDING_CARD_INDEX]:
                    possibleCardsToUse += [ UseFreeRoadsCardAction(player.seatNumber, None, None) ]

            if len(possibleCardsToUse) > 0:
                possibleActions.append(possibleCardsToUse)

            if possibleRoads:
                possibleActions[0] = [BuildRoadAction(player.seatNumber, roadEdge.index,
                                                        len(player.roads))
                                            for roadEdge in possibleRoads]
            if possibleSettlements:
                possibleActions[1] = [BuildSettlementAction(player.seatNumber, setNode.index,
                                                             len(player.settlements))
                                        for setNode in possibleSettlements]
            if possibleCities:
                possibleActions[2] = [ BuildCityAction(player.seatNumber, setNode.index,
                                                        len(player.cities))
                                            for setNode in possibleCities]
            if canBuyADevCard:
                possibleActions[3] = [ BuyDevelopmentCardAction(player.seatNumber) ]
            possibleActions[4] = possibleCardsToUse
            possibleActions[5] = bankTrade
            possibleActions[6] = [ EndTurnAction(player.seatNumber) ]

            return possibleActions

        elif gameState.currState == 'PLACING_ROBBER':

            # Rolled out 7  * or *  Used a knight card
            return player.ChooseRobberPosition(game, player)

        elif gameState.currState == 'WAITING_FOR_DISCARDS':

            return [player.ChooseCardsToDiscard(game, player)]

        elif gameState.currState == 'WAITING_FOR_CHOICE':

            return [player.ChoosePlayerToStealFrom(game)]

        elif gameState.currState == "PLACING_FREE_ROAD1":

            possibleRoads = game.GetPossibleRoads(gameState, player, freeRoad=True)

            return [BuildRoadAction(player.seatNumber, roadEdge.index,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        elif gameState.currState == "PLACING_FREE_ROAD2":

            possibleRoads = game.GetPossibleRoads(gameState, player, freeRoad=True)

            return [BuildRoadAction(player.seatNumber, roadEdge.index,
                                    len(player.roads))
                    for roadEdge in possibleRoads]

        return None

    def DoMove(self, game):

        print("do move! {0}".format(time.clock()))

        if game.gameState.currPlayer != self.seatNumber and \
            game.gameState.currState != "WAITING_FOR_DISCARDS":
            return None

        #return self.Max_N(game, [0, 0, 0, 0], -1, 2)[1]
        return self.Alphabeta(game)[1]

    # TODO: ALPHABETA
    def Alphabeta(self, game, depth=5, alpha=float('-inf'), beta=float('inf'), player_turn=True):

        playerNumber = game.gameState.currPlayer

        score = self.GetGameStateReward(game.gameState, playerNumber)

        possibleActions = self.GetPossibleActions(game, game.gameState.players[playerNumber])

        if depth == 5 and possibleActions is not None:

            if len(possibleActions) == 1:

                return (None, possibleActions[0])

            elif game.gameState.currState == "PLAY1":

                for i in range(0, len(possibleActions)):

                    if possibleActions[i] is not None and len(possibleActions[i]) > 0:
                        break
                    if i == 6: # EndTurnAction
                        return (None, possibleActions[i][0])

        #has_available_moves = len(possibleActions) > 0
        someone_wins = (game.gameState.currState == "OVER")
        max_depth_reached = depth == 0

        if max_depth_reached or someone_wins: #or not has_available_moves:
            return (score, None)

        best = None

        if game.gameState.currState == "PLAY1":

            if possibleActions is not None and len(possibleActions) > 0:

                for i in range(0, len(possibleActions)):

                    if possibleActions[i] is not None:

                        for j in range(0, len(possibleActions[i])):

                            copyGame = copy.deepcopy(game)

                            possibleActions[i][j].ApplyAction(copyGame.gameState)

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
                                best = possibleActions[i][j]

                            else:

                                result = self.Alphabeta(copyGame, currentDepth, alpha, beta, player_turn=True)
                                value = result[0]
                                beta = min(beta, value)
                                if beta <= alpha:
                                    break
                                best = possibleActions[i][j]

        # FOR SETUP TURNS AND OTHER EVENTS
        else:

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


    # TODO -> turn this ugly algorithm from BADBADNOTGOOD to 'ok'
    def Max_N(self, game, values, depth, maxDepth):

        if depth >= maxDepth:

            return ([
                        self.GetGameStateReward(game.gameState, 0),
                        self.GetGameStateReward(game.gameState, 1),
                        self.GetGameStateReward(game.gameState, 2),
                        self.GetGameStateReward(game.gameState, 3)
                    ],
                    None)

        playerNumber = game.gameState.currPlayer

        possibleActions = self.GetPossibleActions(game, game.gameState.players[playerNumber])

        if depth == -1 and possibleActions is not None:

            if len(possibleActions) == 1:

                return (values, possibleActions[0])

            elif game.gameState.currState == "PLAY1":

                for i in range(0, len(possibleActions)):

                    if possibleActions[i] is not None and len(possibleActions[i]) > 0:
                        break
                    if i == 6: # EndTurnAction
                        return (values, possibleActions[i][0])

            depth = 0

        logging.debug("possible actions = {0}".format(possibleActions))

        best = None

        # FOR "PROPER" TURNS
        if game.gameState.currState == "PLAY1":

            if possibleActions is not None and len(possibleActions) > 0:

                for i in range(0, len(possibleActions)):

                    if possibleActions[i] is not None:

                        for j in range(0, len(possibleActions[i])):

                            copyGame = copy.deepcopy(game)

                            possibleActions[i][j].ApplyAction(copyGame.gameState)

                            if copyGame.gameState.currPlayer != playerNumber:
                                currentDepth = depth + 1
                            else:
                                currentDepth = depth

                            result = self.Max_N(copyGame, list(values), currentDepth, maxDepth)

                            value = result[0][playerNumber]

                            if value > values[playerNumber]:

                                values[playerNumber] = value

                                best = possibleActions[i][j]

                                #print("Turn: best! {0}".format(best))

                                values = result[0]

        # FOR SETUP TURNS AND OTHER EVENTS
        else:

            if possibleActions is not None and len(possibleActions) > 0:

                for i in range(0, len(possibleActions)):

                    copyGame = copy.deepcopy(game)

                    possibleActions[i].ApplyAction(copyGame.gameState)

                    if copyGame.gameState.currPlayer != playerNumber:
                        currentDepth = depth + 1
                    else:
                        currentDepth = depth

                    result = self.Max_N(copyGame, list(values), currentDepth, maxDepth)

                    value = result[0][playerNumber]

                    if value > values[playerNumber]:

                        values[playerNumber] = value

                        best = possibleActions[i]

                        #print("N-turn: best! {0}".format(best))

                        values = result[0]

        return (values, best)

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