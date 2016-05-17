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
from DatabaseConn import fetchNewsForCenter
from Utility import placeMapping
from Utility import getGBAResultsRvA
from Utility import getGBAResultsRvR
from Utility import findAverageTimeSeries
from Utility import getColumnFromListOfTuples
from Utility import convertListToFloat
from Utility import plotGraphForHypothesis
import datetime


'''
This function takes 2 arguments:

numOfFiles: Indicates the number of files that needs to be passed to this function.
timeSeriesFileNames: Path of all files.

CSV Files has following format.
It has 4 columns:
Date, Wholesale Price, Retail Price, Arrival

'''
def hypothesisForCenter(numOfFiles, *timeSeriesFileNames):
    if len(timeSeriesFileNames) != numOfFiles:
        print "Number of files mentioned do not match the specified files provided"
        return
    
    csvDataList = [] # 2D list storing data of each file
    for fileName in timeSeriesFileNames:
        with open(fileName, 'rb') as f:
            reader = csv.reader(f)
            csvData = map(tuple, reader)
        csvDataList.append(csvData)
    
    retailList = []
    wholesaleList = []
    arrivalList = []    
    
    temp1 = []
    retailListWithNoDates = []
    
    for i in csvDataList:
        td= getColumnFromListOfTuples(i,2)
        retailListWithNoDates.append(convertListToFloat(td))
        
        # Extracting Date series
        temp1 = getColumnFromListOfTuples(i,0)
        
        # Extracting arrival for all centers
        temp3 = getColumnFromListOfTuples(i,3)
        temp3  = np.array(temp3).astype(np.float)
        temp = zip(temp1,temp3)
        arrivalList.append(temp)
        
        # Extracting retail price for all centers
        temp2 = getColumnFromListOfTuples(i,2)
        temp2  = np.array(temp2).astype(np.float)
        temp = zip(temp1,temp2)
        retailList.append(temp)        
        
        # Extracting wholesale price for all centers
        temp4 = getColumnFromListOfTuples(i,1)
        temp4  = np.array(temp4).astype(np.float)
        temp4 = zip(temp1,temp4)
        wholesaleList.append(temp4)
    
    # Find average of all retail prices
    avgRetailTimeSeries = findAverageTimeSeries(retailListWithNoDates)
    avgRetailTimeSeries = zip(temp1,avgRetailTimeSeries)
    
    # Hashmap to save results of comparison of retail prices.
    center_anomalies_only_retail = dict()
    
    slopeBasedResult=[]
    correlationResult=[]
    lrResult=[]
    for i,c_list in enumerate(retailList):
        
        # Hypothesis 1: START
        
        # CALL SLOPE BASED
        slopeBasedResult = slopeBased(c_list,False,avgRetailTimeSeries, False,7,True,0, -1)
        slopeBasedResult = mergeDates(slopeBasedResult)     
        
        # Correlation
        correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,avgRetailTimeSeries)
        correlationResult = mergeDates(correlationResult)
        
        # Linear Regression
        lrResult = linear_regressionMain(avgRetailTimeSeries,c_list,1)
        lrResult = mergeDates(lrResult)
        
        # Result for Hypothesis 1
        # result = intersection(3,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression')
        result = intersection(2,correlationResult,'correlation',lrResult,'linear_regression')
        center_anomalies_only_retail[i] = result
        
        # Hypothesis 1: END
        
        # Plot Graph for i'th center, it requires 4 args. We have 3. We need to get dates for news articles
        (news_article_found, all_articles) = fetchNewsForCenter(result,i)
        news_article_found_dates = getColumnFromListOfTuples(news_article_found, 1)
        plotGraphForHypothesis(c_list, avgRetailTimeSeries, result, news_article_found_dates)
        
        
        
    # Now lets consider arrival of each center and see whether these anomalies are due to that or not
    # Anomalies from Arrival vs Retail
    center_anomalies_arr_vs_retail = dict()
    for i,c_list in enumerate(arrivalList):
        
        # Hypothesis 2: START        
        
        # CALL SLOPE BASED
        slopeBasedResult = slopeBased(c_list,False,retailList[i], False,7,True,0, 1)
        slopeBasedResult = mergeDates(slopeBasedResult)
        
        # Correlation
        correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,retailList[i],15,15,False)
        correlationResult = mergeDates(correlationResult)
        
        # Linear Regression
        lrResult = linear_regressionMain(c_list,retailList[i],1)
        lrResult = mergeDates(lrResult)
        
        # Result for Hypothesis 2
        result = intersection(3,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression')
        center_anomalies_arr_vs_retail[i] = result
        
        # Hypothesis 2: END
    
hypothesisForCenter(5,"testingCSV/AhmedabadSILData.csv","testingCSV/BengaluruSILData.csv","testingCSV/MumbaiSILData.csv","testingCSV/PatnaSILData.csv","testingCSV/DelhiSILData.csv")


