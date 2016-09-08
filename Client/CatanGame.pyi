from CatanPlayer import *
from CatanAction import *

class Game:

    def __init__(self, gameState : GameState) -> None:
        pass

    def AddPlayer(self, player : Player, index : int) -> None:
        pass

    def CreateBoard(self, message) -> None:
        pass

    def GetPossibleActions(self, player : Player, gameState : GameState, ignoreTurn : bool) -> object:
        pass

    def CanBuildRoad(self, gameState : GameState, player : Player, edge, roadIndex : int, setUpPhase : bool) -> bool:
        pass

    def CanBuildSettlement(self, gameState : GameState, player : Player, node, setUpPhase : bool) -> bool:
        pass

    def GetPossibleRoads(self, gameState : GameState, player : Player, setUpPhase : bool) -> list[BuildRoadAction]:
        pass

    def GetPossibleSettlements(self, gameState : GameState, player : Player, setUpPhase : bool) -> list[BuildSettlementAction]:
        pass

    def GetPossibleCities(self, gameState : GameState, player : Player) -> list[BuildCityAction]:
        pass

    def GetDiceRoll(self) -> int:
        pass

    def GetPossibleRobberPositions(self, gameState : GameState, player : Player) -> list[int]:
        pass

class GameState:

    def __init__(self) -> None:
        pass

    def GetConstructableNodes(self) -> list[object]:
        pass

    def GetConstructableEdges(self) -> list[int]:
        pass

    def ApplyAction(self, action : Action, fromServer : bool) -> None:
        pass