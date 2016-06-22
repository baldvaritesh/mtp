import numpy
import csv
import sys
import matplotlib.pyplot as plt
from slopeBasedDetection import slopeBased
from linear_regression import linear_regressionMain
from window_correlation import anomaliesFromWindowCorrelationWithConstantlag
import numpy as np
from Utility import fetchNewsForCenter,placeMapping, getGBAResultsRvA, getGBAResultsRvR, findAverageTimeSeries, getColumnFromListOfTuples, convertListToFloat, plotGraphForHypothesis, resultOfOneMethod, concateLists, writeToCSV, getDiffStatsOfNewsArticles, statsPrintHelperIntersect, statsPrintHelperUnion,statsPrintHelperAllCentersUnion, intersection, intersectionOfFinalResults, MADThreshold, mergeDates, union, intersect, getYearWiseStats, plotGraphForHypothesisArrival, processListForGB, newsAnomalyDiffDays
import datetime
from multiVariateTimeseries import csvTransform
from multiVariateTimeseries import multivaraiateAnalysis
from callingGraphBasedAnomaly import graphBasedAnomalyMain


'''
This function takes 2 arguments:

numOfFiles: Indicates the number of files that needs to be passed to this function.
timeSeriesFileNames: Path of all files.

CSV Files has following format.
It has 4 columns:
Date, Wholesale Price, Retail Price, Arrival

'''

