import pandas as pd, numpy as np, math, csv, matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter

##################################################################################
# Lib Functions
##################################################################################

def CreateSeries(Centre, Mandis, Retail, Whole):
  rc = Retail[Retail[1] == Centre]
  rc = rc.sort([0], ascending=[True])
  rc[3] = rc.apply(lambda row: datetime.strptime(row[0], '%Y-%m-%d'), axis=1)
  rc.drop(rc.columns[[0,1]], axis=1, inplace=True)

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

rc = retail[retail[1] == 37]
rc = rc.sort([0], ascending=[True])
rc[3] = rc.apply(lambda row: datetime.strptime(row[0], '%Y-%m-%d'), axis=1)
rc.drop(rc.columns[[0,1]], axis=1, inplace=True)
rc.set_index(3, inplace=True)
rc.index.names=[None]
idx = pd.date_range('2006-01-01', '2015-06-23')
# Check this out
# pd.ewma(rc[2], span=7)
rc = rc.reindex(idx, fill_value=0)


# Now for the assigned centres and mandis create series
c = [37,40,50]
m = [[337, 345, 577], [278, 284, 285, 288, 323, 324, 405, 545, 584], [279, 325, 376]]
