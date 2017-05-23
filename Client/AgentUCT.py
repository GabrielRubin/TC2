from AgentMCTS import AgentMCTS
import math
import random

class AgentUCT(AgentMCTS):

    def __init__(self, name, seatNumber, choiceTime = 10.0, simulationCount = None, explorationValue = 0.25,
                 multiThreading = False, numberOfThreads = 0, preSelectMode = 'citiesOverSettlements',
                 simPreSelectMode = None, trading = None, virtualWins = False):

        super(AgentUCT, self).__init__(name, seatNumber, choiceTime, simulationCount, explorationValue,
                                       multiThreading, numberOfThreads, preSelectMode, simPreSelectMode, trading, virtualWins)
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

            #if float(childNode.NValue) <= 0:
            #    print("DIV BY ZERO! ERROR!")
            #    raise ArithmeticError

            evaluationPart  = float(childNode.QValue[tgtPlayer]) / float(childNode.NValue)
            explorationPart = explorationValue * math.sqrt( (2 * math.log(node.NValue)) / float(childNode.NValue) )
            return evaluationPart + explorationPart

        return max(node.children, key=lambda child : UCB1(child))