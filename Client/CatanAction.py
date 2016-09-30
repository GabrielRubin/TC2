from JSettlersMessages import *
from CatanBoard import *

import random

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

    def ApplyAction(self, gameState):
        pass

class BuildAction(Action):

    def __init__(self, playerNumber, position, index, pieceId, cost):

        self.playerNumber = playerNumber
        self.position     = position
        self.index        = index
        self.pieceId      = pieceId
        self.cost         = cost

    def GetMessage(self, gameName, currGameStateName = None):

        putPieceStates = ["START1A", "START1B", "START2A", "START2B",
                          "PLACING_ROAD", "PLACING_SETTLEMENT", "PLACING_CITY",
                          "PLACING_FREE_ROAD1", "PLACING_FREE_ROAD2"]

        if currGameStateName is not None and \
            currGameStateName in putPieceStates:

            return PutPieceMessage(gameName, self.playerNumber, self.pieceId, self.position)

        return BuildRequestMessage(gameName, self.pieceId)


    def ApplyAction(self, gameState):

        newConstruction = Construction(g_constructionTypes[self.pieceId],
                                       self.playerNumber, self.index, self.position)

        freeBuildStates = ["START1A", "START1B", "START2A", "START2B",
                           "PLACING_FREE_ROAD1", "PLACING_FREE_ROAD2"]

        if gameState.currState not in freeBuildStates:
            currResources = gameState.players[self.playerNumber].resources

            gameState.players[self.playerNumber].resources = \
                [x1 - x2 for (x1, x2) in zip(currResources, self.cost)]

        if self.pieceId == 0:   # ROADS

            gameState.players[self.playerNumber].roads.append(self.position)

            gameState.boardEdges[self.position].construction = newConstruction

            gameState.players[self.playerNumber].numberOfPieces[0] -= 1

            #TODO -> Check biggest road...
            # gameState.CheckBiggestRoad()

            if gameState.currState == "START1B":

                nextPlayer = (gameState.currPlayer + 1) % len(gameState.players)

                if nextPlayer == gameState.startingPlayer:
                    gameState.currState = "START2A"

                else:
                    gameState.currPlayer = nextPlayer
                    gameState.currState  = "START1A"

            elif gameState.currState == "START2B":

                if gameState.currPlayer == gameState.startingPlayer:

                    gameState.currState  = "PLAY"

                else:

                    nextPlayer = (gameState.currPlayer - 1) % len(gameState.players)

                    gameState.currPlayer = nextPlayer

                    gameState.currState = "START2A"

            elif gameState.currState == "PLACING_FREE_ROAD1":
                gameState.currState = "PLACING_FREE_ROAD2"

            elif gameState.currState == "PLACING_FREE_ROAD2":
                gameState.currState = "PLAY1"

        elif self.pieceId == 1: # SETTLEMENTS

            gameState.players[self.playerNumber].settlements.append(self.position)

            gameState.boardNodes[self.position].construction = newConstruction

            gameState.players[self.playerNumber].numberOfPieces[1] -= 1

            if gameState.currState == "START1A":
                gameState.currState = "START1B"

            elif gameState.currState == "START2A":

                gameState.players[self.playerNumber].GetStartingResources(gameState)

                gameState.currState = "START2B"

        else:                   # CITIES

            gameState.players[self.playerNumber].settlements.remove(self.position)

            gameState.players[self.playerNumber].cities.append(self.position)

            gameState.boardNodes[self.position].construction = newConstruction

            gameState.players[self.playerNumber].numberOfPieces[2] -= 1


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

        super(BuildRoadAction, self).__init__(playerNumber, position, index,
                                              BuildRoadAction.pieceId, BuildRoadAction.cost)

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
        super(BuildSettlementAction, self).__init__(playerNumber, position, index,
                                                    BuildSettlementAction.pieceId, BuildSettlementAction.cost)

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
        super(BuildCityAction, self).__init__(playerNumber, position, index,
                                              BuildCityAction.pieceId, BuildCityAction.cost)

class RollDicesAction(Action):

    type = 'RollDices'

    def __init__(self, playerNumber = None, result = None):

        self.playerNumber = playerNumber

        if result is not None:
            self.result = result
        else:
            self.result = random.randint(1, 6) + random.randint(1, 6)

    def GetMessage(self, gameName, currGameStateName = None):

        return RollDiceMessage(gameName)

    def ApplyAction(self, gameState):

        if self.playerNumber is not None:
            gameState.players[self.playerNumber].rolledTheDices = True

        if self.result == 7:
            gameState.currState        = "WAITING_FOR_DISCARDS"
            gameState.currPlayerChoice = 0

        else:
            for playerIndex in range(0, len(gameState.players)):
                gameState.players[playerIndex].UpdatePlayerResources(gameState, self.result)

            gameState.currState = "PLAY1"

