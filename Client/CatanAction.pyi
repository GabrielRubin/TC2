class Action:

    def __init__(self) -> None:
        pass

class BuildRoadAction(Action):

    def __init__(self, playerNumber : int, position : int, index : int) -> None:
        pass

class BuildSettlementAction(Action):

    def __init__(self, playerNumber : int, position : int, index : int) -> None:
        pass

class BuildCityAction(Action):

    def __init__(self, playerNumber : int, position : int, index : int) -> None:
        pass

class RollDicesAction(Action):

    def __init__(self, playerNumber : int) -> None:
        pass

class BuyDevelopmentCardAction(Action):

    def __init__(self, playerNumber : int) -> None:
        pass

class UseKnightsCardAction(Action):

    def __init__(self, playerNumber : int, newRobberPos : int, targetPlayerIndex : int) -> None:
        pass

class UseMonopolyCardAction(Action):

    def __init__(self, playerNumber : int, resource) -> None:
        pass

class UseYearOfPlentyCardAction(Action):

    def __init__(self, playerNumber : int, resource1, resource2) -> None:
        pass

class UseFreeRoadsCardAction(Action):

    def __init__(self, playerNumber : int, road1Edge, road2Edge) -> None:
        pass

class PlaceRobberAction(Action):

    def __init__(self, playerNumber : int, newRobberPos : int) -> None:
        pass

class EndTurnAction(Action):

    def __init__(self, playerNumber : int) -> None:
        pass

class DiscardResourcesAction(Action):

    def __init__(self, playerNumber : int, resources) -> None:
        pass

class ChoosePlayerToStealFromAction(Action):

    def __init__(self, playerNumer : int, targetPlayerNumber : int) -> None:
        pass

class TradeOfferAction(Action):

    def __init__(self, offerType, playerNumber : int, targetPlayerNumber: int, offerResources, wantedResources) -> None: