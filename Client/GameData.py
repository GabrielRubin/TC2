from CatanGame import *

class PlayerRecord:

    def __init__(self, player):

        self.agentName        = player.agentName
        self.seatNumber       = player.seatNumber
        self.resources        = [r for r in player.resources]
        self.developmentCards = [c for c in player.developmentCards]
        self.roads            = [r for r in player.roads]
        self.settlements      = [s for s in player.settlements]
        self.cities           = [c for c in player.cities]
        self.biggestRoad      = player.biggestRoad
        self.biggestArmy      = player.biggestArmy
        self.numberOfPieces   = [n for n in player.numberOfPieces]
        self.knights          = player.knights
        self.tradeRates       = [n for n in player.tradeRates]
        self.victoryPoints    = player.victoryPoints

class GameStateRecord:

    def __init__(self, gameState):

        self.turn       = gameState.currTurn
        self.currState  = gameState.currState
        self.currPlayer = gameState.currPlayer
        self.robberPos  = gameState.robberPos

        self.boardNodes = [GameStateRecord.GetBoardNodeValue(gameState, node) for node in g_constructableNodes]
        self.boardEdges = [GameStateRecord.GetBoardEdgeValue(gameState, edge) for edge in g_constructableEdges]
        self.developmentCardsDeck = [n for n in gameState.developmentCardsDeck]

        self.longestRoadPlayer  = gameState.longestRoadPlayer
        self.largestArmyPlayer  = gameState.largestArmyPlayer

        self.setupDone      = gameState.setupDone
        self.winner         = gameState.winner
        self.isGameOver     = gameState.isGameOver

    @staticmethod
    def GetBoardNodeValue(gameState, node):

        for i in range(0, len(gameState.players)):
            if node in gameState.players[i].settlements or node in gameState.players[i].cities:
                return i
        return 0

    @staticmethod
    def GetBoardEdgeValue(gameState, edge):

        for i in range(0, len(gameState.players)):
            if edge in gameState.players[i].roads:
                return i
        return 0


class TurnRecord:

    def __init__(self, action, gameState):

        self.gameState = GameStateRecord(gameState)
        self.action    = action
        self.players   = [PlayerRecord(p) for p in gameState.players]

class GameData:

    VERSION = 1.0

    def __init__(self):

        self.boardConfig    = ""
        self.turnData       = []
        self.startingPlayer = -1
        self.winner         = 0
        self.version        = GameData.VERSION

    def AddRecord(self, action, gameState):

        self.turnData.append(TurnRecord(action, gameState))
        if self.startingPlayer == -1:
            self.startingPlayer = gameState.startingPlayer
        if gameState.winner >= 0:
            self.winner = gameState.winner + 1

    def GetBoardTerrainAndNumbers(self):

        data    = self.boardConfig.split(",")
        hexes   = map(int, data[1:38])
        numbers = map(int, data[38:38 + 37])

        numbers = [numbers[i] for i in range(0, len(numbers)) if hexes[i] < 6]
        hexes   = [h for h in hexes if h < 6]

        return hexes, numbers

    def SaveRecord(self, dirName, filePrefix):

        if not os.path.isdir(dirName):
            os.makedirs(dirName)

        now      = datetime.datetime.today()
        dataName = "{0}_".format(filePrefix) + now.strftime("%d-%m-%Y_%H-%M-%S-%f")
        with open("{0}/{1}.ctndt".format(dirName, dataName),'wb') as handle:
            cPickle.dump(self, handle, protocol=cPickle.HIGHEST_PROTOCOL)