class BuyDevelopmentCardAction(Action):

    type = 'BuyDevelopmentCard'
    cost = [ 0,  # brick
             1,  # ore
             1,  # wool
             1,  # grain
             0,  # lumber
             0 ] # unknown

    def __init__(self, playerNumber, fromServer = False):

        self.playerNumber = playerNumber

        self.fromServer = fromServer

    def GetMessage(self, gameName, currGameStateName = None):

        return BuyCardRequestMessage(gameName)

    def ApplyAction(self, gameState):

        currResources = gameState.players[self.playerNumber].resources

        gameState.players[self.playerNumber].resources = \
            [ x1 - x2 for (x1, x2) in zip(currResources, BuyDevelopmentCardAction.cost) ]

        if not self.fromServer:
            gameState.DrawDevCard(self.playerNumber)

class UseDevelopmentCardAction(Action):

    def __init__(self, playerNumber, index):

        self.playerNumber = playerNumber

        self.index        = index

    def ApplyAction(self, gameState):

        self.gameState.players[self.playerNumber].developmentCards[self.index] -= 1

        self.gameState.players[self.playerNumber].mayPlayDevCards[self.index] = False

        self.gameState.players[self.playerNumber].playedDevCard = True

class UseKnightsCardAction(UseDevelopmentCardAction):

    type = 'UseKnightsCard'

    def __init__(self, playerNumber, newRobberPos, targetPlayerIndex):

        super(UseKnightsCardAction, self).__init__(playerNumber, KNIGHT_CARD_INDEX)

        self.playerNumber      = playerNumber
        self.robberPos         = newRobberPos
        self.targetPlayerIndex = targetPlayerIndex

    def GetMessage(self, gameName, currGameStateName = None):

        return PlayDevCardRequestMessage(gameName, KNIGHT_CARD_INDEX)

    def ApplyAction(self, gameState):

        super(UseKnightsCardAction, self).ApplyAction(gameState)

        self.gameState.currState = "PLACING_ROBBER"

        self.gameState.players[self.playerNumber].knights += 1

class UseMonopolyCardAction(UseDevelopmentCardAction):

    type = 'UseMonopolyCard'

    def __init__(self, playerNumber, resource):

        super(UseMonopolyCardAction, self).__init__(playerNumber, MONOPOLY_CARD_INDEX)

        self.resource     = resource

    def GetMessage(self, gameName, currGameStateName = None):

        return [ PlayDevCardRequestMessage(gameName, self.index),
                 MonopolyPickMessage(gameName, self.resource)            ]

    def ApplyAction(self, gameState):

        super(UseMonopolyCardAction, self).ApplyAction(gameState)

        total = 0

        for index in range(0, len(gameState.players)):

            if index == self.playerNumber:
                continue

            amount = gameState.players[index].resources[self.resource]

            gameState.players[index].resources[self.resource] -= amount

            total += amount

        gameState.players[self.playerNumber].resources[self.resource] += total

class UseYearOfPlentyCardAction(UseDevelopmentCardAction):

    type = 'UseYearOfPlentyCard'

    def __init__(self, playerNumber, resources):

        super(UseYearOfPlentyCardAction, self).__init__(playerNumber, YEAR_OF_PLENTY_CARD_INDEX)

        self.resources    = resources

    def GetMessage(self, gameName, currGameStateName = None):

        return [PlayDevCardRequestMessage(gameName, self.index),
                DiscoveryPickMessage(gameName, self.resources)                ]

    def ApplyAction(self, gameState):

        super(UseYearOfPlentyCardAction, self).ApplyAction(gameState)

        gameState.players[self.playerNumber].resources[self.resources[0]] += 1

        gameState.players[self.playerNumber].resources[self.resources[1]] += 1

class UseFreeRoadsCardAction(UseDevelopmentCardAction):

    type = 'UseFreeRoadsCard'

    def __init__(self, playerNumber, road1Edge, road2Edge):

        super(UseFreeRoadsCardAction, self).__init__(playerNumber, ROAD_BUILDING_CARD_INDEX)

        self.road1Edge    = road1Edge
        self.road2Edge    = road2Edge

    def GetMessage(self, gameName, currGameStateName = None):

        return PlayDevCardRequestMessage(gameName, self.index)

    def ApplyAction(self, gameState):

        super(UseFreeRoadsCardAction, self).ApplyAction(gameState)

        gameState.currState = "PLACING_FREE_ROAD1"

