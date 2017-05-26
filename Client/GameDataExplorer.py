from CatanGame import *
import numpy as np
import glob
import cPickle
from tkFileDialog import askopenfilename
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

class MyDataFile():

    def __init__(self, data, target, featureNames):
        self.data = data
        self.target = target
        self.featureNames = featureNames

allGameData = []

def OpenAllSaveData(path):

    files = glob.glob("{0}/*.ctndt".format(path))
    for f in files:
        try:
            with open('{0}'.format(f), 'rb') as handle:
                allGameData.append(cPickle.load(handle))
        except EOFError as exc:
            print(exc)

def SaveAllSavedDataAsTXT(path, fileName):

    recordStr = ""
    currGameIndex = 1
    for data in allGameData:
        recordStr += "------ Game {0} ------\n".format(currGameIndex)
        recordStr += "BOARD = " + data.boardConfig
        for turnRecord in data.turnData:
            content = "{0}/{1}".format(turnRecord.gameState.turn, type(turnRecord.action).__name__)
            recordStr += "{0}\n".format(content)
        recordStr += "+++++++++++++++++++++\n"
        currGameIndex += 1

    with open("{0}/{1}.txt".format(path, fileName), 'wb') as file:
        file.write(recordStr)

def SaveAllDataAsCSV(path, fileName):

    import csv
    with open("{0}/{1}.csv".format(path, fileName), 'w') as csv_file:

        headers  = GetHeaders(allGameData[0])
        examples = GetExamplesSize(allGameData)
        fileHeader = [examples,len(headers)] + headers + ['target']
        csvWriter = csv.writer(csv_file, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

        csvWriter.writerow(fileHeader)
        for data in allGameData:
            hexes, numbers = data.GetBoardTerrainAndNumbers()
            for turnRecord in data.turnData:

                csvWriter.writerow(hexes + numbers +
                                   [data.startingPlayer] +
                                   ComposeTurnCSVLine(turnRecord) +
                                   [ComposeTargetData(data)])


def ComposeTurnCSVLine(turnRecord):

    gameState = turnRecord.gameState

    rowData = [gameState.turn,
               #gameState.currState,
               gameState.currPlayer,
               gameState.longestRoadPlayer,
               gameState.largestArmyPlayer,
               sum(gameState.developmentCardsDeck)]

    rowData += gameState.boardNodes
    rowData += gameState.boardEdges

    for player in turnRecord.players:
        rowData += ComposePlayerCSVLine(player)

    return rowData

def ComposePlayerCSVLine(player):

    data = [#player.agentName,
            player.seatNumber,
            sum(player.resources),
            player.knights,
            player.victoryPoints]

    data += player.numberOfPieces
    data += player.developmentCards

    return data

def GetHeaders(gameData):

    hexes, numbers = gameData.GetBoardTerrainAndNumbers()

    h = ["hex{0}".format(n) for n in range(1, len(hexes) + 1)]
    numbers = ["n{0}".format(n) for n in range(1, len(numbers) + 1)]

    bN = ["bNode{0}".format(n) for n in range(1, len(gameData.turnData[0].gameState.boardNodes) + 1)]
    bE = ["bEdge{0}".format(n) for n in range(1, len(gameData.turnData[0].gameState.boardEdges) + 1)]

    pData = []
    i = 1
    for player in gameData.turnData[0].players:
        pieces = ["P{0}_piece{1}".format(i, n) for n in range(1, len(player.numberOfPieces) + 1)]
        devs   = ["P{0}_devC{1}".format(i, n) for n in range(1, len(player.developmentCards) + 1)]
        pData += [#"P{0}_agent".format(i),
                  "P{0}_seat".format(i),
                  "P{0}_resources".format(i),
                  "P{0}_knights".format(i),
                  "P{0}_vp".format(i)] + pieces + devs
        i += 1

    return h + numbers + ["sPlayer",
            "turn", #"state",
            "player",
            "lgRoads", "lgArmy", "dvCards"] + \
            bN + bE + pData

def GetExamplesSize(allData):

    i = 0
    for data in allData:
        i += len(data.turnData)
    return i

def ComposeTargetData(gameData):

    return gameData.turnData[-1].players[0].victoryPoints

def GetGameTrainingDataFrame(gameData):

    headers    = GetHeaders(gameData)
    n_samples  = len(gameData.turnData)
    n_features = len(headers)
    hexes, numbers = gameData.GetBoardTerrainAndNumbers()

    data   = np.empty((n_samples, n_features))
    target = np.empty((n_samples,), dtype=np.int)
    for i, turnData in enumerate(gameData.turnData):
        entry = hexes + numbers + [gameData.startingPlayer] + ComposeTurnCSVLine(turnData)
        tgt   = [ComposeTargetData(gameData)]
        data[i]   = np.asarray(entry, dtype=np.float64)
        target[i] = np.asarray(tgt, dtype=np.int)

    dataFile = MyDataFile(data=data, target=target, featureNames=headers)

    dataFrame = pd.DataFrame(dataFile.data)
    dataFrame.columns = dataFile.featureNames
    dataFrame['TargetVP'] = dataFile.target

    X = dataFrame.drop('TargetVP', axis = 1)
    Y = dataFrame['TargetVP']

    return X, Y

def GetGameStateDataFrame(gameState, action, boardConfig):

    gameData = GameData()
    gameData.boardConfig = boardConfig
    gameData.AddRecord(action, gameState)
    hexes, numbers = gameData.GetBoardTerrainAndNumbers()
    entry = hexes + numbers + [gameData.startingPlayer] + ComposeTurnCSVLine(gameData.turnData[0])
    data = np.empty((1, len(entry)))
    data[0] = np.asarray(entry, dtype=np.float64)
    dataFrame = pd.DataFrame(data)
    return dataFrame

if __name__ == '__main__':

    OpenAllSaveData("GameData")
    SaveAllDataAsCSV("GameData", "allCSVData")