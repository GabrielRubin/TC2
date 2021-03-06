import os
from CatanAction import *
import cPickle
import datetime
from GameData import GameData

class Game:

    def __init__(self, gameState):

        self.gameState   = gameState
        self.gameData    = GameData()
        self.recordData  = False

    def AddPlayer(self, player, index):

        self.gameState.players[index] = player

    def CreateBoard(self, message):

        self.gameState.boardConfig = message.text

        # Hexes
        for i in xrange(0, len(message.hexes)):

            self.gameState.boardHexes[g_boardHexes[i]].SetTerrain(message.hexes[i])

            self.gameState.boardHexes[g_boardHexes[i]].number = g_messageNumberToGameNumber[message.numbers[i]]

        # DEBUG FOR HEXES:
        #indexedHex = [self.gameState.boardHexes[g_boardHexes[i]] for i in range(len(g_boardHexes))]
        #logging.debug("Board Hexes   = {0}".format([h.terrain for h in indexedHex]))
        #logging.debug("Board Numbers = {0}".format([h.number  for h in indexedHex]))

        # HARBORS (nodes):
        harbour_coords = [(0x27, 0x38), (0x5a, 0x6b), (0x9c, 0xad),
                          (0x25, 0x34), (0xcd, 0xdc), (0x43, 0x52),
                          (0xc9, 0xda), (0x72, 0x83), (0xa5, 0xb6)]

        hex_indicies   = [0, 2, 8, 9, 21, 22, 32, 33, 35]

        for i in xrange(0, len(hex_indicies)):

            portType = g_board_indicators[ message.hexes[hex_indicies[i]] ]

            self.gameState.boardNodes[ harbour_coords[i][0] ].portType = portType
            self.gameState.boardNodes[ harbour_coords[i][1] ].portType = portType

        # Robber:
        self.gameState.robberPos = message.robberpos

        # DEBUG FOR HARBORS:
        #for nodeIndex, node in self.gameState.boardNodes.items():
        #    logging.debug("Node id = {0}, Port Type = {1}".format(hex(nodeIndex), node.portType))

class GameState(object):

    def __init__(self):

        # board
        self.boardHexes  = { hexIndex  : BoardHex(hexIndex)   for hexIndex  in g_boardHexes }
        self.boardNodes  = { nodeIndex : BoardNode(nodeIndex) for nodeIndex in g_boardNodes }
        self.boardEdges  = { edgeIndex : BoardEdge(edgeIndex) for edgeIndex in g_boardEdges }

        # flag that informs if Nodes/Edges must be updated after a construction is done in the board -- only update players that need to so
        self.updatePlayerNodes  = [True, True, True, True]
        self.updatePlayerEdges  = [True, True, True, True]
        
        # keeps track of constructable Nodes/Edges and possible robber position, to save processing time
        self.constructableNodes = cPickle.loads(cPickle.dumps(g_constructableNodes, -1))
        self.constructableEdges = cPickle.loads(cPickle.dumps(g_constructableEdges, -1))
        self.possibleRobberPos  = cPickle.loads(cPickle.dumps(g_possibleRobberPos,  -1))

        self.currState            = None
        self.currPlayer           = -1
        self.playerBeforeDiscards = -1
        self.currTradeOffer       = None
        self.currTurn             = 0
        self.players              = [ None, None, None, None ]
        self.robberPos            = 0
        self.dicesAreRolled       = False

        # development cards by index
        self.developmentCardsDeck = [14, 2, 2, 2, 5]

        self.longestRoadPlayer  = -1
        self.largestArmyPlayer  = -1

        self.startingPlayer = -1
        self.setupDone      = False
        self.winner         = -1
        self.isGameOver     = False
        self.isLogGenerated = False
        
        # flag to indicate that the longest road should be checked. Only True when a player with 4+ roads constructs a new road
        self.checkLongestRoad = False

        self.boardConfig = None

    def ShiftPlayerToFirstSeat(self, player):

        if player.seatNumber == 0:
            return

        tgtPlayerCurrSeatNumber = player.seatNumber
        playerInFirstSeat = self.players[0]

        self.players[tgtPlayerCurrSeatNumber] = playerInFirstSeat
        self.players[0] = player

        player.seatNumber = 0
        playerInFirstSeat.seatNumber = tgtPlayerCurrSeatNumber

        if self.currPlayer == tgtPlayerCurrSeatNumber:
            self.currPlayer = 0
        elif self.currPlayer == 0:
            self.currPlayer = tgtPlayerCurrSeatNumber

        if self.longestRoadPlayer == tgtPlayerCurrSeatNumber:
            self.longestRoadPlayer = 0
        elif self.longestRoadPlayer == 0:
            self.longestRoadPlayer = tgtPlayerCurrSeatNumber

        if self.largestArmyPlayer == tgtPlayerCurrSeatNumber:
            self.largestArmyPlayer = 0
        elif self.largestArmyPlayer == 0:
            self.largestArmyPlayer = tgtPlayerCurrSeatNumber

        if self.winner == tgtPlayerCurrSeatNumber:
            self.winner = 0
        elif self.winner == 0:
            self.winner = tgtPlayerCurrSeatNumber

        for edge in self.boardEdges:
            if edge.construction is not None:
                if edge.construction.owner == tgtPlayerCurrSeatNumber:
                    edge.construction.owner = 0
                elif edge.construction.owner == 0:
                    edge.construction.owner = tgtPlayerCurrSeatNumber

        for node in self.boardNodes:
            if node.construction is not None:
                if node.construction.owner == tgtPlayerCurrSeatNumber:
                    node.construction.owner = 0
                elif node.construction.owner == 0:
                    node.construction.owner = tgtPlayerCurrSeatNumber

    def FinishSetup(self):

        def UpdateNode(node):
            self.constructableNodes[node][0] = False
            self.constructableNodes[node][1] = False
            self.constructableNodes[node][2] = False
            self.constructableNodes[node][3] = False
            for adjNode in self.boardNodes[node].adjacentNodes:
                if adjNode is not None and adjNode in self.constructableNodes:
                    self.constructableNodes[adjNode][0] = False
                    self.constructableNodes[adjNode][1] = False
                    self.constructableNodes[adjNode][2] = False
                    self.constructableNodes[adjNode][3] = False

        self.setupDone = True

        for player in self.players:
            UpdateNode(player.settlements[0])
            UpdateNode(player.settlements[1])
            self.UpdatePossibleSettlements(player.seatNumber, 'ROAD', player.roads[0])
            self.UpdatePossibleSettlements(player.seatNumber, 'ROAD', player.roads[0])

    def UpdateRobDiceProduction(self, gameState, pastRobberPos, newRobberPos):

        def UpdateDiceProduction(position, multiplier):
            production = gameState.boardHexes[position].production

            if production is not None:

                for nodePos in gameState.boardHexes[position].adjacentNodes:

                    construction = gameState.boardNodes[nodePos].construction

                    if construction is not None:

                        diceNumber = gameState.boardHexes[position].number

                        if construction.type == 'SETTLEMENT':
                            self.players[construction.owner].diceProduction[diceNumber][g_resources.index(production)] += 1 * multiplier
                        else:
                            self.players[construction.owner].diceProduction[diceNumber][g_resources.index(production)] += 2 * multiplier

        if pastRobberPos is not None:
            UpdateDiceProduction(pastRobberPos, 1)
        if newRobberPos is not None:
            UpdateDiceProduction(newRobberPos, -1)

    def CanBuildRoad(self, player, edge, roadIndex, setUpPhase = False):

        # check if there is a road in this edge

        if edge.construction is not None:
            return False

        # check for near settlements
        for nodeIndex in edge.adjacentNodes:

            if setUpPhase:
                # when the game is on setUpPhase, we can only build roads near our recently built settlement:
                if self.boardNodes[nodeIndex].construction is not None:

                    if self.boardNodes[nodeIndex].construction.owner == player.seatNumber and \
                                    self.boardNodes[nodeIndex].construction.index == roadIndex:
                        return True
                    else:
                        return False

            else:
                # normal rules apply otherwise: our roads can be constructed near our settlements
                if self.boardNodes[nodeIndex].construction is not None:
                    if self.boardNodes[nodeIndex].construction.owner == player.seatNumber:
                        return True
                    else:
                        return False

        # if there are no settlements or cities that we own near here, check for other roads...
        for edgeIndex in edge.adjacentEdges:

            edge = self.boardEdges[edgeIndex]

            if edge.construction is not None:

                if edge.construction.owner == player.seatNumber:
                    return True
                else:
                    return False

        return False

    def CanBuildSettlement(self, player, node, setUpPhase = False):

        #step 1: check if someone already build a settlement or city in this node
        if node.construction is not None:
            return False

        #step 2: check if node respects piece connectivity, if not in setUpPhase
        if not setUpPhase:

            foundConnection = False

            for edgeIndex in node.adjacentEdges:

                edge = self.boardEdges[edgeIndex]

                if edge.construction is not None and edge.construction.owner == player.seatNumber:
                    foundConnection = True
                    break

            if not foundConnection:
                return False

        #step 3: check if node respects the distance rule
        for nodeIndex in node.adjacentNodes:

            if self.boardNodes[nodeIndex].construction is not None:
                return False

        return True

    def CanBuyADevCard(self, player):

        if sum(self.developmentCardsDeck) > 0 and player.CanAfford(BuyDevelopmentCardAction.cost):
            return True
        else:
            return False

    def UpdatePossibleRoads(self, playerNumber, constructionType, position):

        if constructionType == 'ROAD':
            self.updatePlayerEdges[0] = True
            self.updatePlayerEdges[1] = True
            self.updatePlayerEdges[2] = True
            self.updatePlayerEdges[3] = True

            self.constructableEdges[position][0] = False
            self.constructableEdges[position][1] = False
            self.constructableEdges[position][2] = False
            self.constructableEdges[position][3] = False

            def verifyEdge(edgeIndex, adjacentEdgeIndex):
                for node in self.boardEdges[edgeIndex].adjacentNodes:
                    construction = self.boardNodes[node].construction
                    if construction is not None and construction.owner != playerNumber:
                        if node in self.boardEdges[adjacentEdgeIndex].adjacentNodes:
                            return False
                return True

            for edge in self.boardEdges[position].adjacentEdges:
                if edge in self.constructableEdges and self.boardEdges[edge].construction is None:
                    self.constructableEdges[edge][playerNumber] = verifyEdge(position, edge)

        elif constructionType == 'SETTLEMENT':

            def haveConnection(nodeIndex, edgeIndex, seatNumber):
                for adjEdge in self.boardEdges[edgeIndex].adjacentEdges:
                    tgtEdge = self.boardEdges[adjEdge]
                    if tgtEdge.construction is not None \
                            and tgtEdge.construction.owner == seatNumber \
                            and nodeIndex not in tgtEdge.adjacentNodes:
                        return True
                return False

            for edge in self.boardNodes[position].adjacentEdges:
                if edge in self.constructableEdges and self.boardEdges[edge].construction is None:
                    for player in self.players:
                        if player.seatNumber == playerNumber:
                            continue
                        self.constructableEdges[edge][player.seatNumber] = haveConnection(position, edge, player.seatNumber)

            self.updatePlayerEdges[0] = True
            self.updatePlayerEdges[1] = True
            self.updatePlayerEdges[2] = True
            self.updatePlayerEdges[3] = True

    def UpdatePossibleSettlements(self, playerNumber, constructionType, position, isSetup=False):

        # updates the static list of possible settlements to save processing time in simulations
        
        if constructionType == 'ROAD':

            def isNodeAvailable(nodeIndex):
                if nodeIndex in self.constructableNodes and self.boardNodes[nodeIndex].construction is not None:
                    return False
                for adjNode in self.boardNodes[nodeIndex].adjacentNodes:
                    if adjNode in self.constructableNodes and self.boardNodes[adjNode].construction is not None:
                        return False
                return True

            for node in self.boardEdges[position].adjacentNodes:
                self.constructableNodes[node][playerNumber] = isNodeAvailable(node)

            self.updatePlayerNodes[playerNumber] = True

        elif constructionType == 'SETTLEMENT':

            self.updatePlayerNodes[0] = True
            self.updatePlayerNodes[1] = True
            self.updatePlayerNodes[2] = True
            self.updatePlayerNodes[3] = True

            self.constructableNodes[position][0] = isSetup
            self.constructableNodes[position][1] = isSetup
            self.constructableNodes[position][2] = isSetup
            self.constructableNodes[position][3] = isSetup

            for node in self.boardNodes[position].adjacentNodes:
                if node in self.constructableNodes:
                    self.constructableNodes[node][0] = isSetup
                    self.constructableNodes[node][1] = isSetup
                    self.constructableNodes[node][2] = isSetup
                    self.constructableNodes[node][3] = isSetup

    def GetPossibleRoads(self, player, setUpPhase = False):

        if self.updatePlayerEdges[player.seatNumber]:

            if setUpPhase:
                if self.currState == "START1B":
                    player.possibleRoads = [edge for edge in
                                            self.boardNodes[player.settlements[0]].adjacentEdges if
                                            edge in self.constructableEdges]
                else:
                    player.possibleRoads = [edge for edge in
                                            self.boardNodes[player.settlements[1]].adjacentEdges if
                                            edge in self.constructableEdges]
            else:
                player.possibleRoads = [edge for edge in
                                        self.constructableEdges if self.constructableEdges[edge][player.seatNumber]]

            self.updatePlayerEdges[player.seatNumber] = False

        return player.possibleRoads

    def GetPossibleSettlements(self, player, setUpPhase = False):

        if self.updatePlayerNodes[player.seatNumber]:

            if setUpPhase:
                player.possibleSettlements = [node for node in
                                              self.constructableNodes if
                                              not self.constructableNodes[node][player.seatNumber]]
            else:
                player.possibleSettlements = [node for node in
                                              self.constructableNodes if
                                              self.constructableNodes[node][player.seatNumber]]

            self.updatePlayerNodes[player.seatNumber] = False

        return player.possibleSettlements

    def GetPossibleCities(self, player):

        return [settlement for settlement in player.settlements]

    def IsTerminal(self):

        return self.currState == "OVER"

    def GetPossiblePlayersToSteal(self, playerIndex):

        robberHex       = self.boardHexes[self.robberPos]

        possibleNodes   = [self.boardNodes[nodeIndex] for nodeIndex in robberHex.adjacentNodes]

        possiblePlayers = []

        for node in possibleNodes:
            if node.construction is not None and node.construction.owner not in possiblePlayers \
                and node.construction.owner != playerIndex and \
                sum(self.players[node.construction.owner].resources) > 0: #THE OTHER PLAYERS RESOURCES HAVE TO BE > 0!

                possiblePlayers.append(node.construction.owner)

        return possiblePlayers

    def UpdateDevCardsFromServer(self, currCount):

        if currCount < sum(self.developmentCardsDeck):

            diff = max(sum(self.developmentCardsDeck) - currCount, 0)

            currDevCardsPopulation = [0 for i in range(0, self.developmentCardsDeck[0])] + \
                                     [1 for i in range(0, self.developmentCardsDeck[1])] + \
                                     [2 for i in range(0, self.developmentCardsDeck[2])] + \
                                     [3 for i in range(0, self.developmentCardsDeck[3])] + \
                                     [4 for i in range(0, self.developmentCardsDeck[4])]

            usedDevCards = random.sample(currDevCardsPopulation, diff)

            for index in xrange(0, len(usedDevCards)):
                self.developmentCardsDeck[usedDevCards[index]] -= 1

    def SetLargestArmy(self, playerNumber):

        if playerNumber < 0 or playerNumber > len(self.players):
            return

        if self.largestArmyPlayer != -1:
            self.players[self.largestArmyPlayer].UpdateLargestArmy(False)

        self.largestArmyPlayer = playerNumber

        self.players[self.largestArmyPlayer].UpdateLargestArmy(True)

    def SetLongestRoad(self, playerNumber):

        if playerNumber < 0 or playerNumber > len(self.players):
            return

        if self.longestRoadPlayer != -1:
            self.players[self.longestRoadPlayer].biggestRoad = False

        self.longestRoadPlayer = playerNumber

        self.players[self.longestRoadPlayer].biggestRoad = True

    def DrawDevCard(self, playerNumber):

        if sum(self.developmentCardsDeck) > 0:

            currDevCardsPopulation = [0 for i in range(0, self.developmentCardsDeck[0])] + \
                                     [1 for i in range(0, self.developmentCardsDeck[1])] + \
                                     [2 for i in range(0, self.developmentCardsDeck[2])] + \
                                     [3 for i in range(0, self.developmentCardsDeck[3])] + \
                                     [4 for i in range(0, self.developmentCardsDeck[4])]

            index = random.choice(currDevCardsPopulation)

            # print("{0} draw a card! He got this: {1}".format(self.players[playerNumber].name,
            #                                                  g_developmentCards[index]))

            self.developmentCardsDeck[index] -= 1
            self.players[playerNumber].developmentCards[index] += 1
            self.players[playerNumber].UpdateMayPlayDevCards(recentlyCardIndex=index)

    def UpdateLongestRoad(self, player = -1):

        if player != -1 and self.longestRoadPlayer != -1:
            tgtPlayer = self.players[player]
            tgtPlayer.roadCount += 1
            if tgtPlayer.roadCount <= self.players[self.longestRoadPlayer].roadCount:
                return
            else:
                roadCount = tgtPlayer.CountRoads(self)
                if roadCount >= 5 and roadCount > self.players[self.longestRoadPlayer].roadCount:
                    self.SetLongestRoad(player)

            tgtPlayer.updateVictoryPoints = True
            return

        roadCount = [0 for i in range(0, len(self.players))]

        for i in xrange(0, len(self.players)):
            roadCount[i] = self.players[i].CountRoads(self)
            self.players[i].updateVictoryPoints = True

        maxRoads = max(roadCount)

        if maxRoads >= 5:

            if roadCount.count(maxRoads) > 1 and self.longestRoadPlayer != -1 and \
                roadCount[self.longestRoadPlayer] == maxRoads:
                return

            self.SetLongestRoad(roadCount.index(maxRoads))

    def UpdateLargestArmy(self):

        totalKnights = [self.players[i].knights for i in range(0, len(self.players))]

        maxKnights = max(totalKnights)

        if maxKnights >= 3:

            if totalKnights.count(maxKnights) > 1 and self.largestArmyPlayer != -1 and \
                self.players[self.largestArmyPlayer].knights == maxKnights:
                return

            self.SetLargestArmy(totalKnights.index(maxKnights))

    def GetConstructableNodes(self):

        oceanNodes = \
            [0x18, 0x3a, 0x5c, 0x7e, 0x8f,
             0x07, 0x29, 0x4b, 0x6d, 0x16,
             0x9e, 0x05, 0xaf, 0x14, 0xbe,
             0x03, 0xcf, 0x12, 0xde, 0x01,
             0xef, 0x10, 0xfe, 0x21, 0xed,
             0x30, 0xfc, 0x41, 0xeb, 0x50,
             0xfa, 0x61, 0xe9, 0x70, 0x92,
             0xb4, 0xd6, 0xf8, 0x81, 0xa3,
             0xc5, 0xe7]

        return [self.boardNodes[i] for i in list(set(g_boardNodes) - set(oceanNodes))]

    def GetConstructableEdges(self):

        oceanEdges = \
            [0x07, 0x18, 0x29, 0x3a, 0x4b, 0x5c, 0x6d, 0x7e,
             0x06, 0x28, 0x4a, 0x6c, 0x8e, 0x05, 0x16, 0x8d,
             0x9e, 0x04, 0xae, 0x03, 0x14, 0xad, 0xbe, 0x02,
             0xce, 0x01, 0x12, 0xcd, 0xde, 0x00, 0xee, 0x10,
             0x21, 0xdc, 0xed, 0x20, 0xec, 0x30, 0x41, 0xda,
             0xeb, 0x40, 0xea, 0x50, 0x61, 0xd8, 0xe9, 0x60,
             0x82, 0xa4, 0xc6, 0xe8, 0x70, 0x81, 0x92, 0xa3,
             0xb4, 0xc5, 0xd6, 0xe7]

        return [self.boardEdges[i] for i in list(set(g_boardEdges) - set(oceanEdges))]

    def GetPossibleRobberPositions(self):

        #DISCONSIDER OCEAN AND CURRENT ROBBER HEXES
        invalidHexes = \
            [0x17, 0x39, 0x5b, 0x7d,
             0x15, 0x9d, 0x13, 0xbd,
             0x11, 0xdd, 0x31, 0xdb,
             0x51, 0xd9, 0x71, 0x93,
             0xb5, 0xd7]

        return list(set(g_boardHexes) - set(invalidHexes))
