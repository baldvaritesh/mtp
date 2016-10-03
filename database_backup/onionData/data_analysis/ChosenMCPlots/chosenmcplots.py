import pandas as pd, numpy as np, math, csv, matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter

##################################################################################
# Lib Functions
##################################################################################

def CreateCentreSeries(Centre, Retail, EWMAisOn):
  rc = Retail[Retail[1] == Centre]
  rc = rc.sort([0], ascending=[True])
  rc[3] = rc.apply(lambda row: datetime.strptime(row[0], '%Y-%m-%d'), axis=1)
  rc.drop(rc.columns[[0,1]], axis=1, inplace=True)
  rc.set_index(3, inplace=True)
  rc.index.names=[None]
  idx = pd.date_range('2006-01-01', '2015-06-23')
  rc = rc.reindex(idx, fill_value=0)
  # Check this out
  rcSeries = []
  if (EWMAisOn):
    rcSeries = pd.ewma(rc[2], span=7)
  else:
    rcSeries = rc
  return rcSeries*100

def CreateMandiSeries(Mandi, Whole, EWMAisOn):
  mc = Whole[Whole[1] == Mandi]
  mc = mc.sort([0], ascending=[True])
  mc[8] = mc.apply(lambda row: datetime.strptime(row[0], '%Y-%m-%d'), axis=1)
  mc.drop(mc.columns[[0,1,2,3,4,5,6]], axis=1, inplace=True)
  mc.set_index(8, inplace=True)
  mc.index.names=[None]
  idx = pd.date_range('2006-01-01', '2015-06-23')
  mc = mc.reindex(idx, fill_value=0)
  mcSeries = []
  if (EWMAisOn):
    mcSeries = pd.ewma(mc[7], span=7)
  else:
    mcSeries = mc
  return mcSeries

def PlotDifferenceAbsolute(SeriesA, SeriesB, MCDiff, SaveToFile=""):
  diff = abs(SeriesA - SeriesB) if (not MCDiff) else abs(SeriesA[2] - SeriesB[7])
  plt.plot(diff)
  plt.savefig(SaveToFile) if (len(SaveToFile) != 0) else plt.show()
  plt.clf()

def PlotDifference(SeriesA, SeriesB, MCDiff, SaveToFile=""):
  diff = (SeriesA - SeriesB) if (not MCDiff) else (SeriesA[2] - SeriesB[7])
  plt.plot(diff)
  plt.savefig(SaveToFile) if (len(SaveToFile) != 0) else plt.show()
  plt.clf()

def PlotCentreWithMandi(CSeries, MSeries, SaveToFile="", ColorC = "", ColorM = ""):
  plt.plot(CSeries, color=ColorC) if (len(ColorC) != 0) else plt.plot(CSeries)
  plt.plot(MSeries, color=ColorM) if (len(ColorM) != 0) else plt.plot(MSeries)
  plt.savefig(SaveToFile) if (len(SaveToFile) != 0) else plt.show()
  plt.clf()


##################################################################################
# Generate Plots
##################################################################################

# Pick the centres assigned to me
# c: 37, 40, 50
# m: [337, 345, 577], [278, 284, 285, 288, 323, 324, 405, 545, 584], [279, 325, 376]

whole = pd.read_csv('../../csv_bkup/wholesaleoniondata.csv', header=None)
retail = pd.read_csv('../../csv_bkup/RetailOnionData.csv', header=None)

# Curate the data sets
whole = whole[whole[2] != 0]
whole = whole[np.isfinite(whole[2])]
whole = whole[whole[7] != 0]
whole = whole[np.isfinite(whole[7])]
retail = retail[retail[2] != 0]
retail = retail[np.isfinite(retail[2])]

whole = whole[whole[0] >= "2006-01-01"]
whole = whole[whole[0] <= "2015-06-23"]
retail = retail[retail[0] >= "2006-01-01"]
retail = retail[retail[0] <= "2015-06-23"]

whole = whole.drop_duplicates(subset=[0,1], take_last=True)
retail = retail.drop_duplicates(subset=[0,1], take_last=True)


# Now for the assigned centres and mandis create series
x = {10: 0, 16: 1, 40: 2, 44: 3, 50: 4}
c = [10, 16, 40, 44, 50]
m = [[182, 174, 194], [281, 404, 351, 312, 165, 70, 293, 164, 407, 166], [545, 323, 405, 584, 278, 288], [156, 427], [279, 376]]

cs = []
ms = []

# We are not doing smoothening now
for i in range(0 , len(c)):
  cs.append(CreateCentreSeries(c[i] , retail, False))
  ms.append([])
  for j in range(0, len(m[i])):
    ms[i].append(CreateMandiSeries(m[i][j] , whole, False))