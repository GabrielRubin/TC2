from TC2Main import *

m_clientPath = os.getcwd()
m_totalGames = 5

def RunMain(gameNamePrefix):

    main = TC2Main()

    main.InitGame(canInitServer=False, gameNamePrefix=gameNamePrefix, callProcess=(gameNamePrefix == 1))

    time.sleep(2)

    gameState = main.RunClient(killProcess=(gameNamePrefix == m_totalGames))

    os.chdir(m_clientPath)

    main.SaveGameStats(gameState)

if __name__ == '__main__':

    os.chdir("..")
    # print("changing to folder "+os.path.join(os.getcwd(), "JSettlers-1.0.6"))
    # os.chdir("\""+os.path.join(os.getcwd(), "JSettlers-1.0.6")+"\"")
    # The line above does not seem to work in my computer because of spaces or quotes
    os.chdir('JSettlers-1.0.6')

    serverProcess = subprocess.Popen("java -jar JSettlersServer.jar 8880 10 dbUser dbPass",
                                 shell=False, stdout=subprocess.PIPE)

    for i in range(0, m_totalGames):
        RunMain((i+1))