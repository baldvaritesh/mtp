import pandas as pd, csv, numpy as np , math
from datetime import datetime
from collections import Counter

''' Structure of Database File From BackUp '''
''' Data 	CentreId 	Price '''

##################################################################################
#	Creating a Valid Retail Database
##################################################################################

df = pd.read_csv('../../csv_bkup/RetailOnionData.csv', header=None)

# delete the rows with price as zero and NaN
df = df[df[2] != 0]
df = df[np.isfinite(df[2])]

# delete the rows with multiple possible entries (same date and centreId)
df = df.drop_duplicates(subset=[0,1])

# remove entries before 2006, check where the end point is
df = df.sort([0], ascending=[True])
df = df.drop(df.index[:34963])

# sort the database by dates and then by ids (both ascending)
df = df.sort([0,1], ascending=[True, True])

# add the day on the particular date in the dataframe
'''	Data 	CentreID 	Price 	Day '''
def StringDateToDay(x):
	dateObject = datetime.strptime(x, '%Y-%m-%d')
	return dateObject.strftime('%A')

df[3] = df.apply(lambda row: StringDateToDay(row[0]), axis=1)

##################################################################################
#	Analysis of the Retail Data
#	1. Note that the threshold for choosing the valid points is taken as 2000
# 	2. Important Variables: IdsPicked, df, dfPicked, dfMandis, dfCentres
##################################################################################

def writeDictToCSV (filename, mydict):
	with open(filename, 'wb') as csv_file:
		writer = csv.writer(csv_file)
		for key, value in mydict.items():
			writer.writerow([key, value])
	return

def WriteListToFile (filename, myList):
	file = open(filename, 'w')
	for item in myList:
  		file.write("%s\n" % item)
  	file.close()
  	return


''' Complete this function '''
def writeMandisToFile(filename, IdsName):
	f = open(filename, 'w')
	for key, value in IdsName.items():
	f.close()
	return 

def PickParticularIDs (threshold, mydict):
	ids = []
	for (key, value) in mydict.items():
		if value > threshold:
			ids.append(key)
	return ids

def AnalyseMissingDataByID(idChosen, df):
	df = df.sort([1,0], ascending=[True, True])
	df = df[df[1] == idChosen]
	daysSeries = df[0].tolist()
	maxValue = -1
	MissingDays = [] 
	for i in xrange(1 , len(daysSeries)):
		dateObject1 = datetime.strptime(daysSeries[i-1], '%Y-%m-%d')
		dateObject2 = datetime.strptime(daysSeries[i], '%Y-%m-%d')
		delta = ( dateObject2 - dateObject1 ).days
		MissingDays.append(delta)
		if(delta > maxValue):
			maxValue = delta
	MissingDays.append(maxValue)
	return MissingDays

def ChooseMandisForCentre(idChosen, df):
	df = df[df[5] == idChosen]
	subset = df[[0,1]]
	return [tuple(x) for x in subset.values]

def GetNameofCentres(df, IdsPicked):
	IdsName = {}
	for i in xrange(0 , len(IdsPicked)):
		dftemp = df[df[0] == IdsPicked[i]]
		IdsName[IdsPicked[i]] = {}
		IdsName[IdsPicked[i]]['name'] = dftemp[2].item()
	return IdsName

def MandisForChosenCentres(IdsPicked, IdsName, dfMandis):
	for i in xrange(0 , len(IdsPicked)):
		IdsName[IdsPicked[i]]['mandis'] = ChooseMandisForCentre(IdsPicked[i], dfMandis)
	return IdsName


#daysList = Counter(df[3].tolist())
IDList = Counter(df[1].tolist())
#writeDictToCSV('daysData.csv', daysList)
writeDictToCSV('pointsCount.csv', IDList)

# pick the subset of data frame which has points greater than 2000
IdsPicked = PickParticularIDs(2000, IDList)
'''	Data 	CentreID 	Price 	Day 	ChosenOrNot '''
df[4] = df.apply(lambda row: row[1] in IdsPicked, axis=1)
dfPicked = df[df[4] == True]
daysList = Counter(dfPicked[3].tolist())
writeDictToCSV('daysData.csv', daysList)

# Analyse the missing data by ID
for i in xrange(0 , len(IdsPicked)):
	m = AnalyseMissingDataByID(IdsPicked[i], dfPicked)
	WriteListToFile(str(IdsPicked[i]) + '.csv', m)

# Get the mandis available around the Chosen Centres
dfMandis = pd.read_csv('../../csv_bkup/mandis.csv', header=None)
dfCentres = pd.read_csv('../../csv_bkup/centres.csv', header=None)
IdsName = GetNameofCentres(dfCentres, IdsPicked)
IdsName = MandisForChosenCentres(IdsPicked, IdsName, dfMandis)
writeMandisToFile( 'mandisChosen.csv', IdsName)