from AgentMCTS import AgentMCTS
import math
import random

class AgentUCT(AgentMCTS):

    def __init__(self, name, seatNumber, choiceTime = 10.0, simulationCount = None,
                 multiThreading = False, numberOfThreads = 0, preSelectMode = 'citiesOverSettlements',
                 simPreSelectMode = None, trading = False):

        super(AgentUCT, self).__init__(name, seatNumber, choiceTime, simulationCount,
                                       multiThreading, numberOfThreads, preSelectMode, simPreSelectMode, trading)
        self.agentName = "UCT : {0} sec, {1} sims".format(choiceTime, simulationCount)

    def BestChild(self, node, explorationValue, totalNValue, player=None):

        if len(node.children) <= 0:
            return None

        if node.action is not None and len(node.children) > 0:
            if node.children[0].action.type == 'RollDices' and node.parent is not None:
                diceResult = 2 + int(random.random() * 6) + int(random.random() * 6)
                return max(node.children, key=lambda child : child.action.result == diceResult)

        def UCB1(childNode):

            tgtPlayer = node.currentPlayer if player is None else player

            evaluationPart  = float(childNode.QValue[tgtPlayer]) / float(childNode.NValue)
            explorationPart = explorationValue * math.sqrt( (2 * math.log(node.NValue)) / float(childNode.NValue) )
            return evaluationPart + explorationPart

        return max(node.children, key=lambda child : UCB1(child))