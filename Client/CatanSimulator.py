from Client import *
import logging

boardLayoutMessage = "1014|TestGame,9,6,10,6,6,1,3,3,67,8,3,5,4,1," \
                     "6,6,2,0,2,3,4,85,8,4,5,1,5,6,6,2,4,5,97,18,6," \
                     "100,6,-1,-1,-1,-1,-1,8,9,6,-1,-1,2,1,4,7,-1,-1," \
                     "5,-1,8,3,5,-1,-1,7,6,2,1,-1,-1,3,0,4,-1,-1,-1,-1,-1,85"

def runGame():

    game = Game(GameState())

    game.AddPlayer(AgentAlphabeta("P1", 0), 0)
    game.AddPlayer(AgentRandom("P2", 1), 1)
    game.AddPlayer(AgentRandom("P3", 2), 2)
    game.AddPlayer(AgentRandom("P4", 3), 3)

    startingPlayer = random.randint(0, 3)

    game.gameState.startingPlayer = startingPlayer
    game.gameState.currPlayer     = startingPlayer

    game.gameState.currState = "START1A"

    game.CreateBoard(BoardLayoutMessage.parse(boardLayoutMessage))

    logging.getLogger().setLevel(logging.CRITICAL)

    while True:

        currPlayer     = game.gameState.players[game.gameState.currPlayer]

        agentAction    = currPlayer.DoMove(game)

        agentAction.ApplyAction(game.gameState)

        if game.gameState.currState == "OVER":

            print("GAME OVER!")

            logging.critical("Game Over! Player {0} Wins!".format(game.gameState.players[game.gameState.winner].name))

            logging.critical("GAME STATS:")

            for i in range(0, 4):

                logging.critical("Player {0} stats:".format(game.gameState.players[i].name))

                logging.critical("his resources are: "
                              "\n RESOURCES = {0} "
                              "\n PIECES    = {1} "
                              "\n KNIGHTS   = {2} ".format(
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

            break

if __name__ == '__main__':

    runGame()

    # import timeit
    #
    # timer = timeit.Timer("runGame()", setup="from __main__ import runGame")
    #
    # print(timer.timeit(300))

    #print(min(timer.repeat(10, 30)))