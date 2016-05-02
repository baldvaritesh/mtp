import numpy
import csv
import matplotlib.pyplot as plt
from slopeBasedDetection import slopeBasedDetection
from slopeBasedDetection import anomalyDatesSlopeBaseddetetion
from Utility import MADThreshold
from Utility import mergeDates
from SlopeCurveBased import slopeCurveBasedDetection

'''

This function takes 1 argument:

timeSeriesCollection: 2D array of float elements.
Each row is one timeseries.

returns average of all timeseries.

For example let,
timeSeriesCollection: [
    [1,2,3], # Timeseries 1
    [4,5,6], # Timeseries 2
    [7,8,9] # Timeseries 3
]

This function will return,

[4,5,6]

'''
def findAverageTimeSeries(timeSeriesCollection):
    return [sum(e)/len(e) for e in zip(* timeSeriesCollection)]

def getColumnFromListOfTuples(lstTuples,i):
    if len(lstTuples) == 0:
        return []
    elif len(lstTuples[0])< i-1 :
        return []
    else:
        return [item[i-1] for item in lstTuples]
    
def convertListToFloat(li):
    return [float(i) for i in li]

'''
This function multiple arguments:

numOfFiles: Indicates the number of files that needs to be passed to this function.
timeSeriesFileNames: Path of all files.

CSV Files has following format.
It has 4 columns:
Date, Wholesale Price, Retail Price, Arrival

'''
def hypothesis4Testing(numOfFiles, *timeSeriesFileNames):
    if len(timeSeriesFileNames) != numOfFiles:
        print "Number of files mentioned do not match the specified files provided"
        return
    
    csvDataList = [] # 2D list storing data of each file
    for fileName in timeSeriesFileNames:
        with open(fileName, 'rb') as f:
            reader = csv.reader(f)
            csvData = map(tuple, reader)
        csvDataList.append(csvData)
    
    testData= []
    for i in csvDataList:
        td= getColumnFromListOfTuples(i,2)  # wholesale price, indexing starts from 1
        testData.append(convertListToFloat(td))
    #print "testData" + str(testData)
    
    avgTimeSeries=findAverageTimeSeries(testData)
    #print "Average Time Series :::::: "+ str(avgTimeSeries)
    
    #Finding anomaly dates for every time series with average time series
    count=0
    tcases=0  # Number of Anomalies
    h4res=[]
    for timeSeries in testData:
        #print "Value of i ::::::::::::::::::::::::: "+ str(count)
        #ser = findDiffSeries(i,1)
        #print "Result of Ser::::::::::::::::"+ str(ser)
        #(r,s)=MADThreshold(ser)
        #print "Result of MAD TEST :::::::::::::::::::::::::"+ str(r)+ ":::"+str(s)
        #p =[x for x in ser if x > 100 or x < -100]
        #print "Exception list :::::::::::"+ str(p)
        #print "length of exception list ::::::::::::::"+ str(len(p))
        #plt.plot(ser)
        #plt.show()
        
        #temp= slopeCurveBasedDetection(i,avgTimeSeries,1)
        temp= slopeBasedDetection(timeSeries,True,avgTimeSeries,True,7,True,0,0) # Returns anomaly points
        tcases=tcases+len(temp)
        #print "TEMP :::::::::::::::::::::::::::::::::::::::::::::"+ str(csvDataList[count])
        res= anomalyDatesSlopeBaseddetetion(temp,csvDataList[count]) # returns date of anomaly
        h4res.append( (count,res)) # (series no. , anomaly dates)
        #h4res.append( (count,temp))
        count=count+1
    #print "Final Result ::::::::::::::::"+ str(h4res)
    mergedWindows = mergeDates(h4res[0][1]) # Finds overlapped dates and merges windows
    print "Final Reported Anomalies ::::::::::::::::::: "+ str(len(mergedWindows))
    
    
# hypothesis4Testing(1,"AhmedabadSILData.csv")
hypothesis4Testing(4,"AhmedabadSILData.csv","BengaluruSILData.csv","MumbaiSILData.csv","PatnaSILData.csv")