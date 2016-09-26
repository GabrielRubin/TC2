import subprocess
import os
import time
import argparse

from Client import *
from AgentRandom import *

AgentTypes = { 'rand' : 'random', 'min' : 'minimax', 'exp' : 'expectimax', 'mcts' : 'monte carlo tree search'}

LogType    = { 'i' : 'info', 'd' : 'debug' }

serverProcess = None
robot1Process = None
robot2Process = None
robot3Process = None
clientProcess = None

parser = argparse.ArgumentParser()

parser.add_argument("-at", "--agentType", help="choose one of these types of agent: {0}".format(AgentTypes),
                    default = 'rand')

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

if args.noGame:
    ourClient = Client("TestGame", player, False, True)
else:
    ourClient = Client("TestGame", player, True, True)


# Give some time so the server can start and the robots get in....
time.sleep(2)

try:
    ourClient.StartClient(("localhost", 8880))

except Exception():

    if clientProcess:
        clientProcess.wait()
        clientProcess.kill()
    if robot1Process:
        robot1Process.wait()
        robot1Process.kill()
    if robot2Process:
        robot2Process.wait()
        robot2Process.kill()
    if robot3Process:
        robot3Process.wait()
        robot3Process.kill()
    if serverProcess:
        serverProcess.wait()
        serverProcess.kill()

    print(serverProcess.returncode)