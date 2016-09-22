g_boardHexes = \
                    [0x17, 0x39, 0x5b, 0x7d,

                 0x15, 0x37, 0x59, 0x7b, 0x9d,

              0x13, 0x35, 0x57, 0x79, 0x9b, 0xbd,

           0x11, 0x33, 0x55, 0x77, 0x99, 0xbb, 0xdd,

              0x31, 0x53, 0x75, 0x97, 0xb9, 0xdb,

                 0x51, 0x73, 0x95, 0xb7, 0xd9,

                    0x71, 0x93, 0xb5, 0xd7]

g_boardNodes = \
                [0x18,   0x3a,   0x5c,   0x7e,
             0x07,   0x29,   0x4b,   0x6d,   0x8f,

             0x16,   0x38,   0x5a,   0x7c,   0x9e,
         0x05,   0x27,   0x49,   0x6b,   0x8d,   0xaf,

         0x14,   0x36,   0x58,   0x7a,   0x9c,   0xbe,
     0x03,   0x25,   0x47,   0x69,   0x8b,   0xad,   0xcf,

     0x12,   0x34,   0x56,   0x78,   0x9a,   0xbc,   0xde,
 0x01,   0x23,   0x45,   0x67,   0x89,   0xab,   0xcd,   0xef,

 0x10,   0x32,   0x54,   0x76,   0x98,   0xba,   0xdc,   0xfe,
     0x21,   0x43,   0x65,   0x87,   0xa9,   0xcb,   0xed,

     0x30,   0x52,   0x74,   0x96,   0xb8,   0xda,   0xfc,
         0x41,   0x63,   0x85,   0xa7,   0xc9,   0xeb,

         0x50,   0x72,   0x94,   0xb6,   0xd8,   0xfa,
             0x61,   0x83,   0xa5,   0xc7,   0xe9,

             0x70,   0x92,   0xb4,   0xd6,   0xf8,
                 0x81,   0xa3,   0xc5,   0xe7]

g_boardEdges = \
                          [0x07,  0x18,  0x29,  0x3a,  0x4b,  0x5c,  0x6d,  0x7e,

                       0x06,         0x28,         0x4a,         0x6c,          0x8e,

                    0x05,  0x16,  0x27,  0x38,  0x49,  0x5a,  0x6b,  0x7c,  0x8d,  0x9e,

                0x04,          0x26,         0x48,         0x6a,         0x8c,        0xae,

             0x03,  0x14,  0x25,  0x36,  0x47,  0x58,  0x69,  0x7a,  0x8b,  0x9c,  0xad,  0xbe,

          0x02,        0x024,        0x46,          0x68,         0x8a,          0xac,        0xce,

      0x01,  0x12,  0x23,  0x34,  0x45,  0x56,  0x67,  0x78,  0x89,  0x9a,  0xab,  0xbc,  0xcd,  0xde,

   0x00,         0x22,         0x44,         0x66,         0x88,         0xaa,        0xcc,         0xee,

      0x10,  0x21,  0x32,  0x43,  0x54,  0x65,  0x76,  0x87,  0x98,  0xa9,  0xba,  0xcb,  0xdc,  0xed,

          0x20,        0x42,          0x64,         0x86,         0xa8,         0xca,        0xec,

             0x30,  0x41,  0x52,  0x63,  0x74,  0x85,  0x96,  0xa7,  0xb8,  0xc9,  0xda,  0xeb,

                 0x40,         0x62,         0x84,         0xa6,         0xc8,        0xea,

                    0x50,  0x61,  0x72,  0x83,  0x94,  0xa5,  0xb6,  0xc7,  0xd8,  0xe9,

                        0x60,         0x82,         0xa4,         0xc6,         0xe8,

                           0x70,  0x81,  0x92,  0xa3,  0xb4,  0xc5,  0xd6,  0xe7]

g_constructionTypes = [
    ('ROAD'      , 0),
    ('SETTLEMENT', 1),
    ('CITY'      , 2)
]

g_portType = [
    'BrickHarbor',
    'OreHarbor',
    'WoolHarbor',
    'GrainHarbor',
    'LumberHarbor',
    '3for1'
]

g_terrains = [
    ('DESERT'   , None    ),
    ('HILLS'    , 'BRICK' ),
    ('MOUNTAINS', 'ORE'   ),
    ('PASTURE'  , 'WOOL'  ),
    ('FIELDS'   , 'GRAIN' ),
    ('FOREST'   , 'LUMBER'),
    ('SEA'      , None    )
]

g_resources = [
    'BRICK',
    'ORE',
    'WOOL',
    'GRAIN',
    'LUMBER',
    'UNKNOWN'
]

g_developmentCards = [
    'KNIGHT',
    'ROAD_BUILDING',
    'YEAR_OF_PLENTY',
    'MONOPOLY',
    'VICTORY_POINT'
]

KNIGHT_CARD_INDEX         = 0
ROAD_BUILDING_CARD_INDEX  = 1
YEAR_OF_PLENTY_CARD_INDEX = 2
MONOPOLY_CARD_INDEX       = 3
VICTORY_POINT_CARD_INDEX  = 4

