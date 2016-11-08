#from Client import *
import GameStateViewer
#import logging
import datetime
import cProfile
import pstats
import timeit
import os.path
import socket
from AgentMCTS import AgentMCTS
import cPickle
from CatanGame import *
from AgentRandom import *
from joblib import Parallel, delayed
import multiprocessing
import CSVGenerator

boardLayoutMessage = "1014|TestGame,9,6,10,6,6,1,3,3,67,8,3,5,4,1," \
                     "6,6,2,0,2,3,4,85,8,4,5,1,5,6,6,2,4,5,97,18,6," \
                     "100,6,-1,-1,-1,-1,-1,8,9,6,-1,-1,2,1,4,7,-1,-1," \
                     "5,-1,8,3,5,-1,-1,7,6,2,1,-1,-1,3,0,4,-1,-1,-1,-1,-1,85"

defaultPlayers = [AgentMCTS("P1", 0, simulationCount=1000),
                  AgentRandom("P2", 1),
                  AgentRandom("P3", 2),
                  AgentRandom("P4", 3)]

#defaultPlayers = [AgentRandom("P1", 0),
#                  AgentRandom("P2", 1),
#                  AgentRandom("P3", 2),
#                  AgentRandom("P4", 3)]

def CreateGame(players):

    game = Game(GameState())

    for player in players:
        game.AddPlayer(player, player.seatNumber)

    game.gameState.players = game.gameState.players[:len(players)]

    startingPlayer = random.randint(0, len(players)-1)

    game.gameState.startingPlayer = startingPlayer
    game.gameState.currPlayer     = startingPlayer

    game.gameState.currState = "START1A"

    game.CreateBoard(BoardLayoutMessage.parse(boardLayoutMessage))

    return game

defaultGame = CreateGame(defaultPlayers)

def RunSingleGame(game):

    #game = copy.deepcopy(game)

    game = cPickle.loads(cPickle.dumps(game, -1))

    while True:

        currPlayer  = game.gameState.players[game.gameState.currPlayer]

        agentAction = currPlayer.DoMove(game)

        if agentAction is None:
            print(game.gameState.currState)

        if isinstance(agentAction, list):
            for action in agentAction:
                action.ApplyAction(game.gameState)
        else:
            agentAction.ApplyAction(game.gameState)

        if game.gameState.currState == "OVER":
        #if game.gameState.setupDone:
            return game

def RunGame(inGame = None, players = None, saveImgLog = False, showLog = False, showFullLog = False, returnLog=False):

    if players is None:
        players = copy.deepcopy(defaultPlayers)

    if inGame is None:
        inGame = CreateGame(players)

    start = datetime.datetime.utcnow()

    #test = RunSingleGame(inGame)
    game = RunSingleGame(inGame)

    now   = datetime.datetime.today()

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

def RunParallel(game, index, numberOfRepetitions, fileName):

    result = RunGame(game, game.gameState.players, showLog=False, returnLog=True)

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

if __name__ == '__main__':

    # for i in range(0, 25):
    #     RunGame(saveImgLog=True)

    #RunGame(showLog=True)

    # for i in range(0, 10):
    #     RunGame(defaultPlayers)
    #
    #     print(" --- GAME : {0} --- ".format(datetime.datetime.utcnow()))

    # RUN WITH LOGGING
    RunWithLogging(10, saveGameStateLogs=False, multiprocess=True)

    # SPEED TEST
    #RunSpeedTest(300)

    # SIMULATOR PROFILER
    #RunProfiler()