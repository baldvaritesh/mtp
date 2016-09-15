import pandas as pd, numpy as np, math, csv
from datetime import datetime
from collections import Counter

''' Structure of Database File From BackUp '''
''' Date  MandiCode Arrival   Origin    Variety   MinP  MaxP  ModalP '''

##################################################################################
# Lib Functions
##################################################################################

def StringDateToDay(x):
  dateObject = datetime.strptime(x, '%Y-%m-%d')
  return dateObject.strftime('%A')

def getMandisList(dataFrame, threshold):
  mandisList = Counter(dataFrame[1].tolist())
  for key, value in mandisList.items():
    if value < (0.8 * threshold):
      del mandisList[key]
  return mandisList.keys()

def getCentresDict(mappingMandiToCentre, mandisList):
  centreDict = {}
  for mandi in mandisList:
    c = mappingMandiToCentre[mandi]
    if c not in centreDict.keys():
      centreDict[c] = [mandi]
    else:
      centreDict[c].append(mandi)
  return centreList


##################################################################################
# Creating a Valid Mandi Database for analysis
##################################################################################

dfMC = pd.read_csv('../../csv_bkup/wholesaleoniondata.csv', header=None)

# Remove the mandis with zero or NULL arrival, and if min price is reported NULL
# You can also do the pruning if by chosing the modal price

dfMC = dfMC[dfMC[2] != 0]
dfMC = dfMC[np.isfinite(dfMC[2])]
dfMC = dfMC[dfMC[7] != 0]
dfMC = dfMC[np.isfinite(dfMC[7])]

# Drop any duplicates based on date and mandi ID and sort to see the last date

dfMC = dfMC.drop_duplicates(subset=[0,1])
dfMC = dfMC.sort([0,1], ascending=[True, True])

# Get the mapping of mandis to centres

df = pd.read_csv('../../csv_bkup/mandis.csv', header=None)
df['mapping'] = zip(df[0], df[5])
mapping = dict(df['mapping'].tolist())

# Here I get most of mandis in your result but I think that we should remove the weekends first
# But the corresponding centres only come out to be only 3 unlike 10, what you reported
mandis = getMandisList(dfMC, 2480)
print len(mandis)
centres = getCentresDict(mapping, mandis)
print len(centres)

# Drop the weekends from the data since we are not considering them in the centres data
# dfMC[8] = dfMC.apply(lambda row: StringDateToDay(row[0]), axis=1)
# dfMC = dfMC[dfMC[8] != 'Saturday']
# dfMC = dfMC[dfMC[8] != 'Sunday']

# Count the number of mandis actually left
# Total days = 9.5 * 365 = 3468
# Days apart from weekends : 9.5 * (365 - 104) = 2480
# Here the output is even more less
# mandis = getMandisList(dfMC, 2480)
# print len(mandis)
# centres = getCentresList(mapping, mandis)
# print len(centres)
# print centres