g_pieces = [
    'ROADS',
    'SETTLEMENTS',
    'CITIES'
]

class BoardHex:

    def __init__(self, index):

        self.index      = index
        self.terrain    = None
        self.production = None
        self.number     = 0

    def SetTerrain(self, terrainId):

        # If the id is too big, is probably a port:
        #  so the hex is SEA (the last one [-1])
        if terrainId >= len(g_terrains):
            self.terrain    = g_terrains[-1][0]
            self.production = g_terrains[-1][1]

        else:
            self.terrain    = g_terrains[terrainId][0]
            self.production = g_terrains[terrainId][1]

    def GetAdjacentHexes(self):

        adjacentHexes = [ -0x20,  0x02,

                        -0x22,       0x22,

                          -0x02,  0x20]

        return [ self.index + h if self.index + h in g_boardHexes else None
                 for h in adjacentHexes ]

    def GetAdjacentNodes(self):

        adjacentNodes = [ 0x01,
                   -0x10,       0x12,

                   -0x01,       0x21,
                          0x10 ]
        return [ self.index + node for node in adjacentNodes]

    def GetAdjacentEdges(self):

        adjacentEdges = [ -0x10,  0x01,

                        -0x11,      0x11,

                          -0x01,  0x10 ]
        return [ self.index + edge for edge in adjacentEdges]

class BoardNode:

    def __init__(self, index):

        self.index        = index
        self.construction = None
        self.portType     = None

    def GetAdjacentHexes(self):

        if self.index & 1: # \ /
                           #  |
            adjacentHexes =    [ -0x10,

                              -0x11, 0x10]

        else:              #  |
                           # / \
            adjacentHexes = [ -0x21,  0x01,

                                 -0x01]
        return [ self.index + h if self.index + h in g_boardHexes else None
                 for h in adjacentHexes ]

    def GetAdjacentNodes(self):

        if self.index & 1: # \ /
                           #  |

            adjacentNodes = [ -0x11, 0x11,

                                  0x0f]

        else:              #  |
                           # / \

            adjacentNodes =    [ -0x0f,

                             -0x11,  0x11]
        return [ self.index + node if self.index + node in g_boardNodes else None
                 for node in adjacentNodes ]

    def GetAdjacentEdges(self):

        if self.index & 1: # \ /
                           #  |

            adjacentEdges = [ -0x11,  0x00,

                                 -0x01]

        else:              #  |
                           # / \

            adjacentEdges =    [ -0x10,

                             -0x11,  0x00]

        return [ self.index + edge if self.index + edge in g_boardEdges else None
                 for edge in adjacentEdges ]

    def GetPossibleResources(self):

        return [hex.production for hex in self.GetAdjacentHexes()]

class BoardEdge:

    def __init__(self, index):

        self.index        = index;
        self.construction = None;

    def GetAdjacentHexes(self):

        if self.index >= 16:
            i0 = int(hex(self.index)[2], 16) & 1
            i1 = int(hex(self.index)[3], 16) & 1
        else:
            i0 = False
            i1 = int(hex(self.index)[2], 16)

        if not i0 and not i1: # |
            adjacentHexes = [-0x11, 0x11]

        elif not i0 and i1:   # /
            adjacentHexes = [-0x10,
                                    0x10]

        elif i0 and not i1:   # \
            adjacentHexes = [       0x01,
                             -0x01       ]

        return [ self.index + h if self.index + h in g_boardHexes else None
                 for h in adjacentHexes]

    def GetAdjacentNodes(self):

        if self.index >= 16:
            i0 = int(hex(self.index)[2], 16) & 1
            i1 = int(hex(self.index)[3], 16) & 1
        else:
            i0 = False
            i1 = int(hex(self.index)[2], 16)

        if not i0 and not i1: # |
            adjacentNodes = [ 0x01,
                              0x10]

        elif not i0 and i1:   # /
            adjacentNodes = [       0x11,
                             0x00       ]

        elif i0 and not i1:   # \
            adjacentNodes = [0x00,
                                    0x11]

        return [ self.index + node if self.index + node in g_boardNodes else None
                 for node in adjacentNodes]

    def GetAdjacentEdges(self):

        if self.index >= 16:
            i0 = int(hex(self.index)[2], 16) & 1
            i1 = int(hex(self.index)[3], 16) & 1
        else:
            i0 = False
            i1 = int(hex(self.index)[2], 16)

        if not i0 and not i1: # |
            adjacentEdges = [-0x10, 0x01,

                             -0x01, 0x10]

        elif not i0 and i1:   # /
            adjacentEdges = [       0x01,
                            -0x11,
                                    0x11,
                            -0x01       ]

        elif i0 and not i1:   # \
            adjacentEdges = [      -0x10,
                            -0x11,
                                    0x11,
                             0x10]

        return [ self.index + edge if self.index + edge in g_boardEdges else None
                 for edge in adjacentEdges]

class Construction:

    def __init__(self, constructionType, owner, index, position):

        self.type          = constructionType[0]
        self.victoryPoints = constructionType[1]
        self.owner         = owner
        self.index         = index
        self.position      = position