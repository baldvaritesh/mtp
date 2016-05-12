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
from Utility import intersectionOfFinalResults
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
    temp1 = []
    testData = []
    arrivalAtCentres = []
    for i in csvDataList:
        td= getColumnFromListOfTuples(i,2)  # wholesale price, indexing starts from 1
        testData.append(convertListToFloat(td))
        temp1 = getColumnFromListOfTuples(i,0)
        # print temp1
        temp2 = getColumnFromListOfTuples(i,2)
        temp2  = np.array(temp2).astype(np.float)
        temp3 = getColumnFromListOfTuples(i,3)
        temp3  = np.array(temp3).astype(np.float)
        temp = zip(temp1,temp2)
        centresList.append(temp)
        temp = zip(temp1,temp3)
        arrivalAtCentres.append(temp)
    #print "testData" + str(testData)
    
    avgTimeSeries=findAverageTimeSeries(testData)
    avgTimeSeries = zip(temp1,avgTimeSeries)
    # print avgTimeSeries
    # print "Average Time Series :::::: "+ str(avgTimeSeries)
    
    # Hashmap to save results of comparison of retail prices.
    center_anomalies_only_retail = dict()
    
    for i,c_list in enumerate(centresList):
        # CALL SLOPE BASED
        slopeBasedResult = slopeBased(c_list,False,avgTimeSeries, False,7,True,0, -1)
        # print slopeBasedResult
        slopeBasedResult = mergeDates(slopeBasedResult)
        #print 'Done slope based'
        # Correlation
        correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,avgTimeSeries)
        correlationResult = mergeDates(correlationResult)
        #print 'Done correlation based'
        # Linear Regression
        lrResult = linear_regressionMain(avgTimeSeries,c_list,1)
        lrResult = mergeDates(lrResult)
        result = intersection(3,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression')
        # Lets save these results.
        center_anomalies_only_retail[i] = result
        '''
        print "Anomalies fior time-series " + str(i) + " are:"
        for (a,b,c,d,e,f,g) in result:
            print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
        '''
        
    
    
    # Now lets consider arrival of each center and see whether these anomalies are due to that or not
    # Anomalies from Arrival vs Retail
    center_anomalies_arr_vs_retail = dict()
    for i,c_list in enumerate(arrivalAtCentres):
        # CALL SLOPE BASED
        slopeBasedResult = slopeBased(c_list,False,centresList[i], False,7,True,0, 1)
        slopeBasedResult = mergeDates(slopeBasedResult)
        # Correlation
        correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,centresList[i],15,15,False)
        correlationResult = mergeDates(correlationResult)
        # Linear Regression
        lrResult = linear_regressionMain(c_list,centresList[i],1)
        lrResult = mergeDates(lrResult)
        #print lrResult
        result = intersection(3,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression')
        # Lets save these results.
        center_anomalies_arr_vs_retail[i] = result
        '''
        print "Anomalies fior time-series with arrival " + str(i) + " are:"
        for (a,b,c,d,e,f,g) in result:
            print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
        '''
    
    # Time to analyse both results:
    for i in range(0,len(arrivalAtCentres)):
        print "\n\n\n\nFOR CENTER " + str(i) + "  INTERSECTION OF RETAIL VS AVG AND RETAIL VS ARRIVAL IS..... \n\n"
        retailVSreatil = center_anomalies_only_retail[i]
        reatilVSarrival = center_anomalies_arr_vs_retail[i]
        print "Retail Results ::::::: "
        print retailVSreatil
        print "Retail vs Arrival Results ::::::: "
        print reatilVSarrival
        intersect = intersectionOfFinalResults(reatilVSarrival,retailVSreatil)
        for (a,b,c,d,e,f,g) in intersect:
            print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
        print "-----------------------------------------------------------------------------------------------------------------------"
        
    
    
# hypothesis4Testing(1,"AhmedabadSILData.csv")
# For Centers
hypothesis4Testing(5,"testingCSV/AhmedabadSILData.csv","testingCSV/BengaluruSILData.csv","testingCSV/MumbaiSILData.csv","testingCSV/PatnaSILData.csv","testingCSV/DelhiSILData.csv")


