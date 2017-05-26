import random

def memoize(f):
    """ Memoization decorator for a function taking one or more arguments. """
    class memodict(dict):
        def __getitem__(self, *key):
            return dict.__getitem__(self, key)

        def __missing__(self, key):
            ret = self[key] = f(*key)
            return ret

    return memodict().__getitem__

class TestClass1:

    def __init__(self):
        self.list = []

    def start(self):
        self.list = [TestClass2() for i in range(0, 100)]
        for test in self.list:
            test.start()

    def getCopy(self):
        copy = TestClass1()
        copy.list = [test.getCopy() for test in self.list]
        return copy

class TestClass2:

    def __init__(self):
        self.list = []
        self.number1 = 0
        self.number2 = 0
        self.number3 = 0

    def start(self):
        self.list = [TestClass3() for i in range(0, 100)]
        for test in self.list:
            test.start()
        self.number1 = random.random()
        self.number2 = random.random()
        self.number3 = random.random()

    def getCopy(self):
        copy = TestClass2()
        copy.list = [test.getCopy() for test in self.list]
        copy.number1 = self.number1
        copy.number2 = self.number2
        copy.number3 = self.number3
        return copy

class TestClass3:

    def __init__(self):
        self.number = 0

    def start(self):
        self.number = random.random()

    def getCopy(self):
        copy = TestClass3()
        copy.number = self.number
        return copy

if __name__ == '__main__':

    list = [TestClass3() for i in range(0, 1000)]
    print(len(list))