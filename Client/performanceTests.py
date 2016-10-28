import timeit
from ctypes import cdll
import random

def func02():
    return int(random.random() * 10)

def func03():
    return random.randint(0, 10)

def func04():
    return random.randrange(10)

def func05():
    list1 = range(10)
    return list1[int(random.random() * len(list1))]

def func06():
    list1 = range(10)
    return random.choice(list1)

def listify(function):
    return [function() for i in range(50)]

if __name__ == '__main__':

    speedP1 = timeit.timeit("func02()", setup="from __main__ import func02")
    speedP2 = timeit.timeit("func03()", setup="from __main__ import func03")
    speedP3 = timeit.timeit("func04()", setup="from __main__ import func04")

    speedL1 = timeit.timeit("func05()", setup="from __main__ import func05")
    speedL2 = timeit.timeit("func06()", setup="from __main__ import func06")

    print("Python1 - {0}".format(speedP1))
    print("Python2 - {0}".format(speedP2))
    print("Python3 - {0}".format(speedP3))

    print("PythonList1 - {0}".format(speedL1))
    print("PythonList2 - {0}".format(speedL2))

    print(listify(func02))
    print(listify(func03))
    print(listify(func04))
