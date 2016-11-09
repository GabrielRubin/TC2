import numpy as np
import os

gameStatsColumns = [
                    ("Winner",       np.str_, 16),
                    ("Points",       np.str_, 16),
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

    arrayType = np.dtype(gameStatsColumns)

    grades = np.array(fileContent, dtype=arrayType)

    if os.path.isfile(filePath):

      with open(filePath, "a") as csv_file:
        np.savetxt(csv_file,
                   grades,
                   delimiter=',',
                   fmt=('%s', '%s', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u'),
                   comments='')
    else:

      with open(filePath, "w") as csv_file:
        np.savetxt(csv_file,
                   grades,
                   delimiter=',',
                   fmt=('%s', '%s', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u', '%2u'),
                   comments='',
                   header='Winner, Points, Turns, Agent Points, Roads, Settlements, Cities, Knights, Largest Road, Largest Army')

    print ("---- CSV file generated in {0}! ----".format(filePath))


