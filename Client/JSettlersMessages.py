'''
    NEWCHANNEL           = 1001
    MEMBERS              = 1002
    CHANNELS             = 1003
    JOIN                 = 1004
    TEXTMSG              = 1005
    LEAVE                = 1006
    DELETECHANNEL        = 1007
    LEAVEALL             = 1008
    PUTPIECE             = 1009
    GAMETEXTMSG          = 1010
    LEAVEGAME            = 1011
    SITDOWN              = 1012
    JOINGAME             = 1013
    BOARDLAYOUT          = 1014
    DELETEGAME           = 1015
    NEWGAME              = 1016
    GAMEMEMBERS          = 1017
    STARTGAME            = 1018
    GAMES                = 1019
    JOINAUTH             = 1020
    JOINGAMEAUTH         = 1021
    IMAROBOT             = 1022
    JOINGAMEREQUEST      = 1023
    PLAYERELEMENT        = 1024
    GAMESTATE            = 1025
    TURN                 = 1026
    SETUPDONE            = 1027
    DICERESULT           = 1028
    DISCARDREQUEST       = 1029
    ROLLDICEREQUEST      = 1030
    ROLLDICE             = 1031
    ENDTURN              = 1032
    DISCARD              = 1033
    MOVEROBBER           = 1034
    CHOOSEPLAYER         = 1035
    CHOOSEPLAYERREQUEST  = 1036
    REJECTOFFER          = 1037
    CLEAROFFER           = 1038
    ACCEPTOFFER          = 1039
    BANKTRADE            = 1040
    MAKEOFFER            = 1041
    CLEARTRADEMSG        = 1042
    BUILDREQUEST         = 1043
    CANCELBUILDREQUEST   = 1044
    BUYCARDREQUEST       = 1045
    DEVCARD              = 1046
    DEVCARDCOUNT         = 1047
    SETPLAYEDDEVCARD     = 1048
    PLAYDEVCARDREQUEST   = 1049
    DISCOVERYPICK        = 1052
    MONOPOLYPICK         = 1053
    FIRSTPLAYER          = 1054
    SETTURN              = 1055
    ROBOTDISMISS         = 1056
    POTENTIALSETTLEMENTS = 1057
    CHANGEFACE           = 1058
    REJECTCONNECTION     = 1059
    LASTSETTLEMENT       = 1060
    GAMESTATS            = 1061
    BCASTTEXTMSG         = 1062
    RESOURCECOUNT        = 1063
    ADMINPING            = 1064
    ADMINRESET           = 1065
    LONGESTROAD          = 1066
    LARGESTARMY          = 1067
    SETSEATLOCK          = 1068
    STATUSMESSAGE        = 1069
    CREATEACCOUNT        = 1070
    UPDATEROBOTPARAMS    = 1071
    SERVERPING           = 9999
'''

class Message:
    def __init__(self):
        pass

    def to_cmd(self):
        pass

    def values(self):
        vars = filter(lambda x: x not in [
                                "__doc__", "__init__", "__module__"
                              , "to_cmd", "parse", "values", "id", "etype"]
                     , dir(self))
        return dict([(name, getattr(self, name)) for name in vars])

    @staticmethod
    def parse(text):
        return None

class ChannelsMessage(Message):
    id = 1003
    def __init__(self, channels):
        self.channels = channels

    def to_cmd(self):
        return "{0}|{1}".format(self.id, ",".join(self.channels))

    @staticmethod
    def parse(text):
        channels = filter(None, text.split(","))
        return ChannelsMessage(channels)

class GamesMessage(Message):
    id = 1019
    def __init__(self, games):
        self.games = games

    def to_cmd(self):
        return "{0}|{1}".format(self.id, ",".join(self.games))

    @staticmethod
    def parse(text):
        games = filter(None, text.split(","))
        return GamesMessage(games)

class JoinGameMessage(Message):
    id = 1013
    def __init__(self, nickname, password, host, game):
        self.nickname = nickname
        self.password = password
        self.host = host
        self.game = game

    def to_cmd(self):
        password = "\t" if self.password == "" else self.password
        return "{0}|{1},{2},{3},{4}".format(self.id, self.nickname, password
                                        ,self.host, self.game)

    @staticmethod
    def parse(text):
        data = text.split(",")
        data[1] = "" if data[1] == "\t" else ""
        return JoinGameMessage(*data)