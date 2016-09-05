g_ActionType = \
[
    'BuildRoad',
    'BuildSettlement',
    'BuildCity',
    'RollDices',
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

    pieceId = 0

    def __init__(self, playerNumber, position, index):

        self.playerNumber = playerNumber
        self.position     = position
        self.index        = index

class BuildSettlementAction(Action):

    type = 'BuildSettlement'
    cost = [ 1,  # brick
             0,  # ore
             1,  # wool
             1,  # grain
             1 ] # lumber

    pieceId = 1

    def __init__(self, playerNumber, position, index):

        self.playerNumber = playerNumber
        self.position     = position
        self.index        = index

class BuildCityAction(Action):

    type = 'BuildCity'
    cost = [ 0,  # brick
             3,  # ore
             0,  # wool
             2,  # grain
             0 ] # lumber

    pieceId = 2

    def __init__(self, playerNumber, position, index):

        self.playerNumber = playerNumber
        self.position     = position
        self.index        = index

class RollDicesAction(Action):

    type = 'RollDices'

    def __init__(self, playerNumber):

        self.playerNumber = playerNumber

class BuyDevelopmentCardAction(Action):

    type = 'BuyDevelopmentCard'
    cost = [ 0,  # brick
             1,  # ore
             1,  # wool
             1,  # grain
             0 ] # lumber

    def __init__(self, playerNumber):

        self.playerName = playerNumber

class UseKnightsCardAction(Action):

    type = 'UseKnightsCard'

    def __init__(self, playerNumber, newRobberPos, targetPlayerIndex):

        self.playerNumber      = playerNumber
        self.robberPos         = newRobberPos
        self.targetPlayerIndex = targetPlayerIndex

class UseMonopolyCardAction(Action):

    type = 'UseMonopolyCard'

    def __init__(self, playerNumber, resource):

        self.playerNumber = playerNumber
        self.resource     = resource

class UseYearOfPlentyCardAction(Action):

    type = 'UseYearOfPlentyCard'

    def __init__(self, playerNumber, resource1, resource2):

        self.playerNumber = playerNumber
        self.resource1    = resource1
        self.resource2    = resource2

class UseFreeRoadsCardAction(Action):

    type = 'UseFreeRoadsCard'

    def __init__(self, playerNumber, road1Edge, road2Edge):

        self.playerNumber = playerNumber
        self.road1Edge    = road1Edge
        self.road2Edge    = road2Edge

class PlaceRobberAction(Action):

    type = 'PlaceRobber'

    def __init__(self, playerNumber, newRobberPos):

        self.playerNumber = playerNumber
        self.robberPos    = newRobberPos

class EndTurnAction(Action):

    type = 'EndTurn'

    def __init__(self, playerNumber):

        self.playerNumber = playerNumber