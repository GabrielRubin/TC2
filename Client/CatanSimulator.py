import GameStateViewer
import copy
import cProfile
import pstats
import timeit
import time
import os.path
import socket
from CatanGame import *
from AgentRandom import *
from joblib import Parallel, delayed
import multiprocessing
import CSVGenerator

# -- ML STUFF --
import sklearn
#SGD = Stochastic Gradient Descent
from sklearn.linear_model import SGDRegressor
from GameDataExplorer import GetGameTrainingDataFrame

#Suggested Board from Catan's Rules Book
suggestedBoard    = "1014|TestGame,7,6,20,6,6,2,3,5,34,53,4,1,3,1," \
                     "6,6,4,5,0,4,2,8,49,5,2,4,3,6,6,1,4,3,67,9,6," \
                     "10,6,-1,-1,-1,-1,-1,7,0,6,-1,-1,9,4,2,7,-1,-1," \
                     "6,8,-1,1,5,-1,-1,5,1,2,3,-1,-1,3,4,8,-1,-1,-1,-1,-1,85"

# defaultPlayers = [AgentUCT("P1", 0, simulationCount=1000),
#                   AgentRandom("P2", 1),
#                   AgentRandom("P3", 2),
#                   AgentRandom("P4", 3)]

# defaultPlayers = [AgentMCTS("P1", 0, simulationCount=1000, preSelect=False),
#                   AgentRandom("P2", 1),
#                   AgentRandom("P3", 2),
#                   AgentRandom("P4", 3)]

defaultPlayers = [AgentRandom("P1", 0),
                  AgentRandom("P2", 1),
                  AgentRandom("P3", 2),
                  AgentRandom("P4", 3)]

modelVersusRandomPlayers = [AgentRandom("P1", 0, useModel=True),
                            AgentRandom("P4", 3),
                            AgentRandom("P2", 1),
                            AgentRandom("P3", 2)]

def CreateNewBoard():
    """
    New board code based on the original JSettlers board generation code.
    (JSettler's SOCBoard.java -> makeNewBoard() method)
    """
    desert = 0
    brick  = 1
    ore    = 2
    wool   = 3
    grain  = 4
    lumber = 5

    hexLayout = [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6] # all sea

    numberLayout = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

    robberPos = 0

    landHexes = [desert, brick, brick, brick, ore, ore, ore, wool, wool, wool, wool,
                 grain, grain, grain, grain, lumber, lumber, lumber, lumber]

    portHexes = [0, 0, 0, 0, brick, ore, wool, grain, lumber] # 0 = 3 to 1

    numbers = [3, 0, 4, 1, 5, 7, 6, 9, 8, 2, 5, 7, 6, 2, 3, 4, 1, 8]

    numPath = [29, 30, 31, 26, 20, 13, 7, 6, 5, 10, 16, 23, 24, 25, 19, 12, 11, 17, 18]

    random.shuffle(landHexes)

    cnt = 0
    for n in range(0, len(landHexes)):

        hexLayout[numPath[n]] = landHexes[n]
        if landHexes[n] == 0:
            robberPos = g_boardHexes[numPath[n]]
            numberLayout[numPath[n]] = -1
        else:
            numberLayout[numPath[n]] = numbers[cnt]
            cnt += 1

    random.shuffle(portHexes)

    def PlacePort(port, he, face):
        if port == 0:
            hexLayout[he] = face + 6
        else:
            hexLayout[he] = (face << 4) + port

    PlacePort(portHexes[0], 0, 3)
    PlacePort(portHexes[1], 2, 4)
    PlacePort(portHexes[2], 8, 4)
    PlacePort(portHexes[3], 9, 2)
    PlacePort(portHexes[4], 21, 5)
    PlacePort(portHexes[5], 22, 2)
    PlacePort(portHexes[6], 32, 6)
    PlacePort(portHexes[7], 33, 1)
    PlacePort(portHexes[8], 35, 6)

    resultString = "1014|TestGame,"
    for h in hexLayout:
        resultString += "{0},".format(h)
    for n in numberLayout:
        resultString += "{0},".format(n)
    resultString += "{0}".format(robberPos)

    return resultString

def CreateGame(players, recordData = False, customBoard = None):

    game = Game(GameState())

    for player in players:
        game.AddPlayer(player, player.seatNumber)

    game.gameState.players = game.gameState.players[:len(players)]

    startingPlayer = random.randint(0, len(players)-1)

    game.gameState.startingPlayer = startingPlayer
    game.gameState.currPlayer     = startingPlayer

    game.gameState.currState = "START1A"

    if customBoard is None:
        newBoard = CreateNewBoard()
    else:
        newBoard = customBoard

    game.recordData           = recordData
    game.gameData.boardConfig = newBoard

    game.CreateBoard(BoardLayoutMessage.parse(newBoard))

    return game

