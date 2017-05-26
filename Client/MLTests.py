import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import sklearn
import csv
import seaborn as sns

from matplotlib import rcParams
from sklearn.datasets import load_boston
from sklearn.linear_model import LinearRegression
from sklearn.ensemble.forest import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR

from Tkinter import Tk
from tkFileDialog import askopenfilename
import cPickle

class MyDataFile():

    def __init__(self, data, target, featureNames):
        self.data = data
        self.target = target
        self.featureNames = featureNames

def LoadDataset(path, fileName):
    with open("{0}/{1}.csv".format(path, fileName)) as csv_file:
        data_file = csv.reader(csv_file)
        temp = next(data_file)
        n_samples = int(temp[0])
        n_features = int(temp[1])
        data = np.empty((n_samples, n_features))
        target = np.empty((n_samples,), dtype=np.int)

        for i, sample in enumerate(data_file):
            data[i] = np.asarray(sample[:-1], dtype=np.float64)
            target[i] = np.asarray(sample[-1], dtype=np.int)

        return MyDataFile(data=data, target=target, featureNames=temp[2:len(temp)-1])

sns.set_style("whitegrid")
sns.set_context("poster")

gameData = LoadDataset("GameData", "allCSVData")

dataFrame = pd.DataFrame(gameData.data)
dataFrame.columns = gameData.featureNames
dataFrame['TargetVP'] = gameData.target

X = dataFrame.drop('TargetVP', axis = 1)
Y = dataFrame['TargetVP']

print(len(X))

X_train, X_test, Y_train, Y_test = sklearn.model_selection.train_test_split(X, Y, test_size = 0.33, random_state = 5)

isNew = True

lm = None

if isNew:
    lm = MLPRegressor()
    lm.fit(X_train, Y_train)
else:
    Tk().withdraw()
    filename = askopenfilename(filetypes=(("Model files", "*.mod"),
                                          ("All files", "*.*")))

    with open('{0}'.format(filename), 'rb') as handle:
        lm = cPickle.load(handle)

    if lm is not None:
        lm.fit(X_train, Y_train)

if lm is not None:

    Y_pred = lm.predict(X_test)

    pointsSize = [1 for n in range(len(X))]

    plt.scatter(Y_test, Y_pred, s=pointsSize)
    plt.xlabel("Total Victory Points (player - all) $Y_i$")
    plt.ylabel("Predicted Total VP $\hat{Y}_i$")
    plt.title("Total VP vs Predicted Total VP: $Y_i$ vs $\hat{Y}_i$")
    plt.show()

    mse = sklearn.metrics.mean_squared_error(Y_test, Y_pred)
    print(mse)

    yey = sklearn.metrics.r2_score(Y_test, Y_pred)
    print(yey)

    with open("Models/mainModel.mod", 'wb') as handle:
        cPickle.dump(lm, handle, protocol=cPickle.HIGHEST_PROTOCOL)

else:
    print("Error! lm is None!")