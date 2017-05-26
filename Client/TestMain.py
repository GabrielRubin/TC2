from TC2Main import *

m_totalGames = 100

def RunMain(gameNamePrefix, serverType = ""):

    main = TC2Main(serverType=serverType)

    main.InitGame(canInitServer=False, gameNamePrefix=gameNamePrefix, callProcess=False)

    time.sleep(2)

    gameState = main.RunClient(killProcess=False)

if __name__ == '__main__':

    os.chdir("..")
    # print("changing to folder "+os.path.join(os.getcwd(), "JSettlers-1.0.6"))
    # os.chdir("\""+os.path.join(os.getcwd(), "JSettlers-1.0.6")+"\"")
    # The line above does not seem to work in my computer because of spaces or quotes
    os.chdir('JSettlers-1.0.6')

    #serverType = "" #default server
    serverType = "_noTimeout" #no timeout server
    #serverType = "_perfectInfo" #perfect information and no timeout server

    serverProcess = subprocess.Popen("java -jar JSettlersServer{0}.jar 8880 10 dbUser dbPass".format(serverType),
                                 shell=False, stdout=subprocess.PIPE)
    robot1Process = subprocess.Popen(
        "java -cp JSettlersServer{0}.jar soc.robot.SOCRobotClient localhost 8880 robot1 passwd".format(serverType),
        shell=True, stdout=subprocess.PIPE)

    robot2Process = subprocess.Popen(
        "java -cp JSettlersServer{0}.jar soc.robot.SOCRobotClient localhost 8880 robot2 passwd".format(serverType),
        shell=True, stdout=subprocess.PIPE)

    robot3Process = subprocess.Popen(
        "java -cp JSettlersServer{0}.jar soc.robot.SOCRobotClient localhost 8880 robot3 passwd".format(serverType),
        shell=True, stdout=subprocess.PIPE)

    clientProcess = subprocess.Popen("java -jar JSettlers.jar localhost 8880")

    for i in range(0, m_totalGames):
        RunMain((i+1), serverType=serverType)

    clientProcess.kill()
    robot1Process.kill()
    robot2Process.kill()
    robot3Process.kill()