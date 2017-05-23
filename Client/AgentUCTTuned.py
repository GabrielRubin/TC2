from AgentMCTS import AgentMCTS
import math
import random

class AgentUCTTuned(AgentMCTS):

    def __init__(self, name, seatNumber, choiceTime = 10.0, simulationCount = None, explorationValue = 0.25,
                 multiThreading = False, numberOfThreads = 0, preSelectMode = 'citiesOverSettlements',
                 simPreSelectMode = None, trading = None, virtualWins = False):

        super(AgentUCTTuned, self).__init__(name, seatNumber, choiceTime, simulationCount, explorationValue,
                                            multiThreading, numberOfThreads, preSelectMode, simPreSelectMode, trading, virtualWins)
        self.agentName = "UCT Tuned: {0} sec, {1} sims".format(choiceTime, simulationCount)

    def BestChild(self, node, explorationValue, totalNValue, player=None):

        if len(node.children) <= 0:
            return None

        if node.action is not None and len(node.children) > 0:
            if node.children[0].action.type == 'RollDices' and node.parent is not None:
                diceResult = 2 + int(random.random() * 6) + int(random.random() * 6)
                return max(node.children, key=lambda child : child.action.result == diceResult)

        def Vj(childNode, tgtPlayer):

            playersQValues = [math.pow(Qval[tgtPlayer], 2.0) for Qval in childNode.QValueHist]

            sumPart       = sum(playersQValues) / float(childNode.NValue)
            mediumRewards = math.pow(float(childNode.QValue[tgtPlayer]) / float(childNode.NValue), 2.0)

            return sumPart - mediumRewards + math.sqrt((2.0 * math.log(totalNValue))/float(childNode.NValue))

        def UCB1Tuned(childNode):

            tgtPlayer = node.currentPlayer if player is None else player

            evaluationPart  = float(childNode.QValue[tgtPlayer]) / float(childNode.NValue)
            explorationPart = math.sqrt( (math.log(node.NValue) / float(childNode.NValue)) *
                                         min( 1.0/4.0, Vj(childNode, tgtPlayer)) )
            return evaluationPart + explorationPart

        return max(node.children, key=lambda child : UCB1Tuned(child))