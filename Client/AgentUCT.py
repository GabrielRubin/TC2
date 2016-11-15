from AgentMCTS import AgentMCTS
import math

class AgentUCT(AgentMCTS):

    def __init__(self, name, seatNumber, choiceTime=10.0, simulationCount=None, multiThreading=False, preSelect=True):

        super(AgentUCT, self).__init__(name, seatNumber, choiceTime, simulationCount, multiThreading, preSelect)
        self.agentName = "UCT : {0} sec, {1} sims".format(choiceTime, simulationCount)

    def BestChild(self, node, explorationValue, player=None):

        if len(node.children) <= 0:
            return None

        def UCB1(childNode):

            tgtPlayer = node.currentPlayer if player is None else player

            evaluationPart  = float(childNode.QValue[tgtPlayer]) / float(childNode.NValue)
            explorationPart = explorationValue * math.sqrt( (2 * math.log(node.NValue)) / float(childNode.NValue) )
            return evaluationPart + explorationPart

        return max(node.children, key=lambda child : UCB1(child))