defaultGame = CreateGame(defaultPlayers)

def RunSingleGame(game):

    game = cPickle.loads(cPickle.dumps(game, -1))

    while True:

        currPlayer  = game.gameState.players[game.gameState.currPlayer]

        agentAction = currPlayer.DoMove(game)

        if agentAction is None:
            print(game.gameState.currState)

        if isinstance(agentAction, list):
            for action in agentAction:
                if game.recordData:
                    #cPickle.load(cPickle.dump(game.gameState, cPickle.HIGHEST_PROTOCOL)
                    game.gameData.AddRecord(action, game.gameState)
                action.ApplyAction(game.gameState)
        else:
            if game.recordData:
                game.gameData.AddRecord(agentAction, game.gameState)
            agentAction.ApplyAction(game.gameState)

        if game.gameState.currState == "OVER":
            game.gameData.AddRecord(agentAction, game.gameState)
            return game

def RunGame(inGame = None, players = None, saveImgLog = False, showLog = False, showFullLog = False, returnLog=False, saveCSV=False):

    if players is None:
        players = copy.deepcopy(defaultPlayers)

    if inGame is None:
        inGame = CreateGame(players)

    start = datetime.datetime.utcnow()

    #test = RunSingleGame(inGame)
    game = RunSingleGame(inGame)

    if game.recordData:
        game.gameData.SaveRecord("GameData", "CatanData")

    if saveCSV:
        CSVGenerator.SaveGameStatsCSV(game.gameState)

    now = datetime.datetime.today()

    if saveImgLog:

        if not os.path.isdir("GameStates"):
            os.makedirs("GameStates")

        currGameStateName = "board_" + now.strftime("%d-%m-%Y_%H-%M-%S-%f")

        #gameStateFile = logging.FileHandler('GameStates/{0}.txt'.format(currGameStateName))

        #logging.getLogger().addHandler(gameStateFile)

        # Store the last GameState
        with open('GameStates/{0}.pickle'.format(currGameStateName), 'wb') as handle:
            cPickle.dump(game.gameState, handle, protocol=cPickle.HIGHEST_PROTOCOL)

        GameStateViewer.SaveGameStateImage(game.gameState, 'GameStates/{0}.png'.format(currGameStateName))

    if showLog:

        logging.critical("#########################################################")

        logging.critical("Game Over! Player {0} Wins!".format(game.gameState.players[game.gameState.winner].name))

        logging.critical("GAME STATS:")

        logging.critical(" total turns: {0} \n starting player: {1} \n largest army player: {2} \n longest road player: {3} ".format(
            game.gameState.currTurn,
            game.gameState.startingPlayer,
            game.gameState.largestArmyPlayer,
            game.gameState.longestRoadPlayer
        ))

        logging.critical("#########################################################")

        if showFullLog:

            for i in range(0, len(game.gameState.players)):

                logging.critical("Player {0} stats:".format(game.gameState.players[i].name))

                logging.critical("Player {0} is a {1} agent".format(game.gameState.players[i].name,
                                                                    game.gameState.players[i].agentName))

                logging.critical("his resources are: "
                              "\n POINTS          = {0} "
                              "\n LARGEST ARMY    = {1} "
                              "\n LONGEST ROAD    = {2} "
                              "\n RESOURCES       = {3} "
                              "\n PIECES          = {4} "
                              "\n KNIGHTS         = {5} "
                              "\n DICE PRODUCTION = {6}".format(
                    game.gameState.players[i].GetVictoryPoints(),
                    game.gameState.players[i].biggestArmy,
                    game.gameState.players[i].biggestRoad,
                    game.gameState.players[i].resources,
                    game.gameState.players[i].numberOfPieces,
                    game.gameState.players[i].knights,
                    game.gameState.players[i].diceProduction
                ))

                devCards = ""

                for j in range(0, len(g_developmentCards)):

                    devCards += " {0} : {1}".format(
                        g_developmentCards[j], game.gameState.players[i].developmentCards[j]
                    )

                logging.critical(" DevCards : {0}".format(devCards))

                logging.critical(" Roads: {0}\n Settlements: {1}\n Cities: {2}".format(
                    [hex(road) for road in game.gameState.players[i].roads],
                    [hex(settlement) for settlement in game.gameState.players[i].settlements],
                    [hex(city) for city in game.gameState.players[i].cities]
                ))

                logging.critical("---------------------------------------------------------")

    # if saveImgLog:
    #     logging.getLogger().removeHandler(gameStateFile)

    if returnLog:

        playerPoints = [0 for i in range(len(game.gameState.players))]
        for player in game.gameState.players:
            playerPoints[player.seatNumber] = player.GetVictoryPoints()

        # @REVIEW:
        ourAgent = game.gameState.players[0]

        totalDiceProduction = listm([0, 0, 0, 0, 0, 0])
        for key, value in ourAgent.diceProduction.iteritems():
            totalDiceProduction += value

        logstr = "######################################################### \n " \
                 "Game Over! Player {0} Wins!\nGAME STATS:\n" \
                 " game time: {1}\n total turns: {2} \n starting player: {3}\n" \
                 " largest army player: {4} \n longest road player: {5} "\
                 " MORE STATS :          \n" \
                 " playerPoints     = {6}\n" \
                 " roadsBuilt       = {7}\n" \
                 " settlementsBuilt = {8}\n" \
                 " citiesBuilt      = {9}\n" \
                 " cardsBought      = {10}\n" \
                 " diceProduction   = {11}\n" \
                 " knights          = {12}\n".format(
            game.gameState.players[game.gameState.winner].name,
            ((datetime.datetime.utcnow() - start).total_seconds() / 60.0),
            game.gameState.currTurn,
            game.gameState.startingPlayer,
            game.gameState.largestArmyPlayer,
            game.gameState.longestRoadPlayer,
            playerPoints,
            [hex(road) for road in ourAgent.roads],
            [hex(settlement) for settlement in ourAgent.settlements],
            [hex(city) for city in ourAgent.cities],
            "TODO",
            totalDiceProduction,
            ourAgent.knights
        )

        logging.critical("#########################################################")

        currGameStateName = "board_" + now.strftime("%d-%m-%Y_%H-%M-%S-%f")

        # Review:
        with open('GameStates/{0}.pickle'.format(currGameStateName), 'wb') as handle:
            cPickle.dump(game.gameState, handle, protocol=cPickle.HIGHEST_PROTOCOL)

        return game.gameState.winner, logstr

    return game.gameState.winner

