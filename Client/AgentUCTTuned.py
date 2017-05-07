from AgentMCTS import AgentMCTS
import math
import random

class AgentUCTTuned(AgentMCTS):

    def __init__(self, name, seatNumber, choiceTime=10.0, simulationCount=None, multiThreading=False, numberOfThreads = 0, preSelect=True):

        super(AgentUCTTuned, self).__init__(name, seatNumber, choiceTime, simulationCount, multiThreading, numberOfThreads, preSelect)
        self.agentName = "UCT Tuned: {0} sec, {1} sims".format(choiceTime, simulationCount)

    def BestChild(self, node, explorationValue, totalNValue, player=None):

        if len(node.children) <= 0:
            return None

        if node.action is not None and len(node.children) > 0:
            if node.children[0].action.type == 'RollDices' and node.parent is not None:
                diceResult = 2 + int(random.random() * 6) + int(random.random() * 6)
                return max(node.children, key=lambda child : child.action.result == diceResult)

        def Vj(childNode, tgtPlayer):

            playersQValues = [Qval[tgtPlayer] for Qval in childNode.QValueHist]

            sumPart       = (math.pow(sum(playersQValues), 2)) / 2
            mediumRewards = math.pow(float(childNode.QValue[tgtPlayer]) / float(childNode.NValue), 2)

            return sumPart - mediumRewards + math.sqrt((2 * math.log(totalNValue))/childNode.NValue)

        def UCB1Tuned(childNode):

            tgtPlayer = node.currentPlayer if player is None else player

            evaluationPart  = float(childNode.QValue[tgtPlayer]) / float(childNode.NValue)
            explorationPart = math.sqrt( ((math.log(node.NValue)) / float(childNode.NValue)) *
                                         min(1/4, Vj(childNode, tgtPlayer)) )
            return evaluationPart + explorationPart

        return max(node.children, key=lambda child : UCB1Tuned(child))