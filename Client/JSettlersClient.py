import socket
import sys
import errno
import time
import select
import threading

class RecvThread(threading.Thread):
    def __init__(self, ip, port):

        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port

    def run(self):

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.ip, self.port))
            while True:
                try:
                    highByte = ord(self.client.recv(1))
                    lowByte = ord(self.client.recv(1))
                    transLength = highByte * 256 + lowByte
                    msg = self.client.recv(transLength)
                    if not msg:
                        print("connection closed")
                        self.client.close()
                        break
                    else:
                        # print("Received %d bytes: '%s'" % (len(msg), msg))
                        self.parse_message(msg)
                except socket.error, e:
                    if e.args[0] == errno.EWOULDBLOCK:
                        print('EWOULDBLOCK')
                        break
                        # time.sleep(1)  # short delay, no tight loops
                    else:
                        print(e)
                        break
        except:
            return False
        return True

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


    #def StartClient(self, address):
#
    #    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #    self.client.connect(address)
    #    #self.client.setblocking(0)
    #    self.run()
#
#
    #def run(self):
#
    #    ret = None
    #    while True:
#
    #        ret = self.runUpdate()
    #        if ret != None:
    #            return ret
#
    #def runUpdate(self):
#
    #    def recvwait(size):
    #        sofar = 0
    #        r = ""
    #        while True:
    #            r += self.client.recv(size - len(r))
    #            if len(r) >= size:
    #                break
    #        return r
#
    #    try:
    #        highByte = ord(recvwait(1))
    #        lowByte = ord(recvwait(1))
    #        transLength = highByte * 256 + lowByte
    #        msg = recvwait(transLength)
    #    except socket.timeout:
    #        logging.critical("recv operation timed out.")
    #        return -1
#
    #    try:
    #        parsed = self.parse_message(msg)
    #    except:
    #        #logging.critical("Failed to parse this message: {0}".format(msg))
    #        self.client.close()
    #        return -1

    def ConnectToJSettlers(self, address):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(address)
            self.client.setblocking(0)

            while True:

                print("wooow")

                r, w, e = select.select([self.client], [], [], 1)

                if r[0]:
                    try:
                        highByte = ord(self.client.recv(1))
                        lowByte  = ord(self.client.recv(1))
                        transLength = highByte * 256 + lowByte
                        msg = self.client.recv(transLength)
                        if not msg:
                            print("connection closed")
                            self.client.close()
                            break
                        else:
                            #print("Received %d bytes: '%s'" % (len(msg), msg))
                            self.parse_message(msg)
                    except socket.error, e:
                        if e.args[0] == errno.EWOULDBLOCK:
                            print('EWOULDBLOCK')
                            break
                            #time.sleep(1)  # short delay, no tight loops
                        else:
                            print(e)
                            break
                else:
                    continue
        except:
            return False
        return True

    #def Update(self):
    def parse_message(self, msg):
        """ Create a message from recieved data """
        id, txt = msg[:4], msg[5:]

        print("received this msg id: {0}".format(id))
        print("content: {0}".format(txt))
        #if not id in self.messagetbl:
        #    logging.critical("Can not parse '{0}'".format(msg))
        #    return

        #message_class, name = self.messagetbl[id]
        #inst = message_class.parse(txt)
        #if inst:
        #    self.update_game(name, inst)
        #return (name, inst)


client = JSettlersClient()

newthread = RecvThread("localhost", 8880)
newthread.start()

while True:
    time.sleep(30)

#if not client.ConnectToJSettlers(("localhost", 8880)):
#    print("Could not connect to JSettlers server!")
#    exit(-1)
