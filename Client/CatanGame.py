import random
from CatanBoard import *
from JSettlersMessages import *
import logging

class Game:

    def __init__(self, gameState):

        self.gameState = gameState

    def AddPlayer(self, player):

        self.gameState.players.append(player)

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

    def GetPossibleActions(self, player, gameState = None, ignoreTurn = False):

        if gameState is None:
            gameState = self.gameState

        if not ignoreTurn and self.gameState.currPlayer.name != player.name:
            return None

        if   gameState.currState == 'START1A':

            pass

        elif gameState.currState == 'START1B':

            pass

        elif gameState.currState == 'START2A':

            pass

        elif gameState.currState == 'START2B':

            pass

        elif gameState.currState == 'PLAY':

            pass

        elif gameState.currState == 'PLAY1':

            pass

        elif gameState.currState == 'PLACING_ROBBER':

            pass

        elif gameState.currState == 'WAITING_FOR_DISCARDS':

            pass

        elif gameState.currState == 'WAITING_FOR_CHOICE':

            pass

        elif gameState.currState == 'WAITING_FOR_DISCOVERY':

            pass

        elif gameState.currState == 'WAITING_FOR_MONOPOLY':

            pass

        return None

    def CanBuildRoad(self, gameState, player, edge):

        # check for near settlements

        for nodeIndex in edge.GetAdjacentNodes():

            if gameState.boardNodes[nodeIndex].construction.owner == player.name:
                return True

        # if there are none, check for near roads

        for edgeIndex in edge.GetAdjacentEdges():

            if gameState.boardEdges[edgeIndex].owner == player.name:
                return True

        return False

    def CanBuildSettlement(self, gameState, player, node):

        #step 1: check if node respects piece connectivity

        foundConnection = False

        for edgeIndex in node.GetAdjacentEdges():

            if gameState.boardEdges[edgeIndex].owner == player.name:
                foundConnection = True
                break

        if not foundConnection:
            return False

        #step 2: check if node respects the distance rule

        for nodeIndex in node.GetAdjacentNodes():

            if gameState.boardNodes[nodeIndex].construction is not None:
                return False

        return True

    def GetPossibleRoads(self, gameState, player):

        possibleRoads = [edge for edge in
                         gameState.GetConstructableEdges() if
                         self.CanBuildRoad(gameState, player, edge)]

        return [BuildRoadAction(player, edge) for edge in possibleRoads]

    def GetPossibleSettlements(self, gameState, player):

        possibleSettlements = [node for node in
                               gameState.GetConstructableNodes() if
                               self.CanBuildSettlement(node)]

        return [BuildSettlementAction(player, node) for node in possibleSettlements]

    def GetPossibleCities(self, gameState, player):

        possibleCities = []

        for construction in player.constructions:
            if construction.type == 'Settlement':
                possibleCities.append(BuildCityAction(construction))

        return possibleCities

    def GetDiceRoll(self):

        return random.randint(1, 6) + random.randint(1, 6)

class GameState:

    def __init__(self):

        self.boardHexes  = { hexIndex  : BoardHex(hexIndex)   for hexIndex  in g_boardHexes }
        self.boardNodes  = { nodeIndex : BoardNode(nodeIndex) for nodeIndex in g_boardNodes }
        self.boardEdges  = { edgeIndex : BoardEdge(edgeIndex) for edgeIndex in g_boardEdges }

        self.currState   = None
        self.currPlayer  = 0
        self.currTurn    = 0
        self.players     = []
        self.robberPos   = 0

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

    def GetNextState(self, action):
        pass

g_ActionType = \
[
    'BuildRoad',
    'BuildSettlement',
    'BuildCity',
    'BuyDevelopmentCard',
    'UseKnightsCard',
    'UseMonopolyCard',
    'UseYearOfPlentyCard',
    'UseFreeRoadsCard',
    'PlaceRobber'
]

class Action:

    def __init__(self):
        pass

class BuildRoadAction(Action):

    type = 'BuildRoad'
    cost = [ 1,  # brick
             0,  # ore
             0,  # wool
             0,  # grain
             1 ] # lumber

    def __init__(self, playerName, targetEdge):

        self.playerName = playerName
        self.edge       = targetEdge

class BuildSettlementAction(Action):

    type = 'BuildSettlement'
    cost = [ 1,  # brick
             0,  # ore
             1,  # wool
             1,  # grain
             1 ] # lumber

    def __init__(self, playerName, targetNode):

        self.playerName = playerName
        self.node       = targetNode

class BuildCityAction(Action):

    type = 'BuildCity'
    cost = [ 0,  # brick
             3,  # ore
             0,  # wool
             2,  # grain
             0 ] # lumber

    def __init__(self, playerName, targetSettlement):

        self.playerName  = playerName
        self.settlement  = targetSettlement

class BuyDevelopmentCardAction(Action):

    type = 'BuyDevelopmentCard'
    cost = [ 0,  # brick
             1,  # ore
             1,  # wool
             1,  # grain
             0 ] # lumber

    def __init__(self, playerName):

        self.playerName = playerName

class UseKnightsCardAction(Action):

    type = 'UseKnightsCard'

    def __init__(self, playerName, newRobberPos, targetPlayerIndex):

        self.playerName        = playerName
        self.robberPos         = newRobberPos
        self.targetPlayerIndex = targetPlayerIndex

class UseMonopolyCardAction(Action):

    type = 'UseMonopolyCard'

    def __init__(self, playerName, resource):

        self.playerName  = playerName
        self.resource    = resource

class UseYearOfPlentyCardAction(Action):

    type = 'UseYearOfPlentyCard'

    def __init__(self, playerName, resource1, resource2):

        self.playerName  = playerName
        self.resource1   = resource1
        self.resource2   = resource2

class UseFreeRoadsCardAction(Action):

    type = 'UseFreeRoadsCard'

    def __init__(self, playerName, road1Edge, road2Edge):

        self.playerName  = playerName
        self.road1Edge   = road1Edge
        self.road2Edge   = road2Edge

class PlaceRobberAction(Action):

    type = 'PlaceRobber'

    def __init__(self, playerName, newRobberPos):

        self.playerName  = playerName
        self.robberPos   = newRobberPos