def RunProfiler():

    logger = logging.getLogger()

    logger.disabled = True

    cProfile.run('RunSingleGame(defaultGame)', 'simulatorStats')

    p = pstats.Stats('simulatorStats')

    p.sort_stats('cumulative').print_stats(30)

    p.sort_stats('time').print_stats(30)

def RunSpeedTest(numberOfRepetitions):

    logger = logging.getLogger()

    logger.disabled = True

    today = datetime.datetime.today()

    timer = timeit.Timer("RunSingleGame(defaultGame)", setup="from __main__ import RunSingleGame, defaultGame")

    speedResults = timer.repeat(numberOfRepetitions, 1)

    if os.path.isfile("SimulatorLogs/SpeedResults.txt"):

        with open("SimulatorLogs/SpeedResults.txt", "a") as text_file:
            text_file.write("\n{0} - {1} >> Best Case: {2}s, Worst Case: {3}s, Average: {4}s".format(
                socket.gethostname(),
                today.strftime("%d/%m/%Y %H:%M"), round(min(speedResults), 4),
                round(max(speedResults), 4), round(sum(speedResults)/numberOfRepetitions, 4)))
    else:

        with open("SimulatorLogs/SpeedResults.txt", "w") as text_file:
            text_file.write("{0} {1} >> Best Case: {2}s, Worst Case: {3}s, Average: {4}s".format(
                socket.gethostname(),
                today.strftime("%d/%m/%Y %H:%M"), round(min(speedResults), 4),
                round(max(speedResults), 4), round(sum(speedResults)/numberOfRepetitions, 4)))

def RunParallel(game, index, numberOfRepetitions, fileName = None, saveCSV = False):

    result = RunGame(game, game.gameState.players, showLog=False, returnLog=True, saveCSV=saveCSV)

    if fileName is not None:

        print("\n TOTAL GAMES = {0}/{1} ".format(
            (index + 1),
            numberOfRepetitions))

        if os.path.isfile(fileName):

            with open(fileName, "a") as text_file:
                text_file.write("\n"+result[1])
        else:

            with open(fileName, "w") as text_file:
                text_file.write(result[1])

    return result[0]

def RunWithLogging(numberOfRepetitions, players = None, saveGameStateLogs = False, agentIndex = 0, multiprocess = False):

    if players is None:
        players = defaultPlayers

    logger = logging.getLogger()

    today = datetime.datetime.today()

    fileName            = 'SimulatorLogs/log_{0}.txt'.format(today.strftime("%d-%m-%Y_%H-%M"))
    fileNameSimulations = 'SimulatorLogs/logSim_{0}.txt'.format(today.strftime("%d-%m-%Y_%H-%M"))

    logFile = logging.FileHandler(fileName)

    logger.addHandler(logFile)

    winCount = [0, 0, 0, 0]

    totalTime = datetime.datetime.utcnow()

    if multiprocess:
        num_cores = multiprocessing.cpu_count()

        winners   = Parallel(n_jobs=num_cores)(delayed(RunParallel)
                                               (CreateGame(players), i, numberOfRepetitions, fileNameSimulations)
                                               for i in range(0, numberOfRepetitions))

        winCount  = [winners.count(0), winners.count(1), winners.count(2), winners.count(3)]

    else:

        games = [CreateGame(players) for i in range(numberOfRepetitions)]

        for i in range(0, numberOfRepetitions):

            time = datetime.datetime.utcnow()

            winner = RunGame(games[i], games[i].gameState.players, showLog=True, showFullLog=False, saveImgLog=saveGameStateLogs)

            logging.critical("\n GAME TIME = {0}".format(((datetime.datetime.utcnow() - time).total_seconds())))

            winCount[winner] += 1

            total = "\n TOTAL GAMES = {0}/{1} ".format(
                (i + 1),
                numberOfRepetitions)

            print(total)

            logging.critical(total)

    logging.critical("\n TOTAL TIME = {0}".format(((datetime.datetime.utcnow() - totalTime).total_seconds())/60.0))

    logging.critical(" TOTAL GAMES = {0} \n WIN COUNT = {1} \n AGENT WIN PERCENTAGE = {2}%".format(
        numberOfRepetitions,
        winCount,
        (float(winCount[agentIndex]) / numberOfRepetitions) * 100.0
    ))

def RunWithCSVSaving(numberOfRepetitions, players = None, multiprocess = False):
    if players is None:
        players = defaultPlayers

    if multiprocess:
        num_cores = multiprocessing.cpu_count()

        Parallel(n_jobs=num_cores)(delayed(RunParallel)
                (CreateGame(players), i, numberOfRepetitions, saveCSV=True)
                 for i in range(0, numberOfRepetitions))
    else:
        games = [CreateGame(players) for i in range(numberOfRepetitions)]
        for i in range(0, numberOfRepetitions):
            RunGame(games[i], games[i].gameState.players, saveCSV=True)

#Online Training
def RunModelTraining(numberOfTrainings, modelName, loadModel = None, customBoard = None):

    model = None

    if loadModel is not None:
        with open('Models/{0}.mod'.format(loadModel), 'rb') as handle:
            model = cPickle.load(handle)
    else:
        model = SGDRegressor()

    start_time = time.time()

    for i in range(0, numberOfTrainings):
        gameResult = RunSingleGame(CreateGame(copy.deepcopy(defaultPlayers),
                                              customBoard=customBoard,
                                              recordData=True))

        X, Y = GetGameTrainingDataFrame(gameResult.gameData)

        model.partial_fit(X, Y)

        elapsed_time = time.time() - start_time

        logging.critical("PROGRESS = {1}%\n"        
                         "TIME ELAPSED = {2}".format(i, float(i+1)/numberOfTrainings * 100,
                                                     time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))

    logging.critical("TRAINING DONE!\n" \
                     "SAVING AT 'Models/{0}.mod'".format(modelName))

    with open("Models/{0}.mod".format(modelName), 'wb') as handle:
        cPickle.dump(model, handle, protocol=cPickle.HIGHEST_PROTOCOL)

#Model Testing
def RunModelTesting(numberOfTests, loadModel, customBoard = None):

    with open('Models/{0}.mod'.format(loadModel), 'rb') as handle:
        model = cPickle.load(handle)

    start_time = time.time()

    for i in range(0, numberOfTests):
        gameResult = RunSingleGame(CreateGame(copy.deepcopy(defaultPlayers),
                                              customBoard=customBoard,
                                              recordData=True))

        X, Y = GetGameTrainingDataFrame(gameResult.gameData)

        Y_pred = model.predict(X)
        score  = sklearn.metrics.r2_score(Y, Y_pred)

        elapsed_time = time.time() - start_time

        logging.critical("SCORE = {0}\n"
                         "PROGRESS = {1}%\n"
                         "TIME ELAPSED = {2}".format(score, float(i + 1) / numberOfTests * 100,
                                                     time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))

if __name__ == '__main__':

    RunModelTraining(numberOfTrainings=20000, modelName="Test07")
    #RunModelTesting(numberOfTests=20, loadModel="Test06")

    #for i in range(0, 500):
    #    RunGame(saveImgLog=False)

    #RunGame(saveImgLog=False, showLog=True)

    # for i in range(0, 10):
    #     RunGame(defaultPlayers)
    #
    #     print(" --- GAME : {0} --- ".format(datetime.datetime.utcnow()))

    # RUN WITH LOGGING
    #RunWithLogging(300, saveGameStateLogs=False, multiprocess=True, players=defaultPlayers)

    #RunWithCSVSaving(1000, multiprocess=False)

    # SPEED TEST
    #RunSpeedTest(50)

    # SIMULATOR PROFILER
    #RunProfiler()