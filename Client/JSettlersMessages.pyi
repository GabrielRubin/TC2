
g_harbour_to_resource = {

    "3For1"       : 6,
    "ClayHarbor"  : 1,
    "OreHarbor"   : 2,
    "SheepHarbor" : 3,
    "GrainHarbor" : 4,
    "LumberHarbor": 5
}

g_board_indicators = {

    0: 'Desert',
    1: 'Clay',
    2: 'Ore',
    3: 'Sheep',
    4: 'Grain',
    5: 'Lumber',
    6: 'EmptySea',

    7: '3For1',
    8: '3For1',
    9: '3For1',
    10: '3For1',
    11: '3For1',
    12: '3For1',

    17: 'ClayHarbor',
    18: 'OreHarbor',
    19: 'SheepHarbor',
    20: 'GrainHarbor',
    21: 'LumberHarbor',

    33: 'ClayHarbor',
    34: 'OreHarbor',
    35: 'SheepHarbor',
    36: 'GrainHarbor',
    37: 'LumberHarbor',

    49: 'ClayHarbor',
    50: 'OreHarbor',
    51: 'SheepHarbor',
    52: 'GrainHarbor',
    53: 'LumberHarbor',

    65: 'ClayHarbor',
    66: 'OreHarbor',
    67: 'SheepHarbor',
    68: 'GrainHarbor',
    69: 'LumberHarbor',

    81: 'ClayHarbor',
    82: 'OreHarbor',
    83: 'SheepHarbor',
    84: 'GrainHarbor',
    85: 'LumberHarbor',

    97: 'ClayHarbor',
    98: 'OreHarbor',
    99: 'SheepHarbor',
    100: 'GrainHarbor',
    101: 'LumberHarbor'
}

g_harbors = {

    '3for1'       : [ 7,  8,  9, 10, 11, 12 ],
    'ClayHarbor'  : [17, 33, 49, 65, 81, 97 ],
    'OreHarbor'   : [18, 34, 50, 66, 82, 98 ],
    'SheepHarbor' : [19, 35, 51, 67, 83, 99 ],
    'GrainHarbor' : [20, 36, 52, 68, 84, 100],
    'LumberHarbor': [21, 37, 53, 69, 85 ,101]
}

g_messageNumberToGameNumber = {

   -1 :  0,
    0 :  2,
    1 :  3,
    2 :  4,
    3 :  5,
    4 :  6,
    5 :  8,
    6 :  9,
    7 : 10,
    8 : 11,
    9 : 12
}

elementIdToType = {

    '1'  : 'BRICK',
    '2'  : 'ORE',
    '3'  : 'WOOL',
    '4'  : 'GRAIN',
    '5'  : 'LUMBER',
    '6'  : 'UNKNOWN',
    '10' : 'ROADS',
    '11' : 'SETTLEMENTS',
    '12' : 'CITIES',
    '15' : 'KNIGHTS',
    '100': 'SET',
    '101': 'GAIN',
    '102': 'LOSE'
}

g_stateIdToName = {

      '0'   : 'NEW'                   # Brand new game
    , '1'   : 'READY'                 # Ready to start playing
    , '5'   : 'START1A'               # Players place 1st settlement
    , '6'   : 'START1B'               # Players place 1st road
    , '10'  : 'START2A'               # Players place 2nd settlement
    , '11'  : 'START2B'               # Players place 2nd road
    , '15'  : 'PLAY'                  # Play continues normally
    , '20'  : 'PLAY1'                 # Done rolling
    , '30'  : 'PLACING_ROAD'
    , '31'  : 'PLACING_SETTLEMENT'
    , '32'  : 'PLACING_CITY'
    , '33'  : 'PLACING_ROBBER'
    , '40'  : 'PLACING_FREE_ROAD1'    # Player is placing first road
    , '41'  : 'PLACING_FREE_ROAD2'    # Player is placing second road
    , '50'  : 'WAITING_FOR_DISCARDS'  # Waiting for players to discard
    , '51'  : 'WAITING_FOR_CHOICE'    # Waiting for player to choose a player
    , '52'  : 'WAITING_FOR_DISCOVERY' # Waiting for player to choose 2 resources
    , '53'  : 'WAITING_FOR_MONOPOLY'  # Waiting for player to choose a resource
    , '1000': 'OVER'                  # The game is over
}

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