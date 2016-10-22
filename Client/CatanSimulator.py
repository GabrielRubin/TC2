from Client import *
import logging
import pickle
import datetime
import GameStateViewer
import cProfile
import pstats
import timeit
import os.path
import socket
from AgentMCTS import AgentMCTS

boardLayoutMessage = "1014|TestGame,9,6,10,6,6,1,3,3,67,8,3,5,4,1," \
                     "6,6,2,0,2,3,4,85,8,4,5,1,5,6,6,2,4,5,97,18,6," \
                     "100,6,-1,-1,-1,-1,-1,8,9,6,-1,-1,2,1,4,7,-1,-1," \
                     "5,-1,8,3,5,-1,-1,7,6,2,1,-1,-1,3,0,4,-1,-1,-1,-1,-1,85"

players = [AgentRandom("P1", 0),
           AgentRandom("P2", 1),
           AgentRandom("P3", 2),
           AgentRandom("P4", 3)]

def RunGame(saveLog = False):

    game = Game(GameState())

    for player in players:

        copyPlayer = copy.deepcopy(player)

        game.AddPlayer(copyPlayer, copyPlayer.seatNumber)

    game.gameState.players = game.gameState.players[:len(players)]

    startingPlayer = random.randint(0, len(players)-1)

    game.gameState.startingPlayer = startingPlayer
    game.gameState.currPlayer     = startingPlayer

    game.gameState.currState = "START1A"

    game.CreateBoard(BoardLayoutMessage.parse(boardLayoutMessage))

    while True:

        currPlayer     = game.gameState.players[game.gameState.currPlayer]

        agentAction    = currPlayer.DoMove(game)

        if agentAction is None:
            print(game.gameState.currState)

        if isinstance(agentAction, list):
            for action in agentAction:
                action.ApplyAction(game.gameState)
        else:
            agentAction.ApplyAction(game.gameState)

        if game.gameState.currState == "OVER":

            #print("--------------GAME!---------------")

            if saveLog:

                now = datetime.datetime.today()

                currGameStateName = "board_" + now.strftime("%d-%m-%Y_%H-%M-%S-%f")

                gameStateFile = logging.FileHandler('GameStates/{0}.txt'.format(currGameStateName))

                logging.getLogger().addHandler(gameStateFile)

                # Store the last GameState
                with open('GameStates/{0}.pickle'.format(currGameStateName), 'wb') as handle:
                    pickle.dump(game.gameState, handle, protocol=pickle.HIGHEST_PROTOCOL)

                GameStateViewer.SaveGameStateImage(game.gameState, 'GameStates/{0}.png'.format(currGameStateName))

            logging.critical("#########################################################")

            logging.critical("Game Over! Player {0} Wins!".format(game.gameState.players[game.gameState.winner].name))

            logging.critical("GAME STATS:")

            logging.critical(" largest army player: {0} \n longest road player: {1} ".format(
                game.gameState.largestArmyPlayer,
                game.gameState.longestRoadPlayer
            ))

            logging.critical("#########################################################")

            for i in range(0, len(game.gameState.players)):

                logging.critical("Player {0} stats:".format(game.gameState.players[i].name))

                logging.critical("Player {0} is a {1} agent".format(game.gameState.players[i].name,
                                                                    game.gameState.players[i].agentName))

                logging.critical("his resources are: "
                              "\n POINTS       = {0} "
                              "\n LARGEST ARMY = {1} "
                              "\n LONGEST ROAD = {2} "
                              "\n RESOURCES    = {3} "
                              "\n PIECES       = {4} "
                              "\n KNIGHTS      = {5} ".format(
                    game.gameState.players[i].GetVictoryPoints(),
                    game.gameState.players[i].biggestArmy,
                    game.gameState.players[i].biggestRoad,
                    game.gameState.players[i].resources,
                    game.gameState.players[i].numberOfPieces,
                    game.gameState.players[i].knights
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


            if saveLog:
                logging.getLogger().removeHandler(gameStateFile)

            break

def RunProfiler():

    logger = logging.getLogger()

    logger.disabled = True

    cProfile.run('RunGame()', 'simulatorStats')

    p = pstats.Stats('simulatorStats')

    p.sort_stats('cumulative').print_stats(10)

    p.sort_stats('time').print_stats(10)

def RunSpeedTest(numberOfRepetitions):

    logger = logging.getLogger()

    logger.disabled = True

    today = datetime.datetime.today()

    timer = timeit.Timer("RunGame()", setup="from __main__ import RunGame")

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

def RunWithLogging(numberOfRepetitions, saveGameStateLogs = False):

    logger = logging.getLogger()

    today = datetime.datetime.today()

    if saveGameStateLogs:
        timer = timeit.Timer("RunGame(True)", setup="from __main__ import RunGame")
    else:
        timer = timeit.Timer("RunGame()", setup="from __main__ import RunGame")

    logFile = logging.FileHandler('SimulatorLogs/log_{0}.txt'.format(today.strftime("%d-%m-%Y_%H-%M")))

    logger.addHandler(logFile)

    print(timer.timeit(numberOfRepetitions))

if __name__ == '__main__':

    RunGame()

    # RUN WITH LOGGING
    #RunWithLogging(10, saveGameStateLogs=True)

    # SPEED TEST
    #RunSpeedTest(300)

    # SIMULATOR PROFILER
    #RunProfiler()