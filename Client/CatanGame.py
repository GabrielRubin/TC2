import random
from CatanBoard import *
from JSettlersMessages import *
import logging

class Game:

    def __init__(self, gameState):

        self.gameState = gameState

    def CreateBoard(self, message):

        # HEXES:
        self.gameState.boardHexes[0x37].resource = message.hexes[5 ]
        self.gameState.boardHexes[0x37].number   = g_messageNumberToGameNumber[message.numbers[5 ]]
        self.gameState.boardHexes[0x59].resource = message.hexes[6 ]
        self.gameState.boardHexes[0x59].number   = g_messageNumberToGameNumber[message.numbers[6 ]]
        self.gameState.boardHexes[0x7b].resource = message.hexes[7 ]
        self.gameState.boardHexes[0x7b].number   = g_messageNumberToGameNumber[message.numbers[7 ]]
        self.gameState.boardHexes[0x35].resource = message.hexes[10]
        self.gameState.boardHexes[0x35].number   = g_messageNumberToGameNumber[message.numbers[10]]
        self.gameState.boardHexes[0x57].resource = message.hexes[11]
        self.gameState.boardHexes[0x57].number   = g_messageNumberToGameNumber[message.numbers[11]]
        self.gameState.boardHexes[0x79].resource = message.hexes[12]
        self.gameState.boardHexes[0x79].number   = g_messageNumberToGameNumber[message.numbers[12]]
        self.gameState.boardHexes[0x9b].resource = message.hexes[13]
        self.gameState.boardHexes[0x9b].number   = g_messageNumberToGameNumber[message.numbers[13]]
        self.gameState.boardHexes[0x33].resource = message.hexes[16]
        self.gameState.boardHexes[0x33].number   = g_messageNumberToGameNumber[message.numbers[16]]
        self.gameState.boardHexes[0x55].resource = message.hexes[17]
        self.gameState.boardHexes[0x55].number   = g_messageNumberToGameNumber[message.numbers[17]]
        self.gameState.boardHexes[0x77].resource = message.hexes[18]
        self.gameState.boardHexes[0x77].number   = g_messageNumberToGameNumber[message.numbers[18]]
        self.gameState.boardHexes[0x99].resource = message.hexes[19]
        self.gameState.boardHexes[0x99].number   = g_messageNumberToGameNumber[message.numbers[19]]
        self.gameState.boardHexes[0xbb].resource = message.hexes[20]
        self.gameState.boardHexes[0xbb].number   = g_messageNumberToGameNumber[message.numbers[20]]
        self.gameState.boardHexes[0x53].resource = message.hexes[23]
        self.gameState.boardHexes[0x53].number   = g_messageNumberToGameNumber[message.numbers[23]]
        self.gameState.boardHexes[0x75].resource = message.hexes[24]
        self.gameState.boardHexes[0x75].number   = g_messageNumberToGameNumber[message.numbers[24]]
        self.gameState.boardHexes[0x97].resource = message.hexes[25]
        self.gameState.boardHexes[0x97].number   = g_messageNumberToGameNumber[message.numbers[25]]
        self.gameState.boardHexes[0xb9].resource = message.hexes[26]
        self.gameState.boardHexes[0xb9].number   = g_messageNumberToGameNumber[message.numbers[26]]
        self.gameState.boardHexes[0x73].resource = message.hexes[29]
        self.gameState.boardHexes[0x73].number   = g_messageNumberToGameNumber[message.numbers[29]]
        self.gameState.boardHexes[0x95].resource = message.hexes[30]
        self.gameState.boardHexes[0x95].number   = g_messageNumberToGameNumber[message.numbers[30]]
        self.gameState.boardHexes[0xb7].resource = message.hexes[31]
        self.gameState.boardHexes[0xb7].number   = g_messageNumberToGameNumber[message.numbers[31]]

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


    def GetDiceRoll(self):

        return random.randint(1, 6) + random.randint(1, 6)

    def GetPossibleActions(self, player):
        pass

class GameState:

    def __init__(self):

        self.boardHexes  = { hexIndex  : BoardHex(hexIndex)   for hexIndex  in g_boardHexes }
        self.boardNodes  = { nodeIndex : BoardNode(nodeIndex) for nodeIndex in g_boardNodes }
        self.boardEdges  = { edgeIndex : BoardEdge(edgeIndex) for edgeIndex in g_boardEdges }

        self.currState   = -1
        self.currPlayer  = 0
        self.currTurn    = 0
        self.players     = []
        self.robberPos   = 0

        self.longestRoadPlayer = 0
        self.largestArmPlayer  = 0

    def GetNextState(self, action):
        pass

class Action:

    def __init__(self):
        pass