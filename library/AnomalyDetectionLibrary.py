import datetime
import csv

def AnomalyDetectionLibrary(startDate,granularity,fileName):
	csvDataList = [] # 2D list storing data of each file
	dt= datetime.datetime.strptime(startDate , '%Y-%m-%d')
	with open(fileName, 'rb') as f:
		reader = csv.reader(f)
		for row in reader:
			row.insert(0,dt)
			csvDataList.append(tuple(row))
			'''csvData = map(tuple, reader)
			csvData = list(csvData)
			csvData.insert(0,dt)
			csvData= tuple(csvData)
			csvDataList.append(csvData)'''
			dt = dt + datetime.timedelta(days=granularity)
	print csvDataList
	
AnomalyDetectionLibrary("2006-01-01",3,"/home/kapil/Desktop/mtp/library/testingCSV/Retailresults.csv")
