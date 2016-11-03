import subprocess
import os
import signal
import time
import argparse

from Client import *
from AgentRandom import *
from AgentMCTS import AgentMCTS

def ComposeGameStatsMessage(gameState):

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

def SaveGameStats(gameState):

        msg = ComposeGameStatsMessage(gameState)

        if os.path.isfile("SimulatorLogs/JSettlersVSGames.txt"):

            with open("SimulatorLogs/JSettlersVSGames.txt", "a") as text_file:
                text_file.write("\n"+msg)
        else:

            with open("SimulatorLogs/JSettlersVSGames.txt", "w") as text_file:
                text_file.write(msg)


AgentTypes = { 'rand' : 'random', 'min' : 'minimax', 'exp' : 'expectimax', 'mcts' : 'monte carlo tree search'}

LogType    = { 'i' : 'info', 'd' : 'debug' }

serverProcess = None
robot1Process = None
robot2Process = None
robot3Process = None
clientProcess = None

parser = argparse.ArgumentParser()

parser.add_argument("-at", "--agentType", help="choose one of these types of agent: {0}".format(AgentTypes),
                    default = 'mcts')

parser.add_argument("-n", "--nickname", help="the nickname the agent will use during gameplay",
                    default='TC2_agent')

parser.add_argument("-ns", "--noServer", help="don't start the JSettlers server",
                    action="store_true", default=False)

parser.add_argument("-nr", "--noRobots", help="don't start the JSettlers robots",
                    action="store_true", default=False)

parser.add_argument("-nc", "--noClient", help="don't start the JSettlers client",
                    action="store_true", default=False)

parser.add_argument("-ng", "--noGame", help="agent don't start a new game; waits for the game to start",
                    action="store_true", default=False)

parser.add_argument("-l", "--logging", help="log stuff. There are two levels of logging: {0}".format(LogType),
                    default='d')

parser.add_argument("-sl", "--saveLog", help="if log is enabled, let it be saved on the specified file")

args = parser.parse_args()

if args.agentType == 'rand':
    player = AgentRandom(args.nickname, 0)

if args.agentType == 'mcts':
    player = AgentMCTS(args.nickname, 0)


# Change the current directory...
mycwd = os.getcwd()

os.chdir("..")
# print("changing to folder "+os.path.join(os.getcwd(), "JSettlers-1.0.6"))
# os.chdir("\""+os.path.join(os.getcwd(), "JSettlers-1.0.6")+"\"")
# The line above does not seem to work in my computer because of spaces or quotes
os.chdir('JSettlers-1.0.6')

# Double negation in the switches here are a bit confusing TBH...
if not args.noServer:

    serverProcess = subprocess.Popen("java -jar JSettlersServer.jar 8880 10 dbUser dbPass",
                                     shell=False, stdout=subprocess.PIPE)

if not args.noRobots:

    robot1Process = subprocess.Popen(
        "java -cp JSettlersServer.jar soc.robot.SOCRobotClient localhost 8880 robot1 passwd",
        shell=True, stdout=subprocess.PIPE)

    robot2Process = subprocess.Popen(
        "java -cp JSettlersServer.jar soc.robot.SOCRobotClient localhost 8880 robot2 passwd",
        shell=True, stdout=subprocess.PIPE)

    robot3Process = subprocess.Popen(
        "java -cp JSettlersServer.jar soc.robot.SOCRobotClient localhost 8880 robot3 passwd",
        shell=True, stdout=subprocess.PIPE)

if not args.noClient:

    clientProcess = subprocess.Popen("java -jar JSettlers.jar localhost 8880")

# Go back to the Client directory...
os.chdir(mycwd)

if args.logging == 'i':
    logging.getLogger().setLevel(logging.INFO)
elif args.logging == 'd':
    logging.getLogger().setLevel(logging.DEBUG)

#logging.getLogger().setLevel(logging.CRITICAL)

if args.noGame:
    ourClient = Client("TestGame", player, False, True)
else:
    ourClient = Client("TestGame", player, True, True)


# Give some time so the server can start and the robots get in....
time.sleep(2)

try:
    games = 2
    winCount = [0, 0, 0, 0]
    for i in range(games):

        gameState = ourClient.StartClient(("localhost", 8880))

        winCount[gameState.winner] += 1

        today = datetime.datetime.today()

        SaveGameStats(gameState)

        player = AgentMCTS(args.nickname, 0)

        ourClient = Client("TestGame{0}".format(i+1), player, True, True)

    today = datetime.datetime.today()

    if os.path.isfile("SimulatorLogs/JSettlersVSResults.txt"):

        with open("SimulatorLogs/JSettlersVSResults.txt", "a") as text_file:
            text_file.write("\nRESULTS FROM {0}: \n"
                            "   TOTAL GAMES:          {1}\n"
                            "   WIN COUNT:            {2}\n"
                            "   AGENT WIN PERCENTAGE: {3}%".format(
                today.strftime("%d/%m/%Y %H:%M"),
                winCount,
                (float(winCount[player.seatNumber]) / games) * 100.0))
    else:

        with open("SimulatorLogs/JSettlersVSResults.txt", "w") as text_file:
            text_file.write("\nRESULTS FROM {0}: \n"
                            "   TOTAL GAMES:          {1}\n"
                            "   WIN COUNT:            {2}\n"
                            "   AGENT WIN PERCENTAGE: {3}%".format(
                today.strftime("%d/%m/%Y %H:%M"),
                winCount,
                (float(winCount[player.seatNumber]) / games) * 100.0))

except Exception():

    if clientProcess:
        clientProcess.wait()
    if robot1Process:
        robot1Process.wait()
    if robot2Process:
        robot2Process.wait()
    if robot3Process:
        robot3Process.wait()
    if serverProcess:
        serverProcess.wait()

    os.killpg(os.getpgid(clientProcess.pid), signal.SIGTERM)
    os.killpg(os.getpgid(robot1Process.pid), signal.SIGTERM)
    os.killpg(os.getpgid(robot2Process.pid), signal.SIGTERM)
    os.killpg(os.getpgid(robot3Process.pid), signal.SIGTERM)
    os.killpg(os.getpgid(serverProcess.pid), signal.SIGTERM)

    print(serverProcess.returncode)