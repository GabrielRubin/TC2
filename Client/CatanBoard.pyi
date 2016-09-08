class BoardHex:

    def __init__(self, index : int) -> None:
      pass

    def SetTerrain(self, terrainId : (str, int)) -> None:
      pass

    def GetAdjacentHexes(self) -> list[int]:
      pass

    def GetAdjacentNodes(self) -> list[int]:
      pass

    def GetAdjacentEdges(self) -> list[int]:
      pass

class BoardNode:

    def __init__(self, index : int) -> None:
      pass

    def GetAdjacentHexes(self) -> list[int]:
      pass

    def GetAdjacentNodes(self) -> list[int]:
      pass

    def GetAdjacentEdges(self) -> list[int]:
      pass

class BoardEdge:

    def __init__(self, index : int) -> None:
      pass

    def GetAdjacentHexes(self) -> list[int]:
      pass

    def GetAdjacentNodes(self) -> list[int]:
      pass

    def GetAdjacentEdges(self) -> list[int]:
      pass

class Construction:

    def __init__(self, constructionType : (str, int), owner : int, index : int, position : int) -> None:
      pass