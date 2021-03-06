import sys
import socket
import logging
from JSettlersMessages import *
from CatanPlayer import *
from CatanGame import *
from CatanAction import *
from AgentRandom import *
from AgentAlphabeta import *
import os
import CSVGenerator

m_clientPath = os.getcwd()

class Client:

    def __init__(self, gameName, player, autoStart, showServerMessages, debugSimulator = False):

        self.socket         = None
        self.game           = None

        self.joinedAGame    = False
        self.isSeated       = False
        self.gameStarted    = False

        self.gameName       = gameName
        self.player         = player

        self.debugSimulator = debugSimulator

        if self.debugSimulator:
            self.debugGame  = Game(GameState())

            self.debugGame.AddPlayer(Player("DebugP1", 0), 0)
            self.debugGame.AddPlayer(Player("DebugP2", 1), 1)
            self.debugGame.AddPlayer(Player("DebugP3", 2), 2)
            self.debugGame.AddPlayer(Player("DebugP4", 3), 3)

        self.autoStart      = autoStart
        self.botsInit       = False

        self.serverMessages = showServerMessages

        self.waitBankTradeAck = False

        self.playerBuildAction = None

        self.expectedResourceCount = [0, 0, 0, 0]

        self.waitTradeResult  = False
        self.tradeResultCount = -1

        self.tradeBuffer = []

        self.messagetbl = {}
        for g in globals():
            cg = globals()[g]
            if g.endswith("Message") and hasattr(cg, "id"):
                self.messagetbl[str(cg.id)] = (cg, g)

    def Assert(self, condition, message):

        if not condition:
            logging.critical("ASSERT FAILED! - {0}".format(message))
            return Exception

    # Connection to jsettlers game server
    def ConnectToServer(self, serverAddress):

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket.connect(serverAddress)

            self.socket.settimeout(0)

            self.socket.setblocking(1)

        except socket.error, exc:

            logging.critical("Caught exception socket.error : %s" % exc)

            logging.critical("Could Not Connect to JSettlers Server :(")

            return False

        logging.info("Connected to JSettlers!")

        return True

    def StartClient(self, serverAddress):

        if self.ConnectToServer(serverAddress):
            while True:
                result = self.Update()
                if result is not None:
                    return result

    def CreateMessage(self, raw_msg):

        highByte = chr(len(raw_msg) / 256)
        lowByte = chr(len(raw_msg) % 256)

        return highByte + lowByte + raw_msg

    def ParseMessage(self, message):
        """ Create a message from recieved data """
        id, txt = message[:4], message[5:]

        if not id in self.messagetbl:
            logging.warning("Can not parse '{0}'".format(message))
            return

        messageClass, messageName = self.messagetbl[id]
        inst = messageClass.parse(txt)

        return (messageName, inst)

    def SendMessage(self, message):

        logging.debug("Sending: {0}".format(message.to_cmd()))

        self.socket.send(self.CreateMessage(message.to_cmd()))

    def Update(self):

        def recvwait(size):
            sofar = 0
            r = ""
            while True:
                r += self.socket.recv(size - len(r))
                if len(r) >= size:
                    break
            return r

        try:
            highByte = ord(recvwait(1))
            lowByte = ord(recvwait(1))
            transLength = highByte * 256 + lowByte
            msg = recvwait(transLength)

            logging.debug("Received this from JSettlers: {0}".format(msg))

        except socket.timeout:
            logging.critical("recv operation timed out.")
            return -1

        try:
            parsed = self.ParseMessage(msg)
        except:
            logging.critical("Failed to parse this message: {0}".format(msg))
            self.socket.close()
            return -1

        if parsed is None:
            logging.debug("Message not supported -- {0}".format(msg))
            return None
        else:
            (messageName, message) = parsed
            winner = self.TreatMessage(messageName, message)
            if winner is not None:
                return self.game.gameState

    def TreatMessage(self, name, instance):

        if name == "GameTextMsgMessage" and self.serverMessages:

            logging.info("Server> " + instance.message)

            if self.game.gameState.isGameOver and self.game.gameState.isLogGenerated:
                return self.game.gameState.winner
            else:
                if self.game.gameState.isGameOver and self.game.gameState.isLogGenerated == False:

                    # EX: robot3 has won the game with 10 points
                    splitMsg = str(instance.message).split()

                    winner = 0
                    for player in self.game.gameState.players:
                        if str(player.name) == str(splitMsg[0]):
                            print("player: {0} at seat {1} is the winner".format(str(player.name), player.seatNumber))
                            winner = player.seatNumber
                            break

                    # I KNOW THIS IS A BAD THING, BUT IT WORKS!!!!
                    self.game.gameState.winner = winner
                    os.chdir(m_clientPath)
                    CSVGenerator.SaveGameStatsCSV(self.game.gameState)

                    self.game.gameState.isLogGenerated = True

                    return winner

        elif name == "ChannelsMessage":

            logging.info("There are {0} channels available: {1}".format(len(instance.channels), instance.channels))

        elif name == "GamesMessage":

            logging.info("There are {0} games available: {1}".format(len(instance.games), instance.games))

            if not self.joinedAGame:
                logging.info("Starting a new game...")
                message = JoinGameMessage(self.player.name, "", socket.gethostname(), self.gameName)
                self.SendMessage(message)

        elif name == "NewGameMessage":

            logging.info("Crated game: '{0}'".format(instance.gameName))

        elif name == "JoinGameAuthMessage":

            logging.info("Entered game: '{0}'".format(instance.gameName))

            self.joinedAGame = True

            self.game = Game(GameState())

            if not self.isSeated:
                logging.info("Sitting on seat number {0}".format(self.player.seatNumber))
                message = SitDownMessage(self.gameName, self.player.name, self.player.seatNumber, True)
                self.SendMessage(message)

        elif name == "SitDownMessage":

            if instance.nickname == self.player.name:
                self.game.AddPlayer(self.player, instance.playerNumber)
            else:
                self.game.AddPlayer(AgentRandom(instance.nickname, instance.playerNumber), instance.playerNumber)

        elif name == "ChangeFaceMessage":

            self.isSeated = True

            if not self.gameStarted:
                logging.info("Seated. Starting game...")

                self.gameStarted = True

                message1 = ChangeFaceMessage(self.gameName, self.player.seatNumber, 44)
                self.SendMessage(message1)

                if self.autoStart:
                    message2 = StartGameMessage(self.gameName)
                    self.SendMessage(message2)

        elif name == "GameMembersMessage":

            logging.info("Players in this game: {0}".format(instance.members))

        elif name == "BoardLayoutMessage":

            logging.info("Received board layout")

            logging.debug("Board Hexes   = {0}".format(instance.hexes))
            logging.debug("Board Numbers = {0}".format(instance.numbers))

            self.game.CreateBoard(instance)

            if self.debugSimulator:
                self.debugGame.CreateBoard(instance)

        elif name == "LongestRoadMessage":

            self.game.gameState.SetLongestRoad(instance.playerNumber)

            logging.info("Received longest road player: {0}".format(self.game.gameState.longestRoadPlayer))

        elif name == "LargestArmyMessage":

            self.game.gameState.SetLargestArmy(instance.playerNumber)

            logging.info("Received largest army player: {0}".format(self.game.gameState.largestArmyPlayer))

        elif name == "PlayerElementMessage":

            self.game.gameState.players[instance.playerNumber].\
                UpdateResourcesFromServer(instance.action, instance.element, instance.value)

            if self.waitBankTradeAck and instance.action == 'GAIN':
                self.waitBankTradeAck = False
                self.RespondToServer()

            if instance.element == 'KNIGHTS':
                self.game.gameState.UpdateLargestArmy()

            negativeResource = False

            for index in range(0, len(g_resources)):
                if self.game.gameState.players[instance.playerNumber].resources[index] < 0:
                    negativeResource = True
                    break

            self.Assert(not negativeResource, "NEGATIVE RESOURCE:\n player: {0} - resources: {1}".format(
                self.game.gameState.players[instance.playerNumber].name,
                self.game.gameState.players[instance.playerNumber].resources
            ))

            logging.debug("CLIENT >>>> Player seated on {0} is {1} : {2} {3} {4}".format(
                instance.playerNumber, self.game.gameState.players[instance.playerNumber].name,
                instance.action, instance.element, instance.value
            ))

            logging.debug("CLIENT >>>> Player seated on {0} is {1}, his resources are: "
                          "\n RESOURCES = {2} \n PIECES = {3} "
                          "\n KNIGHTS = {4}".format(
                instance.playerNumber, self.game.gameState.players[instance.playerNumber].name,
                self.game.gameState.players[instance.playerNumber].resources,
                self.game.gameState.players[instance.playerNumber].numberOfPieces,
                self.game.gameState.players[instance.playerNumber].knights
            ))

        elif name == "GameStateMessage":

            logging.info("Switching gameState from {0} to: {1}".format(self.game.gameState.currState, instance.stateName))

            if instance.stateName == "WAITING_FOR_DISCARDS":
                if self.game.gameState.currState == "WAITING_FOR_DISCARDS":
                    return
                if sum(self.player.resources) <= 7:
                    return

            if self.game.gameState.currState == "WAITING_FOR_TRADE":
                self.game.gameState.currPlayer     = self.game.gameState.currTradeOffer.fromPlayerNumber
                self.game.gameState.currTradeOffer = None

            self.game.gameState.currState = instance.stateName

            if self.debugSimulator:
                logging.debug("GAME STATE = {0} ----  DEBUG GAME STATE = {1}".format(self.game.gameState.currState, self.debugGame.gameState.currState))

            if self.game.gameState.currState == "PLAY" and not self.game.gameState.setupDone:

                self.game.gameState.FinishSetup()

                for index in range(0, len(self.game.gameState.players)):
                    self.game.gameState.players[index].GetStartingResources(self.game.gameState)


            elif self.game.gameState.currState == "PLACING_ROAD" or \
                 self.game.gameState.currState == "PLACING_SETTLEMENT" or \
                 self.game.gameState.currState == "PLACING_CITY":

                if self.game.gameState.currPlayer == self.player.seatNumber:

                    response = self.playerBuildAction.GetMessage(self.gameName,
                                              currGameStateName=instance.stateName)

                    self.playerBuildAction = None

                    self.SendMessage(response)

                return

            elif self.game.gameState.currState == "OVER":

                self.game.gameState.isGameOver = True
                #return winner

            self.RespondToServer()

        elif name == "DevCardMessage":

            #self.UpdateGame(BuyDevelopmentCardAction(instance.playernum))

            if int(instance.playernum) == int(self.player.seatNumber):

                cardType = int(instance.cardtype)
                if cardType > 4 and cardType <= 8:
                    cardType = 4

                # AGENT gain a devcard
                if  int(instance.action) == 0:

                    if   cardType == 0: #KNIGHT
                        self.player.developmentCards[KNIGHT_CARD_INDEX] += 1

                    elif cardType == 1: #ROAD
                        self.player.developmentCards[ROAD_BUILDING_CARD_INDEX] += 1

                    elif cardType == 2: #YEAR_OF_PLENTY
                        self.player.developmentCards[YEAR_OF_PLENTY_CARD_INDEX] += 1

                    elif cardType == 3: #MONOPOLY
                        self.player.developmentCards[MONOPOLY_CARD_INDEX] += 1

                    elif cardType == 4 : #VICTORY_POINTS
                        self.player.developmentCards[VICTORY_POINT_CARD_INDEX] += 1

                # AGENT used a devcard
                elif int(instance.action) == 1:

                    if   cardType == 0:
                        self.player.developmentCards[KNIGHT_CARD_INDEX] -= 1

                    elif cardType == 1:
                        self.player.developmentCards[ROAD_BUILDING_CARD_INDEX] -= 1

                    elif cardType == 2:
                        self.player.developmentCards[YEAR_OF_PLENTY_CARD_INDEX] -= 1

                    elif cardType == 3:
                        self.player.developmentCards[MONOPOLY_CARD_INDEX] -= 1

                    elif cardType == 4 : #VICTORY_POINTS
                        self.player.developmentCards[VICTORY_POINT_CARD_INDEX] -= 1

                if cardType <= 4:
                    self.player.UpdateMayPlayDevCards(cardType, False)

                logging.info("AGENT CARDS: KNIGHT->{0}  ROAD_BUILDING->{1}  YEAR_OF_PLENTY->{2} MONOPOLY->{3} VICTORY_POINT->{4}".format(
                    self.player.developmentCards[0], self.player.developmentCards[1], self.player.developmentCards[2], self.player.developmentCards[3], self.player.developmentCards[4]))

        elif name == "SetPlayedDevCardMessage":

            self.game.gameState.players[instance.playerNumber].playedDevCard = instance.cardFlag

            logging.info("Player seated on {0}:\n Played Dev Card = {1}".format(instance.playerNumber,
                    self.game.gameState.players[instance.playerNumber].playedDevCard))

        elif name == "DevCardCountMessage":

            self.game.gameState.UpdateDevCardsFromServer(instance.count)

            logging.info("Total dev cards available: {0}".format(sum(self.game.gameState.developmentCardsDeck)))

        elif name == "TurnMessage":

            # DEBUG PLAYER RESOURCE COUNT:
            #for index in range(0, len(self.game.gameState.players)):

            #    logging.critical("{0} resources = {1} : count = {2}".format(
            #        self.game.gameState.players[index].name,
            #        self.game.gameState.players[index].resources,
            #        sum(self.game.gameState.players[index].resources)
            #    ))

            if int(self.game.gameState.currPlayer) != int(instance.playerNumber):
                self.game.gameState.currTurn += 1

            self.game.gameState.players[instance.playerNumber].StartTurn()
            self.game.gameState.currPlayer = instance.playerNumber

            if self.game.gameState.startingPlayer == -1:

                self.game.gameState.startingPlayer = instance.playerNumber
                self.game.gameState.currPlayer     = instance.playerNumber

                if self.debugSimulator:

                    self.debugGame.gameState.startingPlayer = instance.playerNumber
                    self.debugGame.gameState.currPlayer     = instance.playerNumber
                    self.debugGame.gameState.currState      = "START1A"

            if self.game.gameState.currPlayer == self.player.seatNumber:
                self.RespondToServer()

        elif name == "PutPieceMessage":

            if instance.playerNumber != self.game.gameState.currPlayer:
                logging.critical("ITS NOT THIS PLAYERS TURN!!!! Received: {0}, Expected: {1}".format(instance.playerNumber, self.game.gameState.currPlayer))

            # if self.debugSimulator:
            #
            #     if instance.pieceType[0] == 'ROAD':
            #         putPieceAction = BuildRoadAction(instance.playerNumber, instance.position,
            #                                          len(self.game.gameState.players[instance.playerNumber].roads))
            #     elif instance.pieceType[0] == 'SETTLEMENT':
            #         putPieceAction = BuildSettlementAction(instance.playerNumber, instance.position,
            #                                                len(self.game.gameState.players[instance.playerNumber].settlements))
            #     elif instance.pieceType[0] == 'CITY':
            #         putPieceAction = BuildCityAction(instance.playerNumber, instance.position,
            #                                          len(self.game.gameState.players[instance.playerNumber].cities))
            #
            #     #putPieceAction.ApplyAction(self.debugGame.gameState)

            self.game.gameState.players[instance.playerNumber].Build(self.game.gameState,
                                                                     instance.pieceType[0],
                                                                     instance.position)

            self.game.gameState.UpdateLongestRoad()

            print("LONGEST ROAD PLAYER = {0}".format(self.game.gameState.longestRoadPlayer))

            logging.info("Player seated on {0} constructed a {1}, have this constructions now:\n"
                         " Roads: {2}\n Settlements: {3}\n Cities: {4}".format(
                instance.playerNumber, instance.pieceType[0],
                [hex(road) for road in self.game.gameState.players[instance.playerNumber].roads],
                [hex(settlement) for settlement in self.game.gameState.players[instance.playerNumber].settlements],
                [hex(city) for city in self.game.gameState.players[instance.playerNumber].cities]
            ))

            if self.debugSimulator:

                logging.info("***DEBUG GAME***\nDebugPlayer seated on {0} constructed a {1}, have this constructions now:\n"
                             " Roads: {2}\n Settlements: {3}\n Cities: {4}".format(
                    instance.playerNumber, instance.pieceType[0],
                    [hex(road) for road in self.debugGame.gameState.players[instance.playerNumber].roads],
                    [hex(settlement) for settlement in self.debugGame.gameState.players[instance.playerNumber].settlements],
                    [hex(city) for city in self.debugGame.gameState.players[instance.playerNumber].cities]
                ))

        elif name == "DiceResultMessage":

            logging.info("---- Dices are rolled! ----\n Dice Result = {0}".format(instance.result))

            self.game.gameState.dicesAreRolled = True

            if self.debugSimulator:

                RollDicesAction(self.game.gameState.currPlayer, result=instance.result).\
                    ApplyAction(self.debugGame.gameState)

        elif name == "MoveRobberMessage":

            logging.info("Player {0} placed the robber on hex {1}".format(instance.playerNumber, hex(self.game.gameState.robberPos)))

            self.game.gameState.players[instance.playerNumber].PlaceRobber(self.game.gameState, instance.position)

            if self.debugSimulator:

                PlaceRobberAction(self.game.gameState.currPlayer, instance.position).\
                    ApplyAction(self.debugGame.gameState)

        elif name == "MakeOfferMessage":

            # TODO -> Make proper trade offer...
            # TRADE?
            #if instance.to[self.player.seatNumber]:
            #    self.SendMessage(RejectOfferMessage(self.gameName, self.player.seatNumber))
            if instance.fr != self.player.seatNumber and instance.to[self.player.seatNumber]:

                if self.player.trading is not None:

                    if self.player.trading == 'Optimistic' and self.game.gameState.currPlayer == self.player.seatNumber:
                        self.SendMessage(RejectOfferMessage(self.gameName, self.player.seatNumber))
                    else:
                        previousPlayer  = self.game.gameState.currPlayer
                        makeOfferAction = MakeTradeOfferAction(instance.fr, instance.to, instance.give, instance.get)
                        makeOfferAction.ApplyAction(self.game.gameState, self.player.seatNumber)
                        self.RespondToServer()
                        self.game.gameState.currPlayer = previousPlayer
                else:
                    self.SendMessage(RejectOfferMessage(self.gameName, self.player.seatNumber))

        elif name == "RejectOfferMessage":

            if self.game.gameState.currPlayer == self.player.seatNumber and \
                instance.playerNumber == self.player.seatNumber:
                self.tradeResultCount = -1
                self.waitTradeResult = False
                self.game.gameState.currState = "PLAY1"
                self.game.gameState.currTradeOffer = None
                self.SendMessage(ClearOfferMessage(self.gameName, self.player.seatNumber))
                self.RespondToServer()
                return

            if self.waitTradeResult:
                self.tradeResultCount -= 1
                print("trade result count = {0}".format(self.tradeResultCount))
                if self.tradeResultCount <= 0:
                    self.tradeResultCount = -1
                    self.waitTradeResult = False
                    self.SendMessage(ClearOfferMessage(self.gameName, self.player.seatNumber))
                    self.RespondToServer()

        elif name == "AcceptOfferMessage":

            if self.game.gameState.currPlayer == self.player.seatNumber and \
                instance.accepting == self.player.seatNumber:
                self.tradeResultCount = -1
                self.waitTradeResult = False
                self.game.gameState.currState = "PLAY1"
                self.game.gameState.currTradeOffer = None
                self.SendMessage(ClearOfferMessage(self.gameName, self.player.seatNumber))
                self.RespondToServer()
                return

            if self.waitTradeResult and instance.offering == self.player.seatNumber:
                self.tradeResultCount = -1
                self.waitTradeResult = False
                self.SendMessage(ClearOfferMessage(self.gameName, self.player.seatNumber))
                self.RespondToServer()

        # elif name == "ChoosePlayerRequestMessage":
        #
        #     choosePlayerAction = self.player.ChoosePlayerToStealFrom(self.game.gameState, self.player)
        #
        #     self.SendMessage(choosePlayerAction.GetMessage(self.gameName))
        #
        #     if self.debugSimulator:
        #
        #         choosePlayerAction.ApplyAction(self.debugGame.gameState)

    preGameStates = ['NEW', 'READY']

    def RespondToServer(self):

        if self.game.gameState.currState in Client.preGameStates:
            return

        #localActionUpdates = ['BankTradeOffer','DiscardResources',
        #                      'UseKnightsCard','UseMonopolyCard','UseYearOfPlentyCard',
        #                      'UseFreeRoadsCard', 'EndTurn']

        if len(self.tradeBuffer) > 0:
            nextTrade = self.tradeBuffer.pop()
            self.waitTradeResult = True
            self.tradeResultCount = sum(nextTrade.toPlayers)
            self.SendMessage(nextTrade.GetMessage(self.gameName, currGameStateName=self.game.gameState.currState))
            return

        agentAction = self.player.DoMove(self.game)

        if agentAction is not None:

            response = agentAction.GetMessage(self.gameName,
                                              currGameStateName=self.game.gameState.currState)

            if agentAction.type == 'BuildRoad' or \
               agentAction.type == 'BuildSettlement' or \
               agentAction.type == 'BuildCity' or \
               agentAction.type == 'BuyDevelopmentCard':

                if agentAction.tradeOptimistic:
                    self.tradeBuffer = self.player.GetRemainingTrades(agentAction.cost)
                    nextTrade = self.tradeBuffer.pop()
                    self.waitTradeResult = True
                    self.tradeResultCount = sum(nextTrade.toPlayers)
                    self.player.tradeLock = True
                    self.SendMessage(nextTrade.GetMessage(self.gameName, currGameStateName=self.game.gameState.currState))
                    return

            if agentAction.type == 'BuildRoad' or \
               agentAction.type == 'BuildSettlement' or \
               agentAction.type == 'BuildCity':

                self.playerBuildAction = agentAction

            if agentAction.type == 'BankTradeOffer':

                self.waitBankTradeAck = True

            if agentAction.type == 'EndTurn':
                # @REVIEW@
                self.player.UpdateMayPlayDevCards(None, True)

            if agentAction.type == 'MakeTradeOffer':

                self.waitTradeResult  = True
                self.tradeResultCount = sum(response.to)
                self.player.tradeLock = True

            if self.debugSimulator:

                agentAction.ApplyAction(self.debugGame.gameState)

            if response is not None:

                if isinstance(response, list):

                    for index in range(0, len(response)):
                        self.SendMessage(response[index])

                else:
                    self.SendMessage(response)

#logging.getLogger().setLevel(logging.INFO)
#logging.getLogger().setLevel(logging.DEBUG) # FOR DEBUG

#client = Client("TestGame", AgentRandom("Danda", 0), True, True)
#client.StartClient(("localhost", 8880))