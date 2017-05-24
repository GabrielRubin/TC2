from AgentUCT import AgentUCT
import math

class AgentRAVE(AgentUCT):

    def __init__(self, name, seatNumber, choiceTime = 10.0, simulationCount = None, explorationValue = 0.25,
                 multiThreading = False, numberOfThreads = 0, preSelectMode = 'citiesOverSettlements',
                 simPreSelectMode = None, trading = None, virtualWins = False):

        super(AgentUCT, self).__init__(name, seatNumber, choiceTime, simulationCount, explorationValue,
                                       multiThreading, numberOfThreads, preSelectMode, simPreSelectMode, trading, virtualWins)
        self.agentName = "RAVE : {0} sec, {1} sims".format(choiceTime, simulationCount)
        self.Vvalue              = 10
        self.explorationConstant = 0.25

    def BestChild(self, node, explorationValue, totalNValue, player=None):

        if len(node.children) <= 0:
            return None

        tgtPlayer = node.currentPlayer if player is None else player

        def UCB1(childNode):
            evaluationPart  = float(childNode.QValue[tgtPlayer]) / float(childNode.NValue)
            explorationPart = explorationValue * math.sqrt( (2 * math.log(node.NValue)) / float(childNode.NValue) )
            return evaluationPart + explorationPart

        def AMAF(childNode):
            return float(childNode.AMAFQValue[tgtPlayer]) / float(childNode.AMAFNValue)

        def RAVESelection(childNode):
            alpha = float(max(0, float(self.Vvalue - childNode.NValue)/max(1, self.Vvalue)))
            A     = float(AMAF(childNode))
            U     = float(UCB1(childNode))
            return alpha*A + (1-alpha)*U

        return max(node.children, key=lambda child : RAVESelection(child))

    def BackUp(self, node, reward):

        nodeAction = node.action

        while node is not None:
            node.UpdateNValue()
            node.QValue += reward
            if node.parent is not None:
                node = node.parent
            else:
                break

        # Update RAVE values doing Breadth-first node traversal
        visited        = []
        toVisit        = [node]

        while len(toVisit) > 0:
            current = toVisit[0]
            toVisit.remove(current)
            visited.append(current)

            if current.action == nodeAction:
                current.AMAFNValue += 1
                current.AMAFQValue += reward

            for node in current.children:
                if node in visited:
                    continue
                toVisit.append(node)