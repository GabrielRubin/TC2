from AgentRandom import *
from datetime import datetime
from datetime import timedelta
import copy
import cPickle

class AgentMCTS(AgentRandom):

    # * OPTION (for performance)*
    #    implement nodes as a tuple (worse to read/understand)
    # MCTS TREE NODE STRUCTURE:
    # (gameState, action     , Q-value , N-value     , PARENT     , CHILDREN)
    #  currState, from parent, reward  , n. of visits, parent node, children
    class MCTSNode:

        def __init__(self, state, action, qValue, nValue, parent, children, actionsFunction):
            self.gameState       = state  # current gameState
            self.action          = action  # action that led to this state
            self.QValue          = qValue  # node estimated reward value
            self.NValue          = nValue  # number of visits
            self.parent          = parent  # parent
            self.children        = children  # children
            self.possibleActions = actionsFunction(state,
                                                   state.players[state.currPlayer])

    explorationConstant = 0.5

    def __init__(self, name, seatNumber, choiceTime = 30.0):

        super(AgentMCTS, self).__init__(name, seatNumber)

        self.choiceTime = choiceTime

        self.agentName = "MONTE CARLO TREE SEARCH : {0} sec".format(choiceTime)

        self.numberOfSimulations = 0

    def DoMove(self, game):

        if game.gameState.currPlayer != self.seatNumber and \
            game.gameState.currState != "WAITING_FOR_DISCARDS":
            return None

        if game.gameState.currState == "WAITING_FOR_DISCARDS":
            return self.ChooseCardsToDiscard()

        if (game.gameState.currState == "START1A" and self.firstSettlementBuild) or \
           (game.gameState.currState == "START1B" and self.firstRoadBuild) or \
           (game.gameState.currState == "START2A" and self.secondSettlementBuild) or \
           (game.gameState.currState == "START2B" and self.secondRoadBuild):
            return None

        self.numberOfSimulations = 0

        state = cPickle.loads(cPickle.dumps(game.gameState, -1))

        self.PrepareGameStateForSimulation(state)

        return self.MonteCarloTreeSearch(state, timedelta(seconds=self.choiceTime))

    def MonteCarloTreeSearch(self, gameState, maxDuration):

        rootNode = self.MCTSNode(
                        state=gameState,
                        action=None,
                        qValue=[0 for i in range(len(gameState.players))],
                        nValue=0,
                        parent=None,
                        children=[],
                        actionsFunction=self.GetPossibleActions)

        if rootNode.possibleActions is None:
            print("MCTS ERROR! POSSIBLE ACTIONS FROM ROOT NODE ARE NONE!!!!")
            return None

        elif len(rootNode.possibleActions) == 1:
            return rootNode.possibleActions[0]

        elif len(rootNode.possibleActions) <= 0:
            print("MCTS ERROR! NO POSSIBLE ACTIONS FROM ROOT NODE!")
            return None

        startTime = datetime.utcnow()

        while (datetime.utcnow() - startTime) < maxDuration:

            nextNode    = self.TreePolicy(rootNode)

            reward      = self.SimulationPolicy(cPickle.loads(cPickle.dumps(nextNode.gameState, -1)))

            self.BackUp(nextNode, reward)

            self.numberOfSimulations += 1

        #print("TOTAL SIMULATIONS = {0}".format(self.numberOfSimulations))

        return self.BestChild(rootNode, 0).action

    def TreePolicy(self, node):

        while not node.gameState.IsTerminal():
            # There are still actions to try in this node...
            if len(node.possibleActions) > 0:
                return self.Expand(node)
            else:
                node = self.BestChild(node, AgentMCTS.explorationConstant)

        return node

    def Expand(self, node):

        chosenAction = random.choice(node.possibleActions)

        node.possibleActions.remove(chosenAction)

        nextGameState = cPickle.loads(cPickle.dumps(node.gameState, -1))

        chosenAction.ApplyAction(nextGameState)

        childNode = self.MCTSNode(state=nextGameState,
                                  action=chosenAction,
                                  qValue=[0 for i in range(len(nextGameState.players))],
                                  nValue=0,
                                  parent=node,
                                  children=[],
                                  actionsFunction=self.GetPossibleActions)

        node.children.append(childNode)

        return childNode

    def BestChild(self, node, explorationValue):

        currPlayerNumber = node.gameState.currPlayer

        # Returns the Child Node with the max 'Q-Value'
        #return max(node.children, key=lambda child: child.QValue[currPlayerNumber])

        def UCTClassifier(childNode):

            evaluationPart  = childNode.QValue[currPlayerNumber] / childNode.NValue
            explorationPart = explorationValue * math.sqrt( (2 * math.log(node.NValue)) / childNode.NValue )
            return evaluationPart + explorationPart

        return max(node.children, key=lambda child : UCTClassifier(child))

    def SimulationPolicy(self, gameState):

        #startTime = datetime.utcnow()
        #print("starting simulation {0}".format(startTime))

        while not gameState.IsTerminal():

            possibleActions = self.GetPossibleActions(gameState,
                                                      gameState.players[gameState.currPlayer],
                                                      atRandom=True)

            if len(possibleActions) > 1:
                action = random.choice(possibleActions)
            else:

                if not possibleActions:
                    print(gameState.currState)

                action = possibleActions[0]

            action.ApplyAction(gameState)

        #endTime = datetime.utcnow()
        #print("simulation ENDED {0} - deltaTime = {1}".format(endTime, (endTime - startTime).total_seconds()))

        return self.Utility(gameState, self.seatNumber)

    def BackUp(self, node, reward):

        currPlayer = node.gameState.currPlayer

        while node is not None:

            node.NValue             += 1
            node.QValue[currPlayer] += reward
            node = node.parent

    def Utility(self, gameState, playerNumber):

        # TEMP...
        return gameState.players[playerNumber].GetVictoryPoints()

    def PrepareGameStateForSimulation(self, gameState):

        for player in gameState.players:

            if player is None:
                continue

            quantity = player.resources[g_resources.index('UNKNOWN')]

            if quantity > 0:

                player.resources[g_resources.index('UNKNOWN')] = 0

                resources = [0, 0, 0, 0, 0, 0]

                for i in range(0, quantity):
                    resources[random.randint(0, 4)] += 1

                player.resources = player.resources + resources

    def GetPossibleActions(self, gameState, player, atRandom=False):

        if not gameState.setupDone:
            return self.GetPossibleActions_SetupTurns(gameState, player)
        elif gameState.currState == "PLAY":
            return self.GetPossibleActions_PreDiceRoll(player)
        elif gameState.currState == "PLAY1":
            if atRandom:
                return [self.GetRandomAction_RegularTurns(gameState, player)]
            else:
                return self.GetPossibleActions_RegularTurns(gameState, player)
        else:
            return self.GetPossibleActions_SpecialTurns(gameState, player)