class PlaceRobberAction(Action):

    type = 'PlaceRobber'

    def __init__(self, playerNumber, newRobberPos):

        self.playerNumber = playerNumber
        self.robberPos    = newRobberPos

    def GetMessage(self, gameName, currGameStateName = None):

        return MoveRobberMessage(gameName, self.playerNumber, self.robberPos)

    def ApplyAction(self, gameState):

        gameState.robberPos = self.robberPos

        gameState.currState = "WAITING_FOR_CHOICE"

class EndTurnAction(Action):

    type = 'EndTurn'

    def __init__(self, playerNumber):

        self.playerNumber = playerNumber

    def GetMessage(self, gameName, currGameStateName = None):

        return EndTurnMessage(gameName)

    def ApplyAction(self, gameState):

        gameState.players[self.playerNumber].rolledTheDices = False

        gameState.currPlayer = (gameState.currPlayer + 1) % len(gameState.players)

        gameState.currState = "PLAY"

class DiscardResourcesAction(Action):

    type = 'DiscardResources'

    def __init__(self, playerNumber, resources):

        self.playerNumber = playerNumber
        self.resources    = resources

    def GetMessage(self, gameName, currGameStateName = None):

        return DiscardMessage(gameName, self.resources[0], self.resources[1],
                                        self.resources[2], self.resources[3],
                                        self.resources[4], self.resources[5])

    def ApplyAction(self, gameState):

        currResources = gameState.players[self.playerNumber].resources

        gameState.players[self.playerNumber].resources = \
            [ x1 - x2 for (x1, x2) in zip(currResources, self.resources) ]

        gameState.currPlayerChoice += 1

        if gameState.currPlayerChoice >= len(gameState.players):

            gameState.currPlayerChoice = -1

            gameState.currState = "PLACING_ROBBER"

class ChoosePlayerToStealFromAction(Action):

    type = 'ChoosePlayerToStealFrom'

    def __init__(self, playerNumber, targetPlayerNumber):

        self.playerNumber       = playerNumber
        self.targetPlayerNumber = targetPlayerNumber

    def GetMessage(self, gameName, currGameStateName = None):

        return ChoosePlayerMessage(gameName, self.targetPlayerNumber)

    def ApplyAction(self, gameState):

        targetPlayer = gameState.players[self.targetPlayerNumber]

        resourcesPopulation = [0 for i in range(0, targetPlayer.resources[0])] + \
                              [1 for j in range(0, targetPlayer.resources[1])] + \
                              [2 for k in range(0, targetPlayer.resources[2])] + \
                              [3 for l in range(0, targetPlayer.resources[3])] + \
                              [4 for m in range(0, targetPlayer.resources[4])] + \
                              [5 for n in range(0, targetPlayer.resources[5])]

        if len(resourcesPopulation) > 0:

            stolenResource = random.choice(resourcesPopulation)

            gameState[self.playerNumber].resources[stolenResource] += 1

            gameState[self.targetPlayerNumber].resources[stolenResource] -= 1

        if gameState.players[self.playerNumber].rolledTheDices:
            gameState.currState = "PLAY1"
        else:
            gameState.currState = "PLAY"

class TradeOfferAction(Action):

    type = 'TradeOffer'

    def __init__(self, offerType, playerNumber, targetPlayerNumber, offerResources, wantedResources):

        self.offerType          = offerType
        self.playerNumber       = playerNumber
        self.targetPlayerNumber = targetPlayerNumber
        self.offerResources     = offerResources
        self.wantedResources    = wantedResources

    # TODO -> GetMessage

    # TODO -> ApplyAction

class BankTradeOfferAction(Action):

    type = 'BankTradeOffer'

    def __init__(self, playerNumber, giveResources, getResources):

        self.playerNumber  = playerNumber
        self.giveResources = giveResources
        self.getResources  = getResources

    def GetMessage(self, gameName, currGameStateName = None):

        return BankTradeMessage(gameName, self.giveResources, self.getResources)

    def ApplyAction(self, gameState):

        # ADD THE 'UNKNOWN' RESOURCE TYPE (not present in trade transaction)
        give = self.giveResources + [0]
        get  = self.getResources  + [0]

        gameState.players[self.playerNumber].resources = \
            [x1 - x2 for (x1, x2) in
             zip(gameState.players[self.playerNumber].resources, give)]

        gameState.players[self.playerNumber].resources = \
            [x1 + x2 for (x1, x2) in
             zip(gameState.players[self.playerNumber].resources, get)]