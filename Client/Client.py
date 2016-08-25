import socket
import logging
from JSettlersMessages import *

class Client:

    def __init__(self):

        self.socket = None
        self.game   = None

        self.isConnected = False
        self.isSeated    = False
        self.gameStarted = False

        self.gameName    = ""
        self.seatNumber  = 0
        self.player      = None

        self.messagetbl = {}
        for g in globals():
            cg = globals()[g]
            if g.endswith("Message") and hasattr(cg, "id"):
                self.messagetbl[str(cg.id)] = (cg, g)

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

    def SendMsg(self, msg):

        logging.debug("Sending: {0}".format(msg.to_cmd()))

        self.socket.send(self.CreateMessage(msg.to_cmd()))

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

    def ParseMessage(self, message):
        """ Create a message from recieved data """
        id, txt = message[:4], message[5:]

        if not id in self.messagetbl:
            logging.critical("Can not parse '{0}'".format(message))
            return

        messageClass, messageName = self.messagetbl[id]
        inst = messageClass.parse(txt)

        return (messageName, inst)

    def TreatMessage(self, name, instance):

        if name   == "ChannelsMessage":
            logging.info("There are {0} channels available: {1}".format(len(instance.channels), instance.channels))

        elif name == "GamesMessage":
            logging.info("There are {0} games available: {1}".format(len(instance.games), instance.games))

    def SendMessage(self):
        pass

logging.getLogger().setLevel(logging.INFO)
#logging.getLogger().setLevel(logging.DEBUG) # FOR DEBUG

client = Client()
client.StartClient(("localhost", 8880))