defaultThresholdCentre1 = [6, 14, -5, 100, 6, 50, -7, 100]
defaultThresholdCentre2 = [6, 14, -4, 100, 6, 20, -5, 100]
userThreshold = False


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
    
    # graphBasedAnomalyMain(retailList,i,50)
    # print "DONE"
    
    # Find average of all retail prices
    avgRetailTimeSeries = findAverageTimeSeries(retailListWithNoDates)
    avgRetailTimeSeries = zip(temp1,avgRetailTimeSeries)
    
    #forecast retail prices of all centers based on the retail prices at differnet centers --Reshma
    lstRetail= concateLists(retailListWithNoDates)
    
    writeToCSV(lstRetail,"testingCSV/AllRetailData.csv")
    args = ['testingCSV/AllRetailData.csv','FALSE',str(len(retailListWithNoDates)),'retail']
    multivaraiateAnalysis(args)
    
    
    # Hashmap to save results of comparison of retail prices vs average
    RvsR_anomalies_slope = dict()
    RvsR_anomalies_correlation = dict()
    RvsR_anomalies_linear_regression = dict()
    RvsR_anomalies_graph_based = dict()
    RvsR_anomalies_multiple_arima = dict()
    RvsR_anomalies_union_of_H1 = dict()
    RvsR_anomalies_union_of_H3 = dict()
    RvsR_anomalies_intersection = dict()   
    
    # Hashmap to save results of comparison of retail prices vs arrival  
    RvsA_anomalies_slope = dict()
    RvsA_anomalies_correlation = dict()
    RvsA_anomalies_linear_regression = dict()
    RvsA_anomalies_graph_based = dict()
    RvsA_anomalies_multiple_arima = dict()
    RvsA_anomalies_union_of_H1 = dict()
    RvsA_anomalies_union_of_H3 = dict()
    RvsA_anomalies_intersection = dict()
    
    # Hashmap to save results of comparison of retail prices vs wholesale  
    RvsW_anomalies_slope = dict()
    RvsW_anomalies_correlation = dict()
    RvsW_anomalies_linear_regression = dict()
    RvsW_anomalies_graph_based = dict()
    RvsW_anomalies_multiple_arima = dict()
    RvsW_anomalies_union_of_H1 = dict()
    RvsW_anomalies_union_of_H3 = dict()
    RvsW_anomalies_intersection = dict()
    
    # Hashmap to save results of comparison of wholesale prices vs arrival  
    WvsA_anomalies_slope = dict()
    WvsA_anomalies_correlation = dict()
    WvsA_anomalies_linear_regression = dict()
    WvsA_anomalies_graph_based = dict()
    WvsA_anomalies_multiple_arima = dict()
    WvsA_anomalies_union_of_H1 = dict()
    WvsA_anomalies_union_of_H3 = dict()
    WvsA_anomalies_intersection = dict()
    
    # To save news
    all_articles = dict()
    
    print "STARTING WITH RETAIL VS AVERAGE \n\n\n"
    
    for i,c_list in enumerate(retailList):
        
        # Hypothesis 1: START
        if(userThreshold):
            if(i==0):
                slopeBasedResult = slopeBased(c_list,False,avgRetailTimeSeries, False,7,False,defaultThresholdCentre1[0], 1)
            elif(i==1):
                slopeBasedResult = slopeBased(c_list,False,avgRetailTimeSeries, False,7,False,defaultThresholdCentre2[0], 1)
            slopeBasedResult = mergeDates(slopeBasedResult)     
            
            # Correlation
            correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,avgRetailTimeSeries)
            correlationResult = mergeDates(correlationResult)
            
            # Linear Regression
            if(i==0):
                lrResult = linear_regressionMain(avgRetailTimeSeries,c_list,1, False, defaultThresholdCentre1[1])
            elif(i==1):
                lrResult = linear_regressionMain(avgRetailTimeSeries,c_list,1, False, defaultThresholdCentre2[1])
            lrResult = mergeDates(lrResult)
        else:            
            # CALL SLOPE BASED
            slopeBasedResult = slopeBased(c_list,False,avgRetailTimeSeries, False,7,True,0, 1)        
            slopeBasedResult = mergeDates(slopeBasedResult)     
            
            # Correlation
            correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,avgRetailTimeSeries)
            correlationResult = mergeDates(correlationResult)
            
            # Linear Regression
            lrResult = linear_regressionMain(avgRetailTimeSeries,c_list,1)
            lrResult = mergeDates(lrResult)
        
        # Result for Hypothesis 1
        slopeBased_result = resultOfOneMethod(slopeBasedResult)
        correlationBased_result = resultOfOneMethod(correlationResult)
        linearRegression_result = resultOfOneMethod(lrResult)
        union_result_of_H1 = union(3,slopeBased_result,correlationBased_result,linearRegression_result)
        
        # Hypothesis 1: END
        
        # Hypothesis 3 For Reatil vs AVG: START
        retailListGB = processListForGB(retailList)
        graphBasedAnomaly = graphBasedAnomalyMain(retailListGB,i,300)
        # graphBasedAnomaly = []
        graphBasedAnomaly_result = resultOfOneMethod(graphBasedAnomaly)
        
        
        #Since 60% data is used for modelling and rest is used to forecast
        startDatePoint =int(0.60*len(retailListWithNoDates[0]))
        multiVariate_Anomaly_Result = csvTransform("testingCSV/retail"+str(i+1)+".csv",temp1[startDatePoint])
        # multiVariate_Anomaly_Result = []
        multiple_arima_result = resultOfOneMethod(multiVariate_Anomaly_Result)
        
        union_result_of_H3 = union(2,graphBasedAnomaly_result, multiple_arima_result)
        
        intersection_result_with_H3 = intersect(union_result_of_H1,union_result_of_H3)
        # Hypothesis 3 For Reatil vs AVG: END
        
        # Get stats of news articles for each method
        (filteredResult_slope_based, slopeBased_news_article_result,all_articles_slope_based) = fetchNewsForCenter(slopeBased_result, i)        
        (filteredResult_correlation_based, correlationBased_news_article_result,all_articles_correlationBased) = fetchNewsForCenter(correlationBased_result, i)
        (filteredResult_linear_regression, linearRegression_news_article_result,all_articles_linearRegression) = fetchNewsForCenter(linearRegression_result, i)
        (filteredResult_graph_based, graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly) = fetchNewsForCenter(graphBasedAnomaly_result, i)
        (filteredResult_multiple_arima, multiple_arima_news_article_result, all_articles_multiple_arima) = fetchNewsForCenter(multiple_arima_result, i)
        (filteredResult_union_of_h1, union_result_of_H1_news_article,all_articles_union_result_of_H1) = fetchNewsForCenter(union_result_of_H1, i)
        (filteredResult_union_of_h3, union_result_of_H3_news_article, all_articles_union_result_of_H3) = fetchNewsForCenter(union_result_of_H3, i)
        (filteredResult_intersection, intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3) = fetchNewsForCenter(intersection_result_with_H3, i)
        
       
        # Plot Graph for i'th center
        # plotGraphForHypothesis(c_list, avgRetailTimeSeries, slopeBased_result, filteredResult_slope_based, all_articles_graphBasedAnomaly)
        # plotGraphForHypothesis(c_list, avgRetailTimeSeries, linearRegression_result, filteredResult_linear_regression, all_articles_graphBasedAnomaly)
        # plotGraphForHypothesis(c_list, avgRetailTimeSeries, graphBasedAnomaly_result, filteredResult_graph_based, all_articles_graphBasedAnomaly)
        print "Graph of System Result for Retail vs Average"
        plotGraphForHypothesis(c_list, avgRetailTimeSeries, intersection_result_with_H3, filteredResult_intersection, all_articles_intersection_result_with_H3)
        
        # Save system results in dictionary to process further
        RvsR_anomalies_union_of_H3[2*i]  = union_result_of_H3
        RvsR_anomalies_union_of_H1[2*i] = union_result_of_H1
        RvsR_anomalies_intersection[2*i] = intersection_result_with_H3
        RvsR_anomalies_slope[2*i] = slopeBased_result
        RvsR_anomalies_correlation[2*i] = correlationBased_result
        RvsR_anomalies_linear_regression[2*i] = linearRegression_result
        RvsR_anomalies_graph_based[2*i] = graphBasedAnomaly_result
        RvsR_anomalies_multiple_arima[2*i] = multiple_arima_result
        
        # Save news matched
        RvsR_anomalies_union_of_H3[2*i+1]  = filteredResult_union_of_h3
        RvsR_anomalies_union_of_H1[2*i+1] = filteredResult_union_of_h1
        RvsR_anomalies_intersection[2*i+1] = filteredResult_intersection
        RvsR_anomalies_slope[2*i+1] = filteredResult_slope_based
        RvsR_anomalies_correlation[2*i+1] = filteredResult_correlation_based
        RvsR_anomalies_linear_regression[2*i+1] = filteredResult_linear_regression
        RvsR_anomalies_graph_based[2*i+1] = filteredResult_graph_based
        RvsR_anomalies_multiple_arima[2*i+1] = filteredResult_multiple_arima
        
        all_articles[i] = all_articles_correlationBased
    
    localNationHelper(retailList[0], avgRetailTimeSeries, retailList[1], avgRetailTimeSeries, RvsR_anomalies_intersection[2*0], RvsR_anomalies_intersection[2*1])
  
    print "END OF RETAIL VS AVERAGE \n\n\n"
    
    
    print "STARTING WITH RETAIL VS ARRIVAL \n\n\n"
    # Now lets consider arrival of each center and see whether these anomalies are due to that or not
    # Anomalies from Arrival vs Retail
    center_anomalies_arr_vs_retail = dict()
    for i,c_list in enumerate(arrivalList):
        
        # Hypothesis 2: START        
        if(userThreshold):
            # CALL SLOPE BASED
            if(i==0):
                slopeBasedResult = slopeBased(retailList[i],False,c_list, False,7,False,defaultThresholdCentre1[2], -1)
            elif(i==1):
                slopeBasedResult = slopeBased(retailList[i],False,c_list, False,7,False,defaultThresholdCentre2[2], -1)
            slopeBasedResult = mergeDates(slopeBasedResult)
            
            # Correlation
            correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,retailList[i],15,15,False)
            correlationResult = mergeDates(correlationResult)
            
            # Linear Regression
            if(i==0):
                lrResult = linear_regressionMain(c_list,retailList[i],1, False, defaultThresholdCentre1[3])
            elif(i==1):
                lrResult = linear_regressionMain(c_list,retailList[i],1, False, defaultThresholdCentre2[3])
            lrResult = mergeDates(lrResult)
        else:            
            # CALL SLOPE BASED
            slopeBasedResult = slopeBased(retailList[i],False,c_list, False,7,True,0, -1)
            slopeBasedResult = mergeDates(slopeBasedResult)
            
            # Correlation
            correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,retailList[i],15,15,False)
            correlationResult = mergeDates(correlationResult)
            
            # Linear Regression
            lrResult = linear_regressionMain(c_list,retailList[i],1)
            lrResult = mergeDates(lrResult)
        

        # Result for Hypothesis 2
        slopeBased_result = resultOfOneMethod(slopeBasedResult)
        correlationBased_result = resultOfOneMethod(correlationResult)
        linearRegression_result = resultOfOneMethod(lrResult)
        union_result_of_H1 = union(3,slopeBased_result,correlationBased_result,linearRegression_result)
        
        # Hypothesis 2: END
        
        # Hypothesis 3 For Reatil vs ARRIVAL: START
        temp5 = []
        temp5.append(retailList[i])
        temp5.append(arrivalList[i])
        temp5 = processListForGB(temp5)
        graphBasedAnomaly = graphBasedAnomalyMain(temp5, 0,500)
        # graphBasedAnomaly = []
        graphBasedAnomaly_result = resultOfOneMethod(graphBasedAnomaly)
        
        
        lstWSRetailArrival =[]
        lstWSRetailArrival.append(getColumnFromListOfTuples(wholesaleList[i],1))
        lstWSRetailArrival.append(getColumnFromListOfTuples(retailList[i],1))
        lstWSRetailArrival.append(getColumnFromListOfTuples(arrivalList[i],1))
        lstRetail= concateLists(lstWSRetailArrival)
        #print lstRetail
        
        writeToCSV(lstRetail,"testingCSV/AllDataForeCast"+str(i+1)+".csv")
        args = ['testingCSV/AllDataForeCast'+str(i+1)+'.csv','FALSE','3','RetailWsArrival']
        multivaraiateAnalysis(args)
        
        multiVariate_Anomaly_Result = csvTransform('testingCSV/RetailWsArrival2.csv',temp1[startDatePoint])
        # multiVariate_Anomaly_Result = []
        multiple_arima_result = resultOfOneMethod(multiVariate_Anomaly_Result)
        union_result_of_H3 = union(2,graphBasedAnomaly_result, multiple_arima_result)
        
        intersection_result_with_H3 = intersect(union_result_of_H1,union_result_of_H3)
        
        #print multiVariate_Anomaly_Result
                
        # Hypothesis 3 For Reatil vs ARRIVAL: END
        
        # Get stats of news articles for each method        
        (filteredResult_slope_based, slopeBased_news_article_result,all_articles_slope_based) = fetchNewsForCenter(slopeBased_result, i)
        (filteredResult_correlation_based, correlationBased_news_article_result,all_articles_correlationBased) = fetchNewsForCenter(correlationBased_result, i)
        (filteredResult_linear_regression, linearRegression_news_article_result,all_articles_linearRegression) = fetchNewsForCenter(linearRegression_result, i)
        (filteredResult_graph_based, graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly) = fetchNewsForCenter(graphBasedAnomaly_result, i)
        (filteredResult_multiple_arima, multiple_arima_news_article_result, all_articles_multiple_arima) = fetchNewsForCenter(multiple_arima_result, i)
        (filteredResult_union_of_h1, union_result_of_H1_news_article,all_articles_union_result_of_H1) = fetchNewsForCenter(union_result_of_H1, i)
        (filteredResult_union_of_h3, union_result_of_H3_news_article, all_articles_union_result_of_H3) = fetchNewsForCenter(union_result_of_H3, i)
        (filteredResult_intersection, intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3) = fetchNewsForCenter(intersection_result_with_H3, i)
        
        
        # Plot Graph for i'th center
        # plotGraphForHypothesisArrival(c_list, retailList[i], slopeBased_result, filteredResult_slope_based, all_articles_graphBasedAnomaly)
        # plotGraphForHypothesisArrival(c_list, retailList[i], linearRegression_result, filteredResult_linear_regression, all_articles_graphBasedAnomaly)
        # plotGraphForHypothesisArrival(c_list, retailList[i], graphBasedAnomaly_result, filteredResult_graph_based, all_articles_graphBasedAnomaly)
        print "Graph of System result Retail vs Arrival"
        plotGraphForHypothesis(c_list, retailList[i], intersection_result_with_H3, filteredResult_intersection, all_articles_intersection_result_with_H3)
        
        # Save system results in dictionary to process further
        RvsA_anomalies_union_of_H3[2*i]  = union_result_of_H3
        RvsA_anomalies_union_of_H1[2*i] = union_result_of_H1
        RvsA_anomalies_intersection[2*i] = intersection_result_with_H3
        RvsA_anomalies_slope[2*i] = slopeBased_result
        RvsA_anomalies_correlation[2*i] = correlationBased_result
        RvsA_anomalies_linear_regression[2*i] = linearRegression_result
        RvsA_anomalies_graph_based[2*i] = graphBasedAnomaly_result
        RvsA_anomalies_multiple_arima[2*i] = multiple_arima_result
        
        # Save news matched
        RvsA_anomalies_union_of_H3[2*i+1]  = filteredResult_union_of_h3
        RvsA_anomalies_union_of_H1[2*i+1] = filteredResult_union_of_h1
        RvsA_anomalies_intersection[2*i+1] = filteredResult_intersection
        RvsA_anomalies_slope[2*i+1] = filteredResult_slope_based
        RvsA_anomalies_correlation[2*i+1] = filteredResult_correlation_based
        RvsA_anomalies_linear_regression[2*i+1] = filteredResult_linear_regression
        RvsA_anomalies_graph_based[2*i+1] = filteredResult_graph_based
        RvsA_anomalies_multiple_arima[2*i+1] = filteredResult_multiple_arima
    
    localNationHelper(arrivalList[0], retailList[0], arrivalList[1], retailList[1], RvsA_anomalies_intersection[2*0], RvsA_anomalies_intersection[2*1], True)
    print "END OF RETAIL VS ARRIVAL \n\n\n"
    
    
    
    print "STARTING WITH RETAIL VS WHOLESALE \n\n\n"
    
    for i,c_list in enumerate(retailList):
        
        # Hypothesis 1: START
        if(userThreshold):
            # CALL SLOPE BASED
            if(i==0):
                slopeBasedResult = slopeBased(c_list,False,wholesaleList[i], False,7,False,defaultThresholdCentre1[4], 1)
            elif(i==1):
                slopeBasedResult = slopeBased(c_list,False,wholesaleList[i], False,7,False,defaultThresholdCentre2[4], 1)
            slopeBasedResult = mergeDates(slopeBasedResult)     
            
            # Correlation
            correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,wholesaleList[i])
            correlationResult = mergeDates(correlationResult)
            
            # Linear Regression
            if(i==0):
                lrResult = linear_regressionMain(wholesaleList[i],c_list,1, False, defaultThresholdCentre1[5])
            elif(i==1):
                lrResult = linear_regressionMain(wholesaleList[i],c_list,1, False, defaultThresholdCentre2[5])
            lrResult = mergeDates(lrResult)
        else:            
            # CALL SLOPE BASED
            slopeBasedResult = slopeBased(c_list,False,wholesaleList[i], False,7,True,0, 1)
            slopeBasedResult = mergeDates(slopeBasedResult)     
            
            # Correlation
            correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,wholesaleList[i])
            correlationResult = mergeDates(correlationResult)
            
            # Linear Regression
            lrResult = linear_regressionMain(wholesaleList[i],c_list,1)
            lrResult = mergeDates(lrResult)
            
        
        
        # Result for Hypothesis 1
        slopeBased_result = resultOfOneMethod(slopeBasedResult)
        correlationBased_result = resultOfOneMethod(correlationResult)
        linearRegression_result = resultOfOneMethod(lrResult)
        union_result_of_H1 = union(3,slopeBased_result,correlationBased_result,linearRegression_result)
        
        # Hypothesis 1: END
        
        # Hypothesis 3 For Reatil vs AVG: START
        temp6 = []
        temp6.append(c_list)
        temp6.append(wholesaleList[i])
        temp6 = processListForGB(temp6)
        graphBasedAnomaly = graphBasedAnomalyMain(temp6,0,300)
        # graphBasedAnomaly  = []
        graphBasedAnomaly_result = resultOfOneMethod(graphBasedAnomaly)
        
        lstCentre=[]
        lstCentre.append(getColumnFromListOfTuples(c_list,1))
        lstCentre.append(getColumnFromListOfTuples(wholesaleList[i],1))
        lstCentre= concateLists(lstCentre)
        #print lstRetail
        
        writeToCSV(lstCentre,"testingCSV/RetailWS"+str(i+1)+".csv")
        args = ['testingCSV/RetailWS'+str(i+1)+'.csv','FALSE','2','RetailWSOutput']
        multivaraiateAnalysis(args)
          
        #Since 60% data is used for modelling and rest is used to forecast
        startDatePoint =int(0.60*len(c_list))
        multiVariate_Anomaly_Result = csvTransform("testingCSV/RetailWSOutput"+str(1)+".csv",temp1[startDatePoint])
        # multiVariate_Anomaly_Result = []
        multiple_arima_result = resultOfOneMethod(multiVariate_Anomaly_Result)
        
        union_result_of_H3 = union(2,graphBasedAnomaly_result, multiple_arima_result)
        
        intersection_result_with_H3 = intersect(union_result_of_H1,union_result_of_H3)
        # Hypothesis 3 For Reatil vs AVG: END
        
        # Get stats of news articles for each method
        (filteredResult_slope_based, slopeBased_news_article_result,all_articles_slope_based) = fetchNewsForCenter(slopeBased_result, i)
        (filteredResult_correlation_based, correlationBased_news_article_result,all_articles_correlationBased) = fetchNewsForCenter(correlationBased_result, i)
        (filteredResult_linear_regression, linearRegression_news_article_result,all_articles_linearRegression) = fetchNewsForCenter(linearRegression_result, i)
        (filteredResult_graph_based, graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly) = fetchNewsForCenter(graphBasedAnomaly_result, i)
        (filteredResult_multiple_arima, multiple_arima_news_article_result, all_articles_multiple_arima) = fetchNewsForCenter(multiple_arima_result, i)
        (filteredResult_union_of_h1, union_result_of_H1_news_article,all_articles_union_result_of_H1) = fetchNewsForCenter(union_result_of_H1, i)
        (filteredResult_union_of_h3, union_result_of_H3_news_article, all_articles_union_result_of_H3) = fetchNewsForCenter(union_result_of_H3, i)
        (filteredResult_intersection, intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3) = fetchNewsForCenter(intersection_result_with_H3, i)
        
        
        # Plot Graph for i'th center
        # plotGraphForHypothesis(c_list, wholesaleList[i], slopeBased_result, filteredResult_slope_based, all_articles_graphBasedAnomaly)
        # plotGraphForHypothesis(c_list, wholesaleList[i], linearRegression_result, filteredResult_linear_regression, all_articles_graphBasedAnomaly)
        # plotGraphForHypothesis(c_list, wholesaleList[i], graphBasedAnomaly_result, filteredResult_graph_based, all_articles_graphBasedAnomaly)
        
        print "System results for Retail vs Wholesale"
        plotGraphForHypothesis(c_list, wholesaleList[i], intersection_result_with_H3, filteredResult_intersection, all_articles_intersection_result_with_H3)
        
        # Save system results in dictionary to process further
        RvsW_anomalies_union_of_H3[2*i]  = union_result_of_H3
        RvsW_anomalies_union_of_H1[2*i] = union_result_of_H1
        RvsW_anomalies_intersection[2*i] = intersection_result_with_H3
        RvsW_anomalies_slope[2*i] = slopeBased_result
        RvsW_anomalies_correlation[2*i] = correlationBased_result
        RvsW_anomalies_linear_regression[2*i] = linearRegression_result
        RvsW_anomalies_graph_based[2*i] = graphBasedAnomaly_result
        RvsW_anomalies_multiple_arima[2*i] = multiple_arima_result
        
        # Save news matched
        RvsW_anomalies_union_of_H3[2*i+1]  = filteredResult_union_of_h3
        RvsW_anomalies_union_of_H1[2*i+1] = filteredResult_union_of_h1
        RvsW_anomalies_intersection[2*i+1] = filteredResult_intersection
        RvsW_anomalies_slope[2*i+1] = filteredResult_slope_based
        RvsW_anomalies_correlation[2*i+1] = filteredResult_correlation_based
        RvsW_anomalies_linear_regression[2*i+1] = filteredResult_linear_regression
        RvsW_anomalies_graph_based[2*i+1] = filteredResult_graph_based
        RvsW_anomalies_multiple_arima[2*i+1] = filteredResult_multiple_arima
  
    
    localNationHelper(retailList[0], wholesaleList[0], retailList[1], wholesaleList[1], RvsW_anomalies_intersection[2*0], RvsW_anomalies_intersection[2*1])
    print "END OF RETAIL VS WHOLESALE \n\n\n"
    
    
    
    print "STARTING WITH WHOLESALE VS ARRIVAL \n\n\n"
    # Now lets consider arrival of each center and see whether these anomalies are due to that or not
    # Anomalies from Arrival vs Retail
    center_anomalies_arr_vs_retail = dict()
    for i,c_list in enumerate(arrivalList):
        
        # Hypothesis 2: START        
        if(userThreshold):
            # CALL SLOPE BASED
            if(i==0):
                slopeBasedResult = slopeBased(wholesaleList[i],False,c_list, False,7,False,defaultThresholdCentre1[6], -1)
            elif(i==1):
                slopeBasedResult = slopeBased(wholesaleList[i],False,c_list, False,7,False,defaultThresholdCentre2[6], -1)
            slopeBasedResult = mergeDates(slopeBasedResult)
            
            # Correlation
            correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,wholesaleList[i],15,15,False)
            correlationResult = mergeDates(correlationResult)
            
            # Linear Regression
            if(i==0):
                lrResult = linear_regressionMain(c_list,wholesaleList[i],1, False,defaultThresholdCentre1[7])
            elif(i==1):
                lrResult = linear_regressionMain(c_list,wholesaleList[i],1, False,defaultThresholdCentre2[7])
            lrResult = mergeDates(lrResult)
        else:            
            # CALL SLOPE BASED
            slopeBasedResult = slopeBased(wholesaleList[i],False,c_list, False,7,True,0, -1)
            slopeBasedResult = mergeDates(slopeBasedResult)
            
            # Correlation
            correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,wholesaleList[i],15,15,False)
            correlationResult = mergeDates(correlationResult)
            
            # Linear Regression
            lrResult = linear_regressionMain(c_list,wholesaleList[i],1)
            lrResult = mergeDates(lrResult)       
        
        

        # Result for Hypothesis 2
        slopeBased_result = resultOfOneMethod(slopeBasedResult)
        correlationBased_result = resultOfOneMethod(correlationResult)
        linearRegression_result = resultOfOneMethod(lrResult)
        union_result_of_H1 = union(3,slopeBased_result,correlationBased_result,linearRegression_result)
        
        # Hypothesis 2: END
        
        # Hypothesis 3 For Reatil vs ARRIVAL: START
        temp5 = []
        temp5.append(wholesaleList[i])
        temp5.append(arrivalList[i])
        temp5 = processListForGB(temp5)
        graphBasedAnomaly = graphBasedAnomalyMain(temp5, 0,500)
        # graphBasedAnomaly = []
        graphBasedAnomaly_result = resultOfOneMethod(graphBasedAnomaly)
        
        lstCentre =[]
        lstCentre.append(getColumnFromListOfTuples(wholesaleList[i],1))
        lstCentre.append(getColumnFromListOfTuples(arrivalList[i],1))
        lstCentre= concateLists(lstCentre)
        #print lstRetail
        
        writeToCSV(lstCentre,"testingCSV/WSArrival"+str(i+1)+".csv")
        args = ['testingCSV/WSArrival'+str(i+1)+'.csv','FALSE','2','WsArrivalOutput']
        multivaraiateAnalysis(args)
        
        multiVariate_Anomaly_Result = csvTransform('testingCSV/WsArrivalOutput1.csv',temp1[startDatePoint])
        # multiVariate_Anomaly_Result = []
        multiple_arima_result = resultOfOneMethod(multiVariate_Anomaly_Result)
        union_result_of_H3 = union(2,graphBasedAnomaly_result, multiple_arima_result)
        
        intersection_result_with_H3 = intersect(union_result_of_H1,union_result_of_H3)
        
        #print multiVariate_Anomaly_Result
                
        # Hypothesis 3 For Reatil vs ARRIVAL: END
        
        # Get stats of news articles for each method
        (filteredResult_slope_based, slopeBased_news_article_result,all_articles_slope_based) = fetchNewsForCenter(slopeBased_result, i)
        (filteredResult_correlation_based, correlationBased_news_article_result,all_articles_correlationBased) = fetchNewsForCenter(correlationBased_result, i)
        (filteredResult_linear_regression, linearRegression_news_article_result,all_articles_linearRegression) = fetchNewsForCenter(linearRegression_result, i)
        (filteredResult_graph_based, graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly) = fetchNewsForCenter(graphBasedAnomaly_result, i)
        (filteredResult_multiple_arima, multiple_arima_news_article_result, all_articles_multiple_arima) = fetchNewsForCenter(multiple_arima_result, i)
        (filteredResult_union_of_h1, union_result_of_H1_news_article,all_articles_union_result_of_H1) = fetchNewsForCenter(union_result_of_H1, i)
        (filteredResult_union_of_h3, union_result_of_H3_news_article, all_articles_union_result_of_H3) = fetchNewsForCenter(union_result_of_H3, i)
        (filteredResult_intersection, intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3) = fetchNewsForCenter(intersection_result_with_H3, i)
        
        # Plot Graph for i'th center
        # plotGraphForHypothesisArrival(c_list, wholesaleList[i], slopeBased_result, filteredResult_slope_based, all_articles_graphBasedAnomaly)
        # plotGraphForHypothesisArrival(c_list, wholesaleList[i], linearRegression_result, filteredResult_linear_regression, all_articles_graphBasedAnomaly)
        # plotGraphForHypothesisArrival(c_list, wholesaleList[i], graphBasedAnomaly_result, filteredResult_graph_based, all_articles_graphBasedAnomaly)
        
        print "System result for Wholesale vs Arrival"
        plotGraphForHypothesis(c_list, wholesaleList[i], intersection_result_with_H3, filteredResult_intersection, all_articles_intersection_result_with_H3)
        
        # Save system results in dictionary to process further
        WvsA_anomalies_union_of_H3[2*i]  = union_result_of_H3
        WvsA_anomalies_union_of_H1[2*i] = union_result_of_H1
        WvsA_anomalies_intersection[2*i] = intersection_result_with_H3
        WvsA_anomalies_slope[2*i] = slopeBased_result
        WvsA_anomalies_correlation[2*i] = correlationBased_result
        WvsA_anomalies_linear_regression[2*i] = linearRegression_result
        WvsA_anomalies_graph_based[2*i] = graphBasedAnomaly_result
        WvsA_anomalies_multiple_arima[2*i] = multiple_arima_result
        
        # Save news matched
        WvsA_anomalies_union_of_H3[2*i+1]  = filteredResult_union_of_h3
        WvsA_anomalies_union_of_H1[2*i+1] = filteredResult_union_of_h1
        WvsA_anomalies_intersection[2*i+1] = filteredResult_intersection
        WvsA_anomalies_slope[2*i+1] = filteredResult_slope_based
        WvsA_anomalies_correlation[2*i+1] = filteredResult_correlation_based
        WvsA_anomalies_linear_regression[2*i+1] = filteredResult_linear_regression
        WvsA_anomalies_graph_based[2*i+1] = filteredResult_graph_based
        WvsA_anomalies_multiple_arima[2*i+1] = filteredResult_multiple_arima
    
    
    localNationHelper(arrivalList[0], wholesaleList[0], arrivalList[1], wholesaleList[1], WvsA_anomalies_intersection[2*0], WvsA_anomalies_intersection[2*1], True)  
    print "END OF RETAIL VS ARRIVAL \n\n\n"
    
    # Printing Analysis
    for i in range(0,numOfFiles):
        print "Center:" + str(placeMapping(i))
        print "\nAnomalies Reported:"
        print ",Slope Based,Correlation,Linear Regression,Graph Based,Multi Variate,1 U 2 U 3,4 U 5,(1 U 2 U 3) ^ (4 U 5)"
        print "Retail Vs Average," + str(len(RvsR_anomalies_slope[2*i])) + "," + str(len(RvsR_anomalies_correlation[2*i])) + "," + str(len(RvsR_anomalies_linear_regression[2*i])) + "," + str(len(RvsR_anomalies_graph_based[2*i])) + "," + str(len(RvsR_anomalies_multiple_arima[2*i])) + "," + str(len(RvsR_anomalies_union_of_H1[2*i])) + "," + str(len(RvsR_anomalies_union_of_H3[2*i])) + "," + str(len(RvsR_anomalies_intersection[2*i]))
        print "Retail Vs Arrival," + str(len(RvsA_anomalies_slope[2*i])) + "," + str(len(RvsA_anomalies_correlation[2*i])) + "," + str(len(RvsA_anomalies_linear_regression[2*i])) + "," + str(len(RvsA_anomalies_graph_based[2*i])) + "," + str(len(RvsA_anomalies_multiple_arima[2*i])) + "," + str(len(RvsA_anomalies_union_of_H1[2*i])) + "," + str(len(RvsA_anomalies_union_of_H3[2*i])) + "," + str(len(RvsA_anomalies_intersection[2*i]))
        print "Retail Vs Wholesale," + str(len(RvsW_anomalies_slope[2*i])) + "," + str(len(RvsW_anomalies_correlation[2*i])) + "," + str(len(RvsW_anomalies_linear_regression[2*i])) + "," + str(len(RvsW_anomalies_graph_based[2*i])) + "," + str(len(RvsW_anomalies_multiple_arima[2*i])) + "," + str(len(RvsW_anomalies_union_of_H1[2*i])) + "," + str(len(RvsW_anomalies_union_of_H3[2*i])) + "," + str(len(RvsW_anomalies_intersection[2*i]))
        print "Wholesale Vs Arrival," + str(len(WvsA_anomalies_slope[2*i])) + "," + str(len(WvsA_anomalies_correlation[2*i])) + "," + str(len(WvsA_anomalies_linear_regression[2*i])) + "," + str(len(WvsA_anomalies_graph_based[2*i])) + "," + str(len(WvsA_anomalies_multiple_arima[2*i])) + "," + str(len(WvsA_anomalies_union_of_H1[2*i])) + "," + str(len(WvsA_anomalies_union_of_H3[2*i])) + "," + str(len(WvsA_anomalies_intersection[2*i]))
        
        print "\n\nNews Article Analysis:\n"
        print ",Slope Based,Correlation,Linear Regression,Graph Based,Multi Variate,1 U 2 U 3,4 U 5,(1 U 2 U 3) ^ (4 U 5)"
        print "Retail Vs Average," + str(len(RvsR_anomalies_slope[2*i+1])) + "," + str(len(RvsR_anomalies_correlation[2*i+1])) + "," + str(len(RvsR_anomalies_linear_regression[2*i+1])) + "," + str(len(RvsR_anomalies_graph_based[2*i+1])) + "," + str(len(RvsR_anomalies_multiple_arima[2*i+1])) + "," + str(len(RvsR_anomalies_union_of_H1[2*i+1])) + "," + str(len(RvsR_anomalies_union_of_H3[2*i+1])) + "," + str(len(RvsR_anomalies_intersection[2*i+1]))
        print "Retail Vs Arrival," + str(len(RvsA_anomalies_slope[2*i+1])) + "," + str(len(RvsA_anomalies_correlation[2*i+1])) + "," + str(len(RvsA_anomalies_linear_regression[2*i+1])) + "," + str(len(RvsA_anomalies_graph_based[2*i+1])) + "," + str(len(RvsA_anomalies_multiple_arima[2*i+1])) + "," + str(len(RvsA_anomalies_union_of_H1[2*i+1])) + "," + str(len(RvsA_anomalies_union_of_H3[2*i+1])) + "," + str(len(RvsA_anomalies_intersection[2*i+1]))
        print "Retail Vs Wholesale," + str(len(RvsW_anomalies_slope[2*i+1])) + "," + str(len(RvsW_anomalies_correlation[2*i+1])) + "," + str(len(RvsW_anomalies_linear_regression[2*i+1])) + "," + str(len(RvsW_anomalies_graph_based[2*i+1])) + "," + str(len(RvsW_anomalies_multiple_arima[2*i+1])) + "," + str(len(RvsW_anomalies_union_of_H1[2*i+1])) + "," + str(len(RvsW_anomalies_union_of_H3[2*i+1])) + "," + str(len(RvsW_anomalies_intersection[2*i+1]))
        print "Wholesale Vs Arrival," + str(len(WvsA_anomalies_slope[2*i+1])) + "," + str(len(WvsA_anomalies_correlation[2*i+1])) + "," + str(len(WvsA_anomalies_linear_regression[2*i+1])) + "," + str(len(WvsA_anomalies_graph_based[2*i+1])) + "," + str(len(WvsA_anomalies_multiple_arima[2*i+1])) + "," + str(len(WvsA_anomalies_union_of_H1[2*i+1])) + "," + str(len(WvsA_anomalies_union_of_H3[2*i+1])) + "," + str(len(WvsA_anomalies_intersection[2*i+1]))
        
        
        print "\n\nTotal Articles for " + placeMapping(i) + "," + str(len(all_articles[i]))
     
        
