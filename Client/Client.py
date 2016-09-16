import sys
import socket
import logging
from JSettlersMessages import *
from CatanPlayer import *
from CatanGame import *
from CatanAction import *

class Client:

    def __init__(self, gameName, player, autoStart, showServerMessages):

        self.socket         = None
        self.game           = None

        self.joinedAGame    = False
        self.isSeated       = False
        self.gameStarted    = False

        self.gameName       = gameName
        self.player         = player
        self.playerBuildReq = None

        self.autoStart      = autoStart
        self.botsInit       = False

        self.serverMessages = showServerMessages

        self.waitBankTradeAck = False
        self.gotBankTradeAck  = False

        self.messagetbl = {}
        for g in globals():
            cg = globals()[g]
            if g.endswith("Message") and hasattr(cg, "id"):
                self.messagetbl[str(cg.id)] = (cg, g)

    # Connection to jsettlers game server
    def ConnectToServer(self, serverAddress):

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket.connect(serverAddress)

            self.socket.settimeout(240)

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
            self.TreatMessage(messageName, message)

    def TreatMessage(self, name, instance):

        if   name == "GameTextMsgMessage" and self.serverMessages:

            logging.info("Server> " + instance.message)

            if self.waitBankTradeAck:

                if self.gotBankTradeAck:
                    self.waitBankTradeAck = False
                    self.gotBankTradeAck  = False
                    self.RespondToServer()
                else:
                    self.waitBankTradeAck = False

        if   name == "ChannelsMessage":

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
                self.game.AddPlayer(Player(instance.nickname, instance.playerNumber), instance.playerNumber)

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

        elif name == "LongestRoadMessage":

            self.game.gameState.longestRoadPlayer = int(instance.playerNumber)

            logging.info("Received longest road player: {0}".format(self.game.gameState.longestRoadPlayer))

        elif name == "LargestArmyMessage":

            self.game.gameState.largestArmyPlayer = int(instance.playerNumber)

            logging.info("Received largest army player: {0}".format(self.game.gameState.largestArmyPlayer))

        elif name == "PlayerElementMessage":

            if self.waitBankTradeAck:

                self.gotBankTradeAck = True

            if instance.element in g_resources: #RESOURCE

                if instance.action == 'SET':
                    self.game.gameState.players[instance.playerNumber].resources[g_resources.index(instance.element)] = instance.value
                elif instance.action == 'GAIN':
                    self.game.gameState.players[instance.playerNumber].resources[g_resources.index(instance.element)] += instance.value
                elif instance.action == 'LOSE':
                    self.game.gameState.players[instance.playerNumber].resources[g_resources.index(instance.element)] -= instance.value

            elif instance.element in g_pieces: #PIECES

                if instance.action == 'SET':
                    self.game.gameState.players[instance.playerNumber].numberOfPieces[g_pieces.index(instance.element)] = instance.value
                elif instance.action == 'GAIN':
                    self.game.gameState.players[instance.playerNumber].numberOfPieces[g_pieces.index(instance.element)] += instance.value
                elif instance.action == 'LOSE':
                    self.game.gameState.players[instance.playerNumber].numberOfPieces[g_pieces.index(instance.element)] -= instance.value

            elif instance.element == 'KNIGHTS': #KNIGHTS

                if instance.action == 'SET':
                    self.game.gameState.players[instance.playerNumber].knights = instance.value
                elif instance.action == 'GAIN':
                    self.game.gameState.players[instance.playerNumber].knights += instance.value
                elif instance.action == 'LOSE':
                    self.game.gameState.players[instance.playerNumber].knights -= instance.value

            # DEBUG - SANITY CHECK
            logging.debug("Player seated on {0} is {1}, his resources are: \n RESOURCES = {2} \n PIECES = {3} \n KNIGHTS = {4}".format(
                instance.playerNumber, self.game.gameState.players[instance.playerNumber].name,
                self.game.gameState.players[instance.playerNumber].resources,
                self.game.gameState.players[instance.playerNumber].numberOfPieces,
                self.game.gameState.players[instance.playerNumber].knights
            ))

        elif name == "GameStateMessage":

            logging.info("Switching gameState from {0} to: {1}".format(self.game.gameState.currState, instance.stateName))

            self.game.gameState.currState = instance.stateName

            if instance.stateName == "START1A":

                logging.info("Game Begin!\n Players in this game are: {0}".format([player.name for player in self.game.gameState.players]))

            elif instance.stateName == "PLACING_ROAD" or \
                 instance.stateName == "PLACING_SETTLEMENT" or \
                 instance.stateName == "PLACING_CITY":

                if self.game.gameState.currPlayer == self.player.seatNumber:

                    response = PutPieceMessage(self.gameName, self.player.seatNumber,
                                               self.playerBuildReq.pieceId, self.playerBuildReq.position)

                    self.SendMessage(response)

                return

            elif instance.stateName == "OVER":
                pass

            self.RespondToServer()

        elif name == "DevCardMessage":

            if int(instance.playernum) == int(self.player.seatNumber):

                cardType = int(instance.cardtype)
                if cardType > 4 and cardType <= 8:
                    cardType = 4

                # DANDA gain a devcard
                if  int(instance.action) == 0:

                    # alternative logic:
                    # if int(instance.cardtype) >= 4 and int(instance.cardtype) <= 8: #VICTORY_POINTS
                    #    self.player.developmentCards[VICTORY_POINT_CARD_INDEX] += 1
                    #elif int(instance.cardtype) >= 0:
                    #   self.player.developmentCards[int(instance.cardtype)] += 1

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

                # DANDA used a devcard
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

                logging.info("DANDA CARDS: KNIGHT->{0}  ROAD_BUILDING->{1}  YEAR_OF_PLENTY->{2} MONOPOLY->{3} VICTORY_POINT->{4}".format(
                    self.player.developmentCards[0], self.player.developmentCards[1], self.player.developmentCards[2], self.player.developmentCards[3], self.player.developmentCards[4]))

        elif name == "SetPlayedDevCardMessage":

            self.game.gameState.players[instance.playerNumber].playedDevCard = instance.cardFlag

            logging.info("Player seated on {0}:\n Played Dev Card = {1}".format(instance.playerNumber,
                    self.game.gameState.players[instance.playerNumber].playedDevCard))

        elif name == "DevCardCountMessage":

            self.game.gameState.devCards = instance.count

            logging.info("Total dev cards available: {0}".format(self.game.gameState.devCards))

        elif name == "TurnMessage":

            self.game.gameState.currPlayer = instance.playerNumber

            self.RespondToServer()

        elif name == "PutPieceMessage":

            if instance.pieceType[0] == 'ROAD':
                putPieceAction = BuildRoadAction(instance.playerNumber, instance.position, len(self.game.gameState.players[instance.playerNumber].roads) )
            elif instance.pieceType[0] == 'SETTLEMENT':
                putPieceAction = BuildSettlementAction(instance.playerNumber, instance.position, len(self.game.gameState.players[instance.playerNumber].settlements))
            elif instance.pieceType[0] == 'CITY':
                putPieceAction = BuildCityAction(instance.playerNumber, instance.position, len(self.game.gameState.players[instance.playerNumber].cities))

            self.game.gameState.ApplyAction(putPieceAction, True)

            logging.info("Player seated on {0} constructed a {1}, have this constructions now:\n"
                         " Roads: {2}\n Settlements: {3}\n Cities: {4}".format(
                instance.playerNumber, instance.pieceType[0],
                [hex(road) for road in self.game.gameState.players[instance.playerNumber].roads],
                [hex(settlement) for settlement in self.game.gameState.players[instance.playerNumber].settlements],
                [hex(city) for city in self.game.gameState.players[instance.playerNumber].cities]
            ))

        elif name == "DiceResultMessage":

            logging.info("---- Dices are rolled! ----\n Dice Result = {0}".format(instance.result))

        elif name == "MoveRobberMessage":

            self.game.gameState.robberPos = instance.position

            logging.info("Player {0} placed the robber on hex {1}".format(instance.playerNumber, hex(self.game.gameState.robberPos)))

        elif name == "MakeOfferMessage":

            # TODO > Review this!!!
            # TRADE?
            if instance.to[int(self.player.seatNumber)] == "true":
                self.SendMessage(RejectOfferMessage(self.gameName, self.player.seatNumber))

        elif name == "ChoosePlayerRequestMessage":

            choosePlayerAction = self.player.ChoosePlayerToStealFrom(self.game)

            self.SendMessage(ChoosePlayerMessage(self.gameName, choosePlayerAction.targetPlayerNumber))

    def RespondToServer(self):

        agentAction = None

        if self.game.gameState.currState == "WAITING_FOR_DISCARDS":

            agentAction = self.player.ChooseCardsToDiscard(self.game)

        elif self.player.seatNumber == self.game.gameState.currPlayer: # ITS OUR TURN:

            #@REVIEW@
            self.player.UpdateMayPlayDevCards(None, True)

            agentAction = self.player.DoMove(self.game)

        if agentAction is not None:

            response = None

            if agentAction.type == 'BuildRoad' or \
               agentAction.type == 'BuildSettlement' or \
               agentAction.type == 'BuildCity':

                if self.game.gameState.currState == "START1A" or self.game.gameState.currState == "START1B" or \
                   self.game.gameState.currState == "START2A" or self.game.gameState.currState == "START2B":

                    response = PutPieceMessage(self.gameName, self.player.seatNumber,
                                               agentAction.pieceId, agentAction.position)
                else:
                    response = BuildRequestMessage(self.gameName, agentAction.pieceId)

                    self.playerBuildReq = agentAction

            if agentAction.type == 'RollDices':

                response = RollDiceMessage(self.gameName)

            if agentAction.type == 'PlaceRobber':

                response = MoveRobberMessage(self.gameName, self.player.seatNumber, agentAction.robberPos)

            if agentAction.type == 'DiscardResources':

                response = DiscardMessage(self.gameName, agentAction.resources[0], agentAction.resources[1],
                                                         agentAction.resources[2], agentAction.resources[3],
                                                         agentAction.resources[4], agentAction.resources[5])

            if agentAction.type == 'BankTradeOffer':

                response = BankTradeMessage(self.gameName, agentAction.giveResources, agentAction.getResources)

                self.waitBankTradeAck = True

            if agentAction.type == 'BuyDevelopmentCard':

                logging.info("COMPROU!!!!")

                response = BuyCardRequestMessage(self.gameName)

            if agentAction.type == 'UseKnightsCard':

                response = PlayDevCardRequestMessage(self.gameName, KNIGHT_CARD_INDEX)

            if agentAction.type == 'UseFreeRoadsCard':

                response = PlayDevCardRequestMessage(self.gameName, ROAD_BUILDING_CARD_INDEX)

            if agentAction.type == 'UseYearOfPlentyCard':

                response = None

                self.SendMessage(PlayDevCardRequestMessage(self.gameName, YEAR_OF_PLENTY_CARD_INDEX))
                self.SendMessage(DiscoveryPickMessage(self.gameName, agentAction.resources))

            if agentAction.type == 'UseMonopolyCard':

                response = None

                self.SendMessage(PlayDevCardRequestMessage(self.gameName, MONOPOLY_CARD_INDEX))
                self.SendMessage(MonopolyPickMessage(self.gameName, agentAction.resource))

            if agentAction.type == 'EndTurn':

                response = EndTurnMessage(self.gameName)

            if response is not None:
                self.SendMessage(response)

#logging.getLogger().setLevel(logging.INFO)
#logging.getLogger().setLevel(logging.DEBUG) # FOR DEBUG
#
#client = Client("TestGame", AgentRandom("Danda", 0), True, True)
#client.StartClient(("localhost", 8880))