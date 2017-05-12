from JSettlersMessages import *
from CatanBoard import *

from CatanUtils import listm

import random

freeBuildStates = ["START1A", "START1B", "START2A", "START2B",
                   "PLACING_ROAD", "PLACING_SETTLEMENT", "PLACING_CITY",
                   "PLACING_FREE_ROAD1", "PLACING_FREE_ROAD2"]

putPieceStates = ["START1A", "START1B", "START2A", "START2B",
                  "PLACING_ROAD", "PLACING_SETTLEMENT", "PLACING_CITY",
                  "PLACING_FREE_ROAD1", "PLACING_FREE_ROAD2"]

class Action(object):

    def __init__(self):
        pass

    def GetMessage(self, gameName, currGameStateName = None):
        pass

    def ApplyAction(self, gameState):
        pass

    def __eq__(self, other):
        if other is None:
            if self is None:
                return True
            return False
        return self.__dict__ == other.__dict__

class BuildAction(Action):

    def __init__(self, playerNumber, position, index, pieceId, cost):

        self.playerNumber = playerNumber
        self.position     = position
        self.index        = index
        self.pieceId      = pieceId
        self.cost         = cost

    def GetMessage(self, gameName, currGameStateName = None):

        if currGameStateName is not None and \
            currGameStateName in putPieceStates:

            return PutPieceMessage(gameName, self.playerNumber, self.pieceId, self.position)

        return BuildRequestMessage(gameName, self.pieceId)


    def ApplyAction(self, gameState):

        #logging.debug("APPLYING ACTION! \n TYPE = BuildAction")

        gameState.players[self.playerNumber].Build(gameState, g_constructionTypes[self.pieceId][0], self.position)

        if gameState.currState not in freeBuildStates:

            gameState.players[self.playerNumber].resources -= self.cost

    def __str__(self):

        return "Build {0} Action:  \n" \
               "    player   = {1} \n" \
               "    position = {2} \n" \
               "    index    = {3}".format(
            g_constructionTypes[self.pieceId][0],
            self.playerNumber,
            hex(self.position),
            self.index
        )

class BuildRoadAction(BuildAction):

    type = 'BuildRoad'
    cost = listm([ 1,  # brick
                   0,  # ore
                   0,  # wool
                   0,  # grain
                   1,  # lumber
                   0 ]) # unknown

    pieceId = 0

    def __init__(self, playerNumber, position, index):
        super(BuildRoadAction, self).__init__(playerNumber, position, index,
                                              BuildRoadAction.pieceId, BuildRoadAction.cost)

    def ApplyAction(self, gameState):

        super(BuildRoadAction, self).ApplyAction(gameState)

        if gameState.checkLongestRoad:
            gameState.UpdateLongestRoad()

        if gameState.currState == "START1B":

            gameState.players[gameState.currPlayer].firstRoadBuild = True

            nextPlayer = (gameState.currPlayer + 1) % len(gameState.players)

            if nextPlayer == gameState.startingPlayer:
                gameState.currState = "START2A"

            else:
                gameState.currPlayer = nextPlayer
                gameState.currState = "START1A"

        elif gameState.currState == "START2B":

            gameState.players[gameState.currPlayer].secondRoadBuild = True

            if gameState.currPlayer == gameState.startingPlayer:
                gameState.FinishSetup()
                gameState.currState = "PLAY"
            else:
                nextPlayer = (gameState.currPlayer - 1) % len(gameState.players)
                gameState.currPlayer = nextPlayer
                gameState.currState = "START2A"

        elif gameState.currState == "PLACING_FREE_ROAD1":
            gameState.currState = "PLACING_FREE_ROAD2"

        elif gameState.currState == "PLACING_FREE_ROAD2":
            gameState.currState = "PLAY1"