# hypothesisForCenter(5,"testingCSV/MumbaiSILData.csv","testingCSV/DelhiSILData.csv", "testingCSV/AhmedabadSILData.csv","testingCSV/BengaluruSILData.csv","testingCSV/PatnaSILData.csv")

def localNationHelper(series1, series2, series3, series4, result1, result2, isArrival = False):
    setOfAnomaliesMumbai = set([date for (date,) in result1])
    setOfAnomaliesDelhi = set([date for (date,) in result2])
    localMumbai= setOfAnomaliesMumbai.difference(setOfAnomaliesDelhi)
    localDelhi = setOfAnomaliesDelhi.difference(setOfAnomaliesMumbai)
    nation = setOfAnomaliesDelhi.intersection(setOfAnomaliesMumbai)
    localMumbai = convertSetToList(localMumbai)
    localDelhi = convertSetToList(localDelhi)
    nation = convertSetToList(nation)
    
    (filteredResult_localMumbai, localMumbai_news_article_result,all_articles_Mumbai) = fetchNewsForCenter(localMumbai, 0)
    (filteredResult_localDelhi, localDelhi_news_article_result,all_articles_Delhi) = fetchNewsForCenter(localDelhi, 1)
    (filteredResult_nation, nation_news_article_result,all_articles) = fetchNewsForCenter(nation, 5)
    
    print "Local Mumbai Anomalies : " + str(len(localMumbai))
    print "Local Delhi Anomalies : " + str(len(localDelhi))
    print "Nation-wide anomalies : " + str(len(nation))
    
    print "Dates for Anomalies of Local Mumbai:"
    for (date,) in localMumbai:
        print date
    
    print "Dates for Anomalies of Local Delhi:"
    for (date,) in localDelhi:
        print date
        
    print "Dates for Anomalies of Nation:"
    for (date,) in nation:
        print date
        
    print "News Dates Matched for Anomalies of Local Mumbai:"
    for (date,) in filteredResult_localMumbai:
        print date
    
    print "News Dates Matched for Anomalies of Local Delhi:"
    for (date,) in filteredResult_localDelhi:
        print date
        
    print "News Dates Matched for Anomalies of Nation:"
    for (date,) in filteredResult_nation:
        print date
    
    if(isArrival == False):
        print "Graph for Local Mumbai"
        plotGraphForHypothesis(series1, series2, localMumbai, filteredResult_localMumbai, all_articles_Mumbai)
        print "Graph for Local Delhi"
        plotGraphForHypothesis(series3, series4, localDelhi, filteredResult_localDelhi, all_articles_Delhi)
        print "Graph for Nation"
        plotGraphForHypothesis(series1, series2, nation, filteredResult_nation, all_articles)
    else:
        print "Graph for Local Mumbai"
        plotGraphForHypothesisArrival(series1, series2, localMumbai, filteredResult_localMumbai, all_articles_Mumbai)
        print "Graph for Local Delhi"
        plotGraphForHypothesisArrival(series3, series4, localDelhi, filteredResult_localDelhi, all_articles_Delhi)
        print "Graph for Nation"
        plotGraphForHypothesisArrival(series1, series2, nation, filteredResult_nation, all_articles)
  
def convertSetToList(s):
    lst = list(s)
    lst.sort()
    lst = [(date,) for date in lst]
    return lst

hypothesisForCenter(2,"testingCSV/MumbaiSILData.csv","testingCSV/DelhiSILData.csv")


