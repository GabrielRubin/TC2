import socket
import sys



class JSettlersClient:

    def __init__(self):

        self.socket      = None
        self.client      = None

        self.connected   = False
        self.isSeated    = False
        self.gameStarted = False

        self.gameName    = ""
        self.seatNumber  = 0
        self.player      = None


    def StartClient(self, gameName, seatNumber):
        pass

    def ConnectToJSettlers(self, address):

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(address)
        except:
            return False
        return True

    #def Update(self):



client = JSettlersClient()

if not client.ConnectToJSettlers(("localhost", 8880)):
    print("Could not connect to JSettlers server!")
    exit(-1)
