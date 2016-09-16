import random
from CatanBoard import *
from JSettlersMessages import *
from CatanAction import *
import logging

class Game:

    def __init__(self, gameState):

        self.gameState = gameState

    def AddPlayer(self, player, index):

        self.gameState.players[index] = player

    def CreateBoard(self, message):
        # Hexes
        for i in range(0, len(message.hexes)):

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

        for i in range(0, len(hex_indicies)):

            portType = g_board_indicators[ message.hexes[hex_indicies[i]] ]

            self.gameState.boardNodes[ harbour_coords[i][0] ].portType = portType
            self.gameState.boardNodes[ harbour_coords[i][1] ].portType = portType

        # Robber:
        self.gameState.robberPos = message.robberpos

        # DEBUG FOR HARBORS:
        #for nodeIndex, node in self.gameState.boardNodes.items():
        #    logging.debug("Node id = {0}, Port Type = {1}".format(hex(nodeIndex), node.portType))

    def CanBuildRoad(self, gameState, player, edge, roadIndex, setUpPhase = False):

        # check if there is a road in this edge

        if edge.construction is not None:

            return False

        # check for near settlements

        for nodeIndex in edge.GetAdjacentNodes():

            if setUpPhase:
                # when the game is on setUpPhase, we can only build roads near our recently built settlement:
                if gameState.boardNodes[nodeIndex].construction is not None:

                    if gameState.boardNodes[nodeIndex].construction.owner == player.seatNumber and \
                       gameState.boardNodes[nodeIndex].construction.index == roadIndex:
                        return True
                    else:
                        return False

                return False

            else:
                # normal rules apply otherwise: our roads can be constructed near our settlements
                if gameState.boardNodes[nodeIndex].construction is not None:
                    if gameState.boardNodes[nodeIndex].construction.owner == player.seatNumber:
                        return True

        # if there are no settlements or cities that we own near here, check for other roads...
        for edgeIndex in edge.GetAdjacentEdges():

            edge = gameState.boardEdges[edgeIndex]

            if edge.construction is not None:

                if edge.construction.owner == player.seatNumber:
                    return True
                else:
                    return False

        return False

    def CanBuildSettlement(self, gameState, player, node, setUpPhase = False):

        #step 1: check if someone already build a settlement or city in this node

        if node.construction is not None:

            return False

        #step 2: check if node respects piece connectivity, if not in setUpPhase
        if not setUpPhase:

            foundConnection = False

            for edgeIndex in node.GetAdjacentEdges():

                edge = gameState.boardEdges[edgeIndex]

                if edge.construction is not None and edge.construction.owner == player.seatNumber:
                    foundConnection = True
                    break

            if not foundConnection:
                return False

        #step 3: check if node respects the distance rule
        for nodeIndex in node.GetAdjacentNodes():

            if gameState.boardNodes[nodeIndex].construction is not None:
                return False

        return True

    def CanBuyADevCard(self, gameState, player):

        #return gameState.devCards > 0 and player.CanAfford(BuyDevelopmentCardAction.cost)

        if gameState.devCards > 0 and player.CanAfford(BuyDevelopmentCardAction.cost):

            logging.info(">>>> CAN BUY CARD!")
            return True
        else:

            logging.info(">>>> CAN'T BUY A CARD!")
            return False

    def GetPossibleRoads(self, gameState, player, setUpPhase = False, freeRoad = False):

        if not setUpPhase and not freeRoad and\
                not player.CanAfford(BuildRoadAction.cost) \
                or not player.HavePiece(g_pieces.index('ROADS')):
            return None

        return [edge for edge in
                gameState.GetConstructableEdges() if
                self.CanBuildRoad(gameState, player, edge, len(player.roads), setUpPhase)]

    def GetPossibleSettlements(self, gameState, player, setUpPhase = False):

        if not setUpPhase and \
                not player.CanAfford(BuildSettlementAction.cost) \
                or not player.HavePiece(g_pieces.index('SETTLEMENTS')):
            return None

        return [node for node in
                gameState.GetConstructableNodes() if
                self.CanBuildSettlement(gameState, player, node, setUpPhase)]

    def GetPossibleCities(self, gameState, player):

        if not player.CanAfford(BuildCityAction.cost) \
                or not player.HavePiece(g_pieces.index('CITIES')):
            return None

        return [gameState.boardNodes[settlement] for settlement in player.settlements]

    def GetDiceRoll(self):

        return random.randint(1, 6) + random.randint(1, 6)

    def GetPossibleRobberPositions(self, gameState, player):

        oceanHexes = \
            [0x17, 0x39, 0x5b, 0x7d,
             0x15, 0x9d, 0x13, 0xbd,
             0x11, 0xdd, 0x31, 0xdb,
             0x51, 0xd9, 0x71, 0x93,
             0xb5, 0xd7, gameState.robberPos]

        possibleRobberPositions = list(set(g_boardHexes) - set(oceanHexes))

        return [PlaceRobberAction(player.seatNumber, position) for position in possibleRobberPositions]

class GameState:

    def __init__(self):

        self.boardHexes  = { hexIndex  : BoardHex(hexIndex)   for hexIndex  in g_boardHexes }
        self.boardNodes  = { nodeIndex : BoardNode(nodeIndex) for nodeIndex in g_boardNodes }
        self.boardEdges  = { edgeIndex : BoardEdge(edgeIndex) for edgeIndex in g_boardEdges }

        self.currState   = None
        self.currPlayer  = -1
        self.currTurn    = 0
        self.players     = [ None, None, None, None ]
        self.robberPos   = 0
        self.devCards    = 25

        self.longestRoadPlayer = 0
        self.largestArmPlayer  = 0

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

    def ApplyAction(self, action, fromServer = False):

        if action.type == 'BuildRoad':

            newRoad = Construction(g_constructionTypes[0], action.playerNumber, action.index, action.position)

            self.players[action.playerNumber].roads.append(action.position)

            self.boardEdges[action.position].construction = newRoad

            if not fromServer:
                self.players.resources = [x1 - x2 for (x1, x2) in zip(self.players.resources, action.cost)]

        elif action.type == 'BuildSettlement':

            newSettlement = Construction(g_constructionTypes[1], action.playerNumber, action.index, action.position)

            self.players[action.playerNumber].settlements.append(action.position)

            self.boardNodes[action.position].construction = newSettlement

            if not fromServer:
                self.players.resources = [x1 - x2 for (x1, x2) in zip(self.players.resources, action.cost)]

        elif action.type == 'BuildCity':

            newCity = Construction(g_constructionTypes[2], action.playerNumber, action.index, action.position)

            self.players[action.playerNumber].settlements.remove(action.position)

            self.players[action.playerNumber].cities.append(action.position)

            self.boardNodes[action.position].construction = newCity

            if not fromServer:
                self.players.resources = [x1 - x2 for (x1, x2) in zip(self.players.resources, action.cost)]