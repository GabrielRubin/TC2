def g_MessageNumberToGameNumber(messageNumber : int) -> int:
    pass

class Message:
    def __init__(self) -> None:
        pass

    def to_cmd(self) -> None:
        pass

    def values(self) -> dict[str, str]:
        pass

    @staticmethod
    def parse(text : str) -> None:
        pass

class ChannelsMessage(Message):
    id = 1003
    def __init__(self, channels):
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class SitDownMessage(Message):
    id = 1012

    def __init__(self, game : str, nickname : str, playerNumber : int, isRobot : bool) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class JoinGameMessage(Message):
    id = 1013
    def __init__(self, nickname : str, password : str, host : str, game : str) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class BoardLayoutMessage(Message):
    id = 1014

    def __init__(self, gameName : str, hexes : list[int], numbers : list[int], robberPos : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class NewGameMessage(Message):
    id = 1016

    def __init__(self, gameName : str) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class StartGameMessage(Message):
    id = 1018

    def __init__(self, game : str) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class GamesMessage(Message):
    id = 1019

    def __init__(self, games : list[str]) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class JoinGameAuthMessage(Message):
    id = 1021

    def __init__(self, gameName : str) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class GameStateMessage(Message):
    id = 1025

    def __init__(self, gameName : str, state : str) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class SetTurnMessage(Message):
    id = 1055

    def __init__(self, gameName : str, seatnum : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class ChangeFaceMessage(Message):
    id = 1058

    def __init__(self, gameName : str, playerNum : int, faceId : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class LongestRoadMessage(Message):
    id = 1066

    def __init__(self, gameName : str, playerNumber : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class LargestArmyMessage(Message):
    id = 1067

    def __init__(self, gameName : str, playerNumber : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class SetSeatLockMessage(Message):
    id = 1068

    def __init__(self, gameName : str, seatNumber : int, isLocked : bool) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class StatusMessageMessage(Message):
    id = 1069

    def __init__(self, status : str) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class GameMembersMessage(Message):
    id = 1017

    def __init__(self, game : str, members : list[str]) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class PlayerElementMessage(Message):
    id = 1024

    def __init__(self, game : str, playerNumber : int, action : str, element : str, value : int):
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class SetPlayedDevCardMessage(Message):
    id = 1048

    def __init__(self, game : str, playerNumber : int, cardflag : bool) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class DevCardCountMessage(Message):
    id = 1047

    def __init__(self, game : str, count : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class TurnMessage(Message):
    id = 1026

    def __init__(self, game : str, playerNumber : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class GameTextMsgMessage(Message):
    id = 1010

    def __init__(self, game : str, nickname : str, textmessage : str) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class PutPieceMessage(Message):
    id = 1009

    def __init__(self, game : str, playerNumber : int, pieceType : int, position : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

#class RollDiceRequestMessage(Message):
#    id = 1030
#
#    def __init__(self, game):
#        self.game = game
#
#    def to_cmd(self):
#        return "{0}|{1}".format(self.id, self.game)
#
#    @staticmethod
#    def parse(text):
#        return RollDiceRequestMessage(text)

class RollDiceMessage(Message):
    id = 1031

    def __init__(self, game : str):
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class DiceResultMessage(Message):
    id = 1028

    def __init__(self, game : str, result : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class EndTurnMessage(Message):
    id = 1032

    def __init__(self, game : str) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class MoveRobberMessage(Message):
    id = 1034

    def __init__(self, game : str, playerNumber : int, position : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class DiscardRequestMessage(Message):
    id = 1029

    def __init__(self, game : str, numCards : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class DiscardMessage(Message):
    id = 1033

    def __init__(self, game : str, clay : int, ore : int, sheep : int, wheat : int, wood : int, unknown : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

# TODO: FIX!
class MakeOfferMessage(Message):
    id = 1041

    def __init__(self, game : str, fr : str, to : str, give : str, get : str) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class RejectOfferMessage(Message):
    id = 1037

    def __init__(self, game : int, playerNumber : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class ChoosePlayerRequestMessage(Message):
    id = 1036

    def __init__(self, game : str, choices : list[str]) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass

class ChoosePlayerMessage(Message):
    id = 1035

    def __init__(self, game : str, choice : int) -> None:
        pass

    def to_cmd(self):
        pass

    @staticmethod
    def parse(text):
        pass