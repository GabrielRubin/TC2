import numpy as np
import os

gameStatsColumns = [
                    ("Winner",       np.str_, 16),
                    ("Points",       np.str_, 16),
                    ("Turns",        np.int),
                    ("Agent Points", np.int),
                    ("Roads",        np.int),
                    ("Settlements",  np.int),
                    ("Cities",       np.int),
                    ("Knights",      np.int),
                    ("Largest Road", np.int),
                    ("Largest Army", np.int)
                   ]


def SaveGameStatsCSV(gameState):

  msg = ComposeGameStatsMessageCSV(gameState)

  WriteCSVFile("GamesStats", "GameStats", msg)

def ComposeGameStatsMessageCSV(gameState):

  playersPoints = "{0} | {1} | {2} | {3}".format(gameState.players[0].GetVictoryPoints(),
                                                 gameState.players[1].GetVictoryPoints(),
                                                 gameState.players[3].GetVictoryPoints(),
                                                 gameState.players[2].GetVictoryPoints())

  msg = [(gameState.players[gameState.winner].name,  # winner name
          playersPoints,
          gameState.currTurn,  # total turns
          gameState.players[0].GetVictoryPoints(),  # agent points
          len(gameState.players[0].roads),  # total roads
          len(gameState.players[0].settlements),  # total settlements
          len(gameState.players[0].cities),  # total cities
          gameState.players[0].knights,  # total knights
          gameState.players[0].biggestRoad,  # has the biggest road?
          gameState.players[0].biggestArmy)]  # has the biggest army?

  return msg

def WriteCSVFile(fileName, fileType, fileContent):

  filePath = "SimulatorLogs/" + fileName + ".csv"

  if fileType == "GameStats":

    arrayType = np.dtype(gameStatsColumns)

    grades = np.array(fileContent, dtype=arrayType)

    if os.path.isfile(filePath):

      with open(filePath, "a") as csv_file:
        np.savetxt(csv_file,
                   grades,
                   delimiter=',',
                   fmt=('%s', '%s', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u'),
                   comments='')
    else:

      with open(filePath, "w") as csv_file:
        np.savetxt(csv_file,
                   grades,
                   delimiter=',',
                   fmt=('%s', '%s', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u'),
                   comments='',
                   header='Winner, Points, Turns, Agent Points, Roads, Settlements, Cities, Knights, Largest Road, Largest Army')

    print ("---- CSV file generated in {0}! ----".format(filePath))


