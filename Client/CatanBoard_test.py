import unittest

from Client.CatanBoard import *

class CatanBoardTest(unittest.TestCase):

    def testHexAdjHexes(self):

        respAdjHex = {

            0x17: [ None, None, None, 0x39, 0x15, 0x37 ],
            0x39: [ None, None, 0x17, 0x5b, 0x37, 0x59 ],
            0x5b: [ None, None, 0x39, 0x7d, 0x59, 0x7b ],
            0x7d: [ None, None, 0x5b, None, 0x7b, 0x9d ],
            0x15: [ None, 0x17, None, 0x37, 0x13, 0x35 ]
        }

        for hexa in g_boardHexes:
            if hexa in respAdjHex:
                self.assertEqual(BoardHex(hexa).GetAdjacentHexes(), respAdjHex[hexa], "problem in " + str(hex(hexa)))

    def testHexAdjNodes(self):

        respAdjNodes = {

            0x17: [0x18, 0x07, 0x29, 0x16, 0x38, 0x27],
            0x39: [0x3a, 0x29, 0x4b, 0x38, 0x5a, 0x49],
            0x5b: [0x5c, 0x4b, 0x6d, 0x5a, 0x7c, 0x6b],
            0x7d: [0x7e, 0x6d, 0x8f, 0x7c, 0x9e, 0x8d],
            0x15: [0x16, 0x05, 0x27, 0x14, 0x36, 0x25]
        }

        for hexa in g_boardHexes:
            if hexa in respAdjNodes:
                self.assertEqual(BoardHex(hexa).GetAdjacentNodes(), respAdjNodes[hexa], "problem in " + str(hex(hexa)))

    def testHexAdjEdge(self):

        respAdjEdges = {

            0x17: [0x07, 0x18, 0x06, 0x28, 0x16, 0x27]
        }

        for hexa in g_boardHexes:
            if hexa in respAdjEdges:
                self.assertEqual(BoardHex(hexa).GetAdjacentEdges(), respAdjEdges[hexa], "problem in " + str(hex(hexa)))

    def testNodeAdjHex(self):

        respAdjHexes = {

            0x18: [None, None, 0x17],
            0x38: [0x17, 0x39, 0x37],
            0xd8: [0xb7, 0xd9, 0xd7],
            0xe7: [0xd7, None, None]
        }

        for node in g_boardNodes:
            if node in respAdjHexes:
                self.assertEqual(BoardNode(node).GetAdjacentHexes(), respAdjHexes[node], "problem in " + str(hex(node)))

    def testNodeAdjNode(self):

        respAdjNode = {

            0x18: [None, 0x07, 0x29],
            0x38: [0x29, 0x27, 0x49],
            0xd8: [0xc9, 0xc7, 0xe9],
            0xe7: [0xd6, 0xf8, None]
        }

        for node in g_boardNodes:
            if node in respAdjNode:
                self.assertEqual(BoardNode(node).GetAdjacentNodes(), respAdjNode[node], "problem in " + str(hex(node)))

    def testNodeAdjEdge(self):

        respAdjEdges = {

            0x18: [None, 0x07, 0x18],
            0x38: [0x28, 0x27, 0x38],
            0xd8: [0xc8, 0xc7, 0xd8],
            0xe7: [0xd6, 0xe7, None]
        }

        for node in g_boardNodes:
            if node in respAdjEdges:
                self.assertEqual(BoardNode(node).GetAdjacentEdges(), respAdjEdges[node], "problem in " + str(hex(node)))

    def testEdgeAdjHex(self):

        respAdjHexes = {

            0x07: [None, 0x17],
            0x88: [0x77, 0x99],
            0xd8: [0xd9, 0xd7]
        }

        for edge in g_boardEdges:
            if edge in respAdjHexes:
                self.assertEqual(BoardEdge(edge).GetAdjacentHexes(), respAdjHexes[edge], "problem in " + str(hex(edge)))

    def testEdgeAdjNode(self):

        respAdjNode = {

            0x07: [0x18, 0x07],
            0x88: [0x89, 0x98],
            0xd8: [0xd8, 0xe9]
        }

        for edge in g_boardEdges:
            if edge in respAdjNode:
                self.assertEqual(BoardEdge(edge).GetAdjacentNodes(), respAdjNode[edge], "problem in " + str(hex(edge)))

    def testEdgeAdjEdge(self):

        respAdjEdges = {

            0x07: [None, None, 0x18, 0x06],
            0x88: [0x78, 0x89, 0x87, 0x98],
            0xd8: [0xc8, 0xc7, 0xe9, 0xe8]
        }

        for edge in g_boardEdges:
            if edge in respAdjEdges:
                self.assertEqual(BoardEdge(edge).GetAdjacentEdges(), respAdjEdges[edge], "problem in " + str(hex(edge)))