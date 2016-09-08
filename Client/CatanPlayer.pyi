from CatanGame import *

class Player:

    def __init__(self, name : str, seatNumber : int) -> None:
        pass

    def GetVictoryPoints(self) -> int:
        pass

    def DoMove(self, game : Game) -> object:
        # type: (Game) -> object
        pass

    def ChooseCardsToDisard(self, game : Game):
        pass

class AgentRandom(Player):

    def DoMove(self, game : Game) -> object:
        # type: (Game) -> object
        pass

    def ChooseCardsToDiscard(self, game : Game):
        pass

    def ChoosePlayerToStealFrom(self, game : Game) -> int:
        pass