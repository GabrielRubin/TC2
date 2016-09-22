from JSettlersMessages import *
from CatanBoard import *

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
    'PlaceRobber',
    'EndTurn',
    'DiscardResources',
    'ChoosePlayerToStealFrom',
    'TradeOffer',
    'BankTradeOffer'
]

g_OfferType = [

    'Request',
    'Accept',
    'Decline'
]

class Action(object):

    def __init__(self):
        pass

    def GetMessage(self, gameName, currGameStateName = None):
        pass

class BuildAction(Action):

    def __init__(self, playerNumber, position, index, pieceId):

        self.playerNumber = playerNumber
        self.position     = position
        self.index        = index
        self.pieceId      = pieceId

    def GetMessage(self, gameName, currGameStateName = None):

        putPieceStates = ["START1A", "START1B", "START2A", "START2B",
                          "PLACING_ROAD", "PLACING_SETTLEMENT", "PLACING_CITY",
                          "PLACING_FREE_ROAD1", "PLACING_FREE_ROAD2"]

        if currGameStateName is not None and \
            currGameStateName in putPieceStates:

            return PutPieceMessage(gameName, self.playerNumber, self.pieceId, self.position)

        return BuildRequestMessage(gameName, self.pieceId)


class BuildRoadAction(BuildAction):

    type = 'BuildRoad'
    cost = [ 1,  # brick
             0,  # ore
             0,  # wool
             0,  # grain
             1,  # lumber
             0 ] # unknown

    pieceId = 0

    def __init__(self, playerNumber, position, index):

        super(BuildRoadAction, self).__init__(playerNumber, position, index, BuildRoadAction.pieceId)

class BuildSettlementAction(BuildAction):

    type = 'BuildSettlement'
    cost = [ 1,  # brick
             0,  # ore
             1,  # wool
             1,  # grain
             1,  # lumber
             0 ] # unknown

    pieceId = 1

    def __init__(self, playerNumber, position, index):
        super(BuildSettlementAction, self).__init__(playerNumber, position, index, BuildSettlementAction.pieceId)

class BuildCityAction(BuildAction):

    type = 'BuildCity'
    cost = [ 0,  # brick
             3,  # ore
             0,  # wool
             2,  # grain
             0,  # lumber
             0 ] # unknown

    pieceId = 2

    def __init__(self, playerNumber, position, index):
        super(BuildCityAction, self).__init__(playerNumber, position, index, BuildCityAction.pieceId)

class RollDicesAction(Action):

    type = 'RollDices'

    def __init__(self, playerNumber):

        self.playerNumber = playerNumber

    def GetMessage(self, gameName, currGameStateName = None):

        return RollDiceMessage(gameName)

class BuyDevelopmentCardAction(Action):

    type = 'BuyDevelopmentCard'
    cost = [ 0,  # brick
             1,  # ore
             1,  # wool
             1,  # grain
             0,  # lumber
             0 ] # unknown

    def __init__(self, playerNumber):

        self.playerName = playerNumber

    def GetMessage(self, gameName, currGameStateName = None):

        return BuyCardRequestMessage(gameName)

class UseKnightsCardAction(Action):

    type = 'UseKnightsCard'

    def __init__(self, playerNumber, newRobberPos, targetPlayerIndex):

        self.playerNumber      = playerNumber
        self.robberPos         = newRobberPos
        self.targetPlayerIndex = targetPlayerIndex

    def GetMessage(self, gameName, currGameStateName = None):

        return PlayDevCardRequestMessage(gameName, KNIGHT_CARD_INDEX)

class UseMonopolyCardAction(Action):

    type = 'UseMonopolyCard'

    def __init__(self, playerNumber, resource):

        self.playerNumber = playerNumber
        self.resource     = resource

class UseYearOfPlentyCardAction(Action):

    type = 'UseYearOfPlentyCard'

    def __init__(self, playerNumber, resources):

        self.playerNumber = playerNumber
        self.resources    = resources

class UseFreeRoadsCardAction(Action):

    type = 'UseFreeRoadsCard'

    def __init__(self, playerNumber, road1Edge, road2Edge):

        self.playerNumber = playerNumber
        self.road1Edge    = road1Edge
        self.road2Edge    = road2Edge

    def GetMessage(self, gameName, currGameStateName = None):

        return PlayDevCardRequestMessage(gameName, ROAD_BUILDING_CARD_INDEX)

class PlaceRobberAction(Action):

    type = 'PlaceRobber'

    def __init__(self, playerNumber, newRobberPos):

        self.playerNumber = playerNumber
        self.robberPos    = newRobberPos

    def GetMessage(self, gameName, currGameStateName = None):

        return MoveRobberMessage(gameName, self.playerNumber, self.robberPos)

class EndTurnAction(Action):

    type = 'EndTurn'

    def __init__(self, playerNumber):

        self.playerNumber = playerNumber

    def GetMessage(self, gameName, currGameStateName = None):

        return EndTurnMessage(gameName)

class DiscardResourcesAction(Action):

    type = 'DiscardResources'

    def __init__(self, playerNumber, resources):

        self.playerNumber = playerNumber
        self.resources    = resources

    def GetMessage(self, gameName, currGameStateName = None):

        return DiscardMessage(gameName, self.resources[0], self.resources[1],
                                        self.resources[2], self.resources[3],
                                        self.resources[4], self.resources[5])

class ChoosePlayerToStealFromAction(Action):

    type = 'ChoosePlayerToStealFrom'

    def __init__(self, playerNumer, targetPlayerNumber):

        self.playerNumber       = playerNumer
        self.targetPlayerNumber = targetPlayerNumber

class TradeOfferAction(Action):

    type = 'TradeOffer'

    def __init__(self, offerType, playerNumber, targetPlayerNumber, offerResources, wantedResources):

        self.offerType          = offerType
        self.playerNumber       = playerNumber
        self.targetPlayerNumber = targetPlayerNumber
        self.offerResources     = offerResources
        self.wantedResources    = wantedResources

class BankTradeOfferAction(Action):

    type = 'BankTradeOffer'

    def __init__(self, playerNumber, giveResources, getResources):

        self.playerNumber  = playerNumber
        self.giveResources = giveResources
        self.getResources  = getResources

    def GetMessage(self, gameName, currGameStateName = None):

        return BankTradeMessage(gameName, self.giveResources, self.getResources)