class BuildSettlementAction(BuildAction):

    type = 'BuildSettlement'
    cost = listm([ 1,  # brick
                   0,  # ore
                   1,  # wool
                   1,  # grain
                   1,  # lumber
                   0 ]) # unknown

    pieceId = 1

    def __init__(self, playerNumber, position, index):
        super(BuildSettlementAction, self).__init__(playerNumber, position, index,
                                                    BuildSettlementAction.pieceId, BuildSettlementAction.cost)

    def ApplyAction(self, gameState):

        super(BuildSettlementAction, self).ApplyAction(gameState)

        #if gameState.boardNodes[self.position].portType is not None:
        #    gameState.players[self.playerNumber].UpdateTradeRates(gameState)

        if gameState.checkLongestRoad:

            for edge in gameState.boardNodes[self.position].adjacentEdges:
                checkLongestRoad = False
                if gameState.boardEdges[edge].construction is not None and \
                   gameState.boardEdges[edge].construction.owner != self.playerNumber:
                    checkLongestRoad = True
                    break

            if checkLongestRoad:
                gameState.UpdateLongestRoad()

        if gameState.currState == "START1A":

            gameState.players[gameState.currPlayer].firstSettlementBuild = True

            gameState.currState = "START1B"

        elif gameState.currState == "START2A":

            gameState.players[gameState.currPlayer].secondSettlementBuild = True

            gameState.players[self.playerNumber].GetStartingResources(gameState)

            gameState.currState = "START2B"


class BuildCityAction(BuildAction):

    type = 'BuildCity'
    cost = listm([ 0,  # brick
                   3,  # ore
                   0,  # wool
                   2,  # grain
                   0,  # lumber
                   0 ]) # unknown

    pieceId = 2

    def __init__(self, playerNumber, position, index):
        super(BuildCityAction, self).__init__(playerNumber, position, index,
                                              BuildCityAction.pieceId, BuildCityAction.cost)

    '''
    def ApplyAction(self, gameState):

        super(BuildCityAction, self).ApplyAction(gameState)
    '''

class RollDicesAction(Action):

    type = 'RollDices'

    def __init__(self, playerNumber = None, result = None):

        self.playerNumber = playerNumber

        if result is not None:
            self.result = result
        else:
            self.result = 2 + int(random.random() * 6) + int(random.random() * 6)

    def GetMessage(self, gameName, currGameStateName = None):

        return RollDiceMessage(gameName)

    def ApplyAction(self, gameState):

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(RollDicesAction.type))

        gameState.players[self.playerNumber].rolledTheDices = True
        gameState.dicesAreRolled = True

        if self.result == 7:

            discardRound = False

            for index in xrange(0, len(gameState.players)):

                if sum(gameState.players[index].resources) > 7:
                    discardRound = True

            if discardRound:

                gameState.currState = "WAITING_FOR_DISCARDS"

                gameState.currPlayerChoice = 0

            else:

                gameState.currState = "PLACING_ROBBER"

        else:
            for player in gameState.players:
                player.UpdatePlayerResources(gameState, self.result)

            gameState.currState = "PLAY1"

class BuyDevelopmentCardAction(Action):

    type = 'BuyDevelopmentCard'
    cost = listm([ 0,  # brick
                   1,  # ore
                   1,  # wool
                   1,  # grain
                   0,  # lumber
                   0 ]) # unknown

    def __init__(self, playerNumber):

        self.playerNumber = playerNumber

    def GetMessage(self, gameName, currGameStateName = None):

        return BuyCardRequestMessage(gameName)

    def ApplyAction(self, gameState):

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(BuyDevelopmentCardAction.type))

        gameState.players[self.playerNumber].resources -= BuyDevelopmentCardAction.cost

        gameState.DrawDevCard(self.playerNumber)

class UseDevelopmentCardAction(Action):

    def __init__(self, playerNumber, index):

        self.playerNumber = playerNumber

        self.index        = index

    def ApplyAction(self, gameState):

        gameState.players[self.playerNumber].developmentCards[self.index] -= 1

        gameState.players[self.playerNumber].mayPlayDevCards[self.index] = False

        gameState.players[self.playerNumber].playedDevCard = True

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

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(UseKnightsCardAction.type))

        super(UseKnightsCardAction, self).ApplyAction(gameState)

        gameState.currState = "PLACING_ROBBER"

        gameState.players[self.playerNumber].knights += 1

        gameState.UpdateLargestArmy()

class UseMonopolyCardAction(UseDevelopmentCardAction):

    type = 'UseMonopolyCard'

    def __init__(self, playerNumber, resource):

        super(UseMonopolyCardAction, self).__init__(playerNumber, MONOPOLY_CARD_INDEX)

        self.resource     = resource

    def GetMessage(self, gameName, currGameStateName = None):

        return [ PlayDevCardRequestMessage(gameName, self.index),
                 MonopolyPickMessage(gameName, self.resource)   ]

    def ApplyAction(self, gameState):

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(UseMonopolyCardAction.type))

        super(UseMonopolyCardAction, self).ApplyAction(gameState)

        total = 0

        for index in xrange(0, len(gameState.players)):

            if index == self.playerNumber:
                continue

            amount = gameState.players[index].resources[self.resource]

            gameState.players[index].resources[self.resource] = 0

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

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(UseYearOfPlentyCardAction.type))

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

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(UseFreeRoadsCardAction.type))

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

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(PlaceRobberAction.type))

        pastRobberPos = gameState.robberPos

        gameState.players[self.playerNumber].PlaceRobber(gameState, self.robberPos)

        gameState.UpdateRobDiceProduction(gameState, pastRobberPos=pastRobberPos, newRobberPos=gameState.robberPos)

        possiblePlayers = gameState.GetPossiblePlayersToSteal(self.playerNumber)

        if len(possiblePlayers) > 1:
            gameState.currState = "WAITING_FOR_CHOICE"
        else:
            if len(possiblePlayers) == 1:
                ChoosePlayerToStealFromAction(self.playerNumber, possiblePlayers[0]).ApplyAction(gameState)
            else:
                if gameState.dicesAreRolled:
                    gameState.currState = "PLAY1"
                else:
                    gameState.currState = "PLAY"

class EndTurnAction(Action):

    type = 'EndTurn'

    def __init__(self, playerNumber):

        self.playerNumber = playerNumber

    def GetMessage(self, gameName, currGameStateName = None):

        return EndTurnMessage(gameName)

    def ApplyAction(self, gameState):

        gameState.dicesAreRolled = False
        gameState.players[self.playerNumber].rolledTheDices = False
        gameState.players[self.playerNumber].placedRobber   = False
        gameState.currTurn += 1

        playerPoints = gameState.players[self.playerNumber].GetVictoryPoints()

        if playerPoints >= 8 and not gameState.checkLongestRoad:
            gameState.UpdateLongestRoad()
            gameState.checkLongestRoad = True

        if playerPoints >= 10:
            gameState.currState = "OVER"
            gameState.winner    = self.playerNumber

        else:
            gameState.currState = "PLAY"

            gameState.currPlayer = (gameState.currPlayer + 1) % len(gameState.players)

            gameState.players[gameState.currPlayer].UpdateMayPlayDevCards(canUseAll=True)
            gameState.players[gameState.currPlayer].playedDevCard = False

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

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(DiscardResourcesAction.type))

        gameState.players[self.playerNumber].resources -= self.resources

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

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(ChoosePlayerToStealFromAction.type))

        targetPlayer = gameState.players[self.targetPlayerNumber]

        resourcesPopulation = [0 for i in range(0, targetPlayer.resources[0])] + \
                              [1 for j in range(0, targetPlayer.resources[1])] + \
                              [2 for k in range(0, targetPlayer.resources[2])] + \
                              [3 for l in range(0, targetPlayer.resources[3])] + \
                              [4 for m in range(0, targetPlayer.resources[4])] + \
                              [5 for n in range(0, targetPlayer.resources[5])]

        if len(resourcesPopulation) > 0:

            stolenResource = random.choice(resourcesPopulation)

            gameState.players[self.playerNumber].resources[stolenResource] += 1

            gameState.players[self.targetPlayerNumber].resources[stolenResource] -= 1

        if gameState.dicesAreRolled:
            gameState.currState = "PLAY1"
        else:
            gameState.currState = "PLAY"

class MakeTradeOfferAction(Action):

    type = 'MakeTradeOffer'

    def __init__(self, fromPlayerNumber, toPlayers, giveResources, getResources):

        self.fromPlayerNumber = fromPlayerNumber

        self.toPlayers                   = toPlayers
        self.toPlayers[fromPlayerNumber] = False #Asser the player cannot offer to himself!

        self.toPlayerNumbers = []
        for i in range(0, len(self.toPlayers)):
            if self.toPlayers[i]:
                self.toPlayerNumbers.append(i)

        self.giveResources     = giveResources
        self.getResources      = getResources
        self.previousGameState = None

    def GetMessage(self, gameName, currGameStateName = None):

        return MakeOfferMessage(gameName, self.fromPlayerNumber, self.toPlayers, self.giveResources, self.getResources)

    def ApplyAction(self, gameState):

        self.previousGameState = gameState.currState
        gameState.currState    = 'WAITING_FOR_TRADE'
        gameState.currPlayer   = self.toPlayerNumbers[int(random.random() * len(self.toPlayerNumbers))]
        self.toPlayerNumbers.remove(gameState.currPlayer)
        gameState.currTradeOffer = self


class RejectTradeOfferAction(Action):

    type = 'RejectTradeOffer'

    def __init__(self, playerNumber):

        self.playerNumber = playerNumber

    def GetMessage(self, gameName, currGameStateName = None):

        return RejectOfferMessage(gameName, self.playerNumber)

    def ApplyAction(self, gameState):

        if len(gameState.currTradeOffer.toPlayerNumbers) <= 0:
            gameState.currState      = gameState.currTradeOffer.previousGameState
            gameState.currPlayer     = gameState.currTradeOffer.fromPlayerNumber
            gameState.currTradeOffer = None
        else:
            currPlayerIndex = int(random.random() * len(gameState.currTradeOffer.toPlayerNumbers))
            gameState.currPlayer = gameState.currTradeOffer.toPlayerNumbers[currPlayerIndex]
            gameState.currTradeOffer.toPlayerNumbers.remove(gameState.currPlayer)

class AcceptTradeOfferAction(Action):

    type = 'AcceptTradeOffer'

    def __init__(self, playerNumber, offerPlayerNumber):

        self.playerNumber      = playerNumber
        self.offerPlayerNumber = offerPlayerNumber

    def GetMessage(self, gameName, currGameStateName = None):

        return AcceptOfferMessage(gameName, self.playerNumber, self.offerPlayerNumber)

    def ApplyAction(self, gameState):

        gameState.currState  = gameState.currTradeOffer.previousGameState
        gameState.currPlayer = gameState.currTradeOffer.fromPlayerNumber

        give = gameState.currTradeOffer.giveResources + [0]
        get  = gameState.currTradeOffer.getResources  + [0]

        gameState.players[self.offerPlayerNumber].resources -= listm(give)
        gameState.players[self.playerNumber].resources      -= listm(get )

        gameState.players[self.offerPlayerNumber].resources += listm(give)
        gameState.players[self.playerNumber].resources      += listm(get )

        gameState.currTradeOffer = None

class BankTradeOfferAction(Action):

    type = 'BankTradeOffer'

    def __init__(self, playerNumber, giveResources, getResources):

        self.playerNumber  = playerNumber
        self.giveResources = giveResources
        self.getResources  = getResources

    def GetMessage(self, gameName, currGameStateName = None):

        return BankTradeMessage(gameName, self.giveResources, self.getResources)

    def ApplyAction(self, gameState):

        #logging.debug("APPLYING ACTION! \n TYPE = {0}".format(BankTradeOfferAction.type))

        # ADD THE 'UNKNOWN' RESOURCE TYPE (not present in trade transaction)
        give = self.giveResources + [0]
        get  = self.getResources  + [0]

        gameState.players[self.playerNumber].resources -= listm(give)
        gameState.players[self.playerNumber].resources += listm(get )

class ChangeGameStateAction(Action):

    type = 'ChangeGameState'

    def __init__(self, newGameState):
        self.gameState = newGameState

    def GetMessage(self, gameName, currGameStateName=None):
        return None

    def ApplyAction(self, gameState):

        gameState.currState = self.gameState