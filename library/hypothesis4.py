import numpy
import csv
import matplotlib.pyplot as plt
from slopeBasedDetection import slopeBasedDetection
from slopeBasedDetection import anomalyDatesSlopeBaseddetetion
from Utility import MADThreshold
from Utility import mergeDates
from SlopeCurveBased import slopeCurveBasedDetection
from slopeBasedDetection import slopeBased
from linear_regression import linear_regressionMain
from window_correlation import anomaliesFromWindowCorrelationWithConstantlag
from Utility import intersection
import numpy as np
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
        return [item[i] for item in lstTuples]
    
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
    
    centresList = []
    testData= []
    temp1 = []
    for i in csvDataList:
        td= getColumnFromListOfTuples(i,2)  # wholesale price, indexing starts from 1
        testData.append(convertListToFloat(td))
        temp1 = getColumnFromListOfTuples(i,0)
        # print temp1
        temp2 = getColumnFromListOfTuples(i,2)
        temp2  = np.array(temp2).astype(np.float)
        temp = zip(temp1,temp2)
        centresList.append(temp)
    #print "testData" + str(testData)
    
    avgTimeSeries=findAverageTimeSeries(testData)
    avgTimeSeries = zip(temp1,avgTimeSeries)
    # print avgTimeSeries
    #print "Average Time Series :::::: "+ str(avgTimeSeries)
    
    for i,c_list in enumerate(centresList):
        # CALL SLOPE BASED
        slopeBasedResult = slopeBased(c_list,False,avgTimeSeries, False)
        # print slopeBasedResult
        slopeBasedResult = mergeDates(slopeBasedResult)
        # Correlation
        correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,avgTimeSeries)
        correlationResult = mergeDates(correlationResult)
        # Linear Regression
        lrResult = linear_regressionMain(avgTimeSeries,c_list,1)
        lrResult = mergeDates(lrResult)
        result = intersection(3,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression')
        print "Anomalies fior time-series " + str(i) + " are:"
        for (a,b,c,d,e,f,g) in result:
            print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
    
# hypothesis4Testing(1,"AhmedabadSILData.csv")
hypothesis4Testing(4,"testingCSV/AhmedabadSILData.csv","testingCSV/BengaluruSILData.csv","testingCSV/MumbaiSILData.csv","testingCSV/PatnaSILData.csv")