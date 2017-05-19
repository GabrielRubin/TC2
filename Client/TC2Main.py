import subprocess
import os
import signal
import time
import argparse

from Client import *
from AgentRandom import *
from AgentMCTS import AgentMCTS
from AgentUCT  import AgentUCT
from AgentRAVE import AgentRAVE
from AgentUCTParanoid import AgentUCTParanoid
from AgentUCTTuned import AgentUCTTuned
import CSVGenerator

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

class TC2Main(object):

    def __init__(self):

        self.serverProcess = None
        self.robot1Process = None
        self.robot2Process = None
        self.robot3Process = None
        self.clientProcess = None
        self.player        = None
        self.ourClient     = None
        self.simCount      = 1000

    def ComposeGameStatsMessage(self, gameState):

        msg =  "#########################################################\n" \
              +"Game Over! Player {0} Wins!\n".format(gameState.players[gameState.winner].name) \
              +"GAME STATS:\n" \
              +" total turns: {0} \n starting player: {1} \n largest army player: {2} \n longest road player: {3}\n".format(
                    gameState.currTurn,
                    gameState.startingPlayer,
                    gameState.largestArmyPlayer,
                    gameState.longestRoadPlayer
                )\
              +"#########################################################\n"

        for n in range(0, len(gameState.players)):
            msg += "Player {0} stats:".format(gameState.players[n].name)\
                +  "Player {0} is a {1} agent".format(gameState.players[n].name,
                                                      gameState.players[n].agentName) \
                +    "his resources are: "       \
                     "\n POINTS          = {0} " \
                     "\n LARGEST ARMY    = {1} " \
                     "\n LONGEST ROAD    = {2} " \
                     "\n RESOURCES       = {3} " \
                     "\n PIECES          = {4} " \
                     "\n KNIGHTS         = {5} " \
                     "\n DICE PRODUCTION = {6}".format(
                        gameState.players[n].GetVictoryPoints(),
                        gameState.players[n].biggestArmy,
                        gameState.players[n].biggestRoad,
                        gameState.players[n].resources,
                        gameState.players[n].numberOfPieces,
                        gameState.players[n].knights,
                        gameState.players[n].diceProduction
                    )\

            devCards = ""

            for j in range(0, len(g_developmentCards)):
                devCards += " {0} : {1}".format(
                    g_developmentCards[j], gameState.players[n].developmentCards[n]
                )

            msg += "DevCards : " + devCards

            msg += " Roads: {0}\n Settlements: {1}\n Cities: {2}".format(
                    [hex(road) for road in gameState.players[n].roads],
                    [hex(settlement) for settlement in gameState.players[n].settlements],
                    [hex(city) for city in gameState.players[n].cities])

            msg += "---------------------------------------------------------"

            return msg

    def SaveGameStats(self, gameState):

        msg = self.ComposeGameStatsMessage(gameState)

        if os.path.isfile("SimulatorLogs/JSettlersVSGames.txt"):

            with open("SimulatorLogs/JSettlersVSGames.txt", "a") as text_file:
                text_file.write("\n"+msg)
        else:

            with open("SimulatorLogs/JSettlersVSGames.txt", "w") as text_file:
                text_file.write(msg)


    def RunClient(self, killProcess=True):
        result = self.ourClient.StartClient(("localhost", 8880))
        return result
        # try:
        #     result = self.ourClient.StartClient(("localhost", 8880))
        #
        # finally:
        #
        #     if killProcess:
        #       self.clientProcess.kill()
        #       self.robot1Process.kill()
        #       self.robot2Process.kill()
        #       self.robot3Process.kill()
        #
        #     return result

    def InitGame(self, canInitServer = True, gameNamePrefix = None, callProcess=True):

        AgentTypes = { 'rand' : 'random', 'min' : 'minimax', 'exp' : 'expectimax', 'mcts' : 'monte carlo tree search', 'uct' : 'upper confidence bound for trees', 'rave' : 'AMAF-rave'}

        LogType    = { 'i' : 'info', 'd' : 'debug' }

        parser = argparse.ArgumentParser()

        parser.add_argument("-at", "--agentType", help="choose one of these types of agent: {0}".format(AgentTypes),
                            default = 'uct')

        parser.add_argument("-n", "--nickname", help="the nickname the agent will use during gameplay",
                            default='TC2_agent')

        parser.add_argument("-ns", "--startServer", help="start the JSettlers server (default:True)",
                            action="store_true", default=True)

        parser.add_argument("-nr", "--robots", help="start the JSettlers robots (default:True)",
                            action="store_true", default=True)

        parser.add_argument("-nc", "--client", help="start the JSettlers client (default:True)",
                            action="store_true", default=True)

        parser.add_argument("-ng", "--game", help="start a new game if True, waits for the game to start otherwise (default:True)",
                            action="store_true", default=True)

        parser.add_argument('-sim', "--simulationCount", type=check_positive,
                            help="number of simulations done by MCTS methods (default = 1000)", default=1000)

        parser.add_argument("-l", "--logging", help="log stuff. There are two levels of logging: {0}".format(LogType),
                            default='d')

        parser.add_argument("-sl", "--saveLog", help="if log is enabled, let it be saved on the specified file")

        args = parser.parse_args()

        self.simCount = args.simulationCount

        if args.agentType == 'rand':
            self.player = AgentRandom(args.nickname, 0)

        if args.agentType == 'mcts':
            # 10.000 sims without multiThread - 2 min and 30 sec
            # 10.000 sims with    multiThread - 50 sec
            self.player = AgentMCTS(args.nickname, 0, simulationCount=self.simCount, multiThreading=False)

        if args.agentType == 'uct':
            self.player = AgentUCT(args.nickname, 0, simulationCount=self.simCount, explorationValue=0.25, multiThreading=True, numberOfThreads=10,
                                   preSelectMode='citiesOverSettlements', simPreSelectMode='citiesOverSettlements', trading=False)

        if args.agentType == 'rave':
            self.player = AgentRAVE(args.nickname, 0, simulationCount=self.simCount, multiThreading=False)

        if args.agentType == 'paranoid':
            self.player = AgentUCTParanoid(args.nickname, 0, simulationCount=self.simCount, multiThreading=True, numberOfThreads=10)

        if args.agentType == 'uctTuned':
            self.player = AgentUCTTuned(args.nickname, 0, simulationCount=self.simCount, multiThreading=True, numberOfThreads=10)

        # Change the current directory...
        mycwd = os.getcwd()

        os.chdir("..")
        # print("changing to folder "+os.path.join(os.getcwd(), "JSettlers-1.0.6"))
        # os.chdir("\""+os.path.join(os.getcwd(), "JSettlers-1.0.6")+"\"")
        # The line above does not seem to work in my computer because of spaces or quotes
        os.chdir('JSettlers-1.0.6')

        # Double negation in the switches here are a bit confusing TBH...
        if args.startServer and canInitServer:

            self.serverProcess = subprocess.Popen("java -jar JSettlersServer.jar 8880 10 dbUser dbPass",
                                             shell=False, stdout=subprocess.PIPE)

        if args.robots and callProcess:
            self.robot1Process = subprocess.Popen(
                "java -cp JSettlersServer.jar soc.robot.SOCRobotClient localhost 8880 robot1 passwd",
                shell=True, stdout=subprocess.PIPE)

            self.robot2Process = subprocess.Popen(
                "java -cp JSettlersServer.jar soc.robot.SOCRobotClient localhost 8880 robot2 passwd",
                shell=True, stdout=subprocess.PIPE)

            self.robot3Process = subprocess.Popen(
                "java -cp JSettlersServer.jar soc.robot.SOCRobotClient localhost 8880 robot3 passwd",
                shell=True, stdout=subprocess.PIPE)

        if args.client and callProcess:

            self.clientProcess = subprocess.Popen("java -jar JSettlers.jar localhost 8880")

        # Go back to the Client directory...
        os.chdir(mycwd)

        if args.logging == 'i':
            logging.getLogger().setLevel(logging.INFO)
        elif args.logging == 'd':
            logging.getLogger().setLevel(logging.DEBUG)

        #logging.getLogger().setLevel(logging.CRITICAL)

        gameName = "TestGame"
        if gameNamePrefix is not None:
            gameName += str(gameNamePrefix)

        if not args.game:
            self.ourClient = Client(gameName, self.player, False, True)
        else:
            self.ourClient = Client(gameName, self.player, True, True)

    if __name__ == '__main__':

        from TC2Main import TC2Main

        main = TC2Main()

        main.InitGame()
        # Give some time so the server can start and the robots get in....
        time.sleep(2)

        main.RunClient()