import cython
import random
cimport cython

cdef class listm(list):
    """
    See http://docs.cython.org/src/userguide/special_methods.html
    """
    def __add__(self,y):
        cdef int i,N

        if isinstance(self,listm):
            N=len(self)
            if isinstance(y,int) or isinstance(y,float):
                return listm([self[i]+y for i in range(N)])
            else:
                return listm([self[i]+y[i] for i in range(N)])
        else:
            ### it is backwards, self is something else, y is a listm
            N=len(y)
            if isinstance(self,int) or isinstance(self,float):
                return listm([y[i]+self for i in range(N)])
            else:
                return listm([self[i]+y[i] for i in range(N)])

    def __mul__(self,y):
        cdef int i,N

        if isinstance(self,listm):
            N=len(self)
            if isinstance(y,int) or isinstance(y,float):
                return listm([self[i]*y for i in range(N)])
            else:
                return listm([self[i]*y[i] for i in range(N)])
        else:
            ### it is backwards, self is something else, y is a listm
            N=len(y)
            if isinstance(self,int) or isinstance(self,float):
                return listm([y[i]*self for i in range(N)])
            else:
                return listm([self[i]*y[i] for i in range(N)])

    def __truediv__(self,y):
        cdef int i,N

        if isinstance(self,listm):
            N=len(self)
            if isinstance(y,int) or isinstance(y,float):
                return listm([self[i]/y for i in range(N)])
            else:
                return listm([self[i]/y[i] for i in range(N)])
        else:
            ### it is backwards, self is something else, y is a listm
            N=len(y)
            if isinstance(self,int) or isinstance(self,float):
                return listm([self/y[i] for i in range(N)])
            else:
                return listm([self[i]/y[i] for i in range(N)])

    def __sub__(self,y):
        cdef int i,N

        if isinstance(self,listm):
            N=len(self)
            if isinstance(y,int) or isinstance(y,float):
                return listm([self[i]-y for i in range(N)])
            else:
                return listm([self[i]-y[i] for i in range(N)])
        else:
            ### it is backwards, self is something else, y is a listm
            N=len(y)
            if isinstance(self,int) or isinstance(self,float):
                return listm([self-y[i] for i in range(N)])
            else:
                return listm([self[i]-y[i] for i in range(N)])

def CanAfford(listm resources, listm price):
    cdef int i
    for i in range(5):
        if price[i] > resources[i]:
            return False
    return True

def GetRandomBankTrade(listm playerResources, tradeRates):

    cdef int i, j, k, l, m
    cdef listm possibleTradeAmount = listm([0, 0, 0, 0, 0])
    candidateForTrade              = []

    minResourceAmount = min(playerResources[:-1]) #Don't count the 'UNKNOWN' resource

    for i in range(len(possibleTradeAmount)):
        possibleTradeAmount[i] = int(playerResources[i] / tradeRates[i])
        if playerResources[i] == minResourceAmount:
            candidateForTrade.append(i)

    #tradeAmount = random.randint(0, sum(possibleTradeAmount))
    tradeAmount = int(random.random() * sum(possibleTradeAmount))

    if tradeAmount > 0 and len(candidateForTrade) > 0:

        possibleTradePopulation = [0 for i in range(0, possibleTradeAmount[0])] + \
                                  [1 for j in range(0, possibleTradeAmount[1])] + \
                                  [2 for k in range(0, possibleTradeAmount[2])] + \
                                  [3 for l in range(0, possibleTradeAmount[3])] + \
                                  [4 for m in range(0, possibleTradeAmount[4])]

        chosenResources   = random.sample(possibleTradePopulation, tradeAmount)

        expectedResources = []
        for i in range(0, tradeAmount):
            expectedResources.append(candidateForTrade[int(random.random() * len(candidateForTrade))])

        give = [chosenResources.count(0) * tradeRates[0], chosenResources.count(1) * tradeRates[1],
                chosenResources.count(2) * tradeRates[2], chosenResources.count(3) * tradeRates[3],
                chosenResources.count(4) * tradeRates[4]]

        get  = [expectedResources.count(0), expectedResources.count(1),
                expectedResources.count(2), expectedResources.count(3),
                expectedResources.count(4)]

        return give, get
    else:
        return None