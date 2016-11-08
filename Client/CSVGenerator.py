import numpy as np
import os

gameStatsColumms = [
                    ("Winner",       np.str_, 16),
                    ("Points",       np.int),
                    ("Turns",        np.int),
                    ("Agent Points", np.int),
                    ("Roads",        np.int),
                    ("Settlements",  np.int),
                    ("Cities",       np.int),
                    ("Knights",      np.int),
                    ("Largest Road", np.int),
                    ("Largest Army", np.int)
                   ]

def WriteCSVFile(fileName, fileType, fileContent):

  filePath = "SimulatorLogs/" + fileName + ".csv"

  if fileType == "GameStats":

    arrayType = np.dtype(gameStatsColumms)

    grades = np.array(fileContent, dtype=arrayType)

    if os.path.isfile(filePath):

      with open(filePath, "a") as csv_file:
        np.savetxt(csv_file,
                   grades,
                   delimiter=',',
                   fmt=('%s', '%2u', '%2.1f'),
                   comments='', )
    else:

      with open(filePath, "w") as csv_file:
        np.savetxt(csv_file,
                   grades,
                   delimiter=',',
                   fmt=('%s', '%2u', '%2.1f'),
                   header='Winner, Points, Turns, Agent Points, Roads, Settlements, Cities, Knights, Largest Road, Largest Army',
                   comments='', )


