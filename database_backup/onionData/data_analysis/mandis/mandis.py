import pandas as pd, csv, numpy as np , math
from datetime import datetime
from collections import Counter

''' Structure of Database File From BackUp '''
''' Date 	MandiCode	Arrival		Origin 		Variety 	MinP 	MaxP 	ModalP '''

##################################################################################
#	Creating a Valid Mandi Database for analysis
##################################################################################

dfMC = pd.read_csv('../../csv_bkup/wholesaleoniondata.csv', header=None)
dfManidisChosen = pd.read_csv('../retail/mandisChosen.csv', header=None)
MandisChosen = dfManidisChosen[0].tolist()

# Pick the mandis which are chosen
dfMC[8] = dfMC.apply(lambda row: row[1] in MandisChosen, axis=1)
dfMC = dfMC[dfMC[8] == True]

# Remove the mandis with zero or NULL arrival, and if any price is reported NULL
dfMC = dfMC[dfMC[2] != 0]
dfMC = dfMC[np.isfinite(dfMC[2])]
dfMC = dfMC[np.isfinite(dfMC[5])]
dfMC = dfMC[np.isfinite(dfMC[6])]
dfMC = dfMC[np.isfinite(dfMC[7])]

# Remove the duplicates like the last time
dfMC = dfMC.drop_duplicates(subset=[0,1])


# add the day on the particular date in the dataframe
'''	Data 	CentreID 	Price 	Day '''
def StringDateToDay(x):
	dateObject = datetime.strptime(x, '%Y-%m-%d')
	return dateObject.strftime('%A')

dfMC[9] = dfMC.apply(lambda row: StringDateToDay(row[0]), axis=1)


def writeDictToCSV (filename, mydict):
	with open(filename, 'wb') as csv_file:
		writer = csv.writer(csv_file)
		for key, value in mydict.items():
			writer.writerow([key, value])
	return

#daysList = Counter(df[3].tolist())
IDList = Counter(df[1].tolist())
#writeDictToCSV('daysData.csv', daysList)
writeDictToCSV('pointsCount.csv', IDList)
