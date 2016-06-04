import numpy
import csv
import sys
import matplotlib.pyplot as plt
from slopeBasedDetection import slopeBased
from linear_regression import linear_regressionMain
from window_correlation import anomaliesFromWindowCorrelationWithConstantlag
import numpy as np
from Utility import fetchNewsForCenter,placeMapping, getGBAResultsRvA, getGBAResultsRvR, findAverageTimeSeries, getColumnFromListOfTuples, convertListToFloat, plotGraphForHypothesis, resultOfOneMethod, concateLists, writeToCSV, getDiffStatsOfNewsArticles, statsPrintHelperIntersect, statsPrintHelperUnion,statsPrintHelperAllCentersUnion, intersection, intersectionOfFinalResults, MADThreshold, mergeDates, union, intersect
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
    
    # print csvDataList
    # sys.exit(0)
    
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
    
    writeToCSV(lstRetail,"/home/kapil/Desktop/mtp/library/testingCSV/AllRetailData.csv")
    args = ['/home/kapil/Desktop/mtp/library/testingCSV/AllRetailData.csv','FALSE',str(len(retailListWithNoDates)),'retail']
    multivaraiateAnalysis(args)
    
    
    # Hashmap to save results of comparison of retail prices vs average
    RvsR_anomalies_without_H3 = dict()
    RvsR_anomalies_with_H3 = dict()
    RvsR_anomalies_slope = dict()
    RvsR_anomalies_correlation = dict()
    RvsR_anomalies_linear_regression = dict()
    RvsR_anomalies_graph_based = dict()
    RvsR_anomalies_multiple_arima = dict()
    
    
    # Hashmap to save results of comparison of retail prices vs arrival
    RvsA_anomalies_without_H3 = dict()
    RvsA_anomalies_with_H3 = dict()
    RvsA_anomalies_slope = dict()
    RvsA_anomalies_correlation = dict()
    RvsA_anomalies_linear_regression = dict()
    RvsA_anomalies_graph_based = dict()
    RvsA_anomalies_multiple_arima = dict()
    
    print "STARTING WITH RETAIL VS AVERAGE \n\n\n"
    
    for i,c_list in enumerate(retailList):
        
        # Hypothesis 1: START
        
        # CALL SLOPE BASED
        slopeBasedResult = slopeBased(c_list,False,avgRetailTimeSeries, False,7,True,0, 1)
        # slopeBasedResult = temp1234(c_list,False,avgRetailTimeSeries, False,7,True,0, -1)
        
        # print "Done slope based "
        # sys.exit(0)
        
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
        
        graphBasedAnomaly = graphBasedAnomalyMain(retailList,i,100)
        # graphBasedAnomaly  = []
        graphBasedAnomaly_result = resultOfOneMethod(graphBasedAnomaly)
        
        
        #Since 60% data is used for modelling and rest is used to forecast
        startDatePoint =int(0.60*len(retailListWithNoDates[0]))
        multiVariate_Anomaly_Result = csvTransform("/home/kapil/Desktop/mtp/library/testingCSV/retail"+str(i+1)+".csv",temp1[startDatePoint])
        multiple_arima_result = resultOfOneMethod(multiVariate_Anomaly_Result)
        
        union_result_of_H3 = union(2,graphBasedAnomaly_result, multiple_arima_result)
        
        intersection_result_with_H3 = intersect(union_result_of_H1,union_result_of_H3)
        # Hypothesis 3 For Reatil vs AVG: END
        
        # Get stats of news articles for each method
        (slopeBased_news_article_result,all_articles_slope_based) = fetchNewsForCenter(slopeBased_result, i)
        (correlationBased_news_article_result,all_articles_correlationBased) = fetchNewsForCenter(correlationBased_result, i)
        (linearRegression_news_article_result,all_articles_linearRegression) = fetchNewsForCenter(linearRegression_result, i)
        (graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly) = fetchNewsForCenter(graphBasedAnomaly_result, i)
        (multiple_arima_news_article_result, all_articles_multiple_arima) = fetchNewsForCenter(multiple_arima_result, i)
        (union_result_of_H1_news_article,all_articles_union_result_of_H1) = fetchNewsForCenter(union_result_of_H1, i)
        (union_result_of_H3_news_article, all_articles_union_result_of_H3) = fetchNewsForCenter(union_result_of_H3, i)
        (intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3) = fetchNewsForCenter(intersection_result_with_H3, i)
        
        print "STATS FOR CENTER:" + placeMapping(i)
        print "For Method : Slope Based"
        print "Total anomalies reported: " + str(len(slopeBased_result))
        print "Total news articles found related to anomaly reported: " + str(len(slopeBased_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_slope_based))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(slopeBased_news_article_result, all_articles_slope_based)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in slopeBased_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : Correlation Based"
        print "Total anomalies reported: " + str(len(correlationBased_result))
        print "Total news articles found related to anomaly reported: " + str(len(correlationBased_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_correlationBased))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(correlationBased_news_article_result,all_articles_correlationBased)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in correlationBased_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : Linear Regression"
        print "Total anomalies reported: " + str(len(linearRegression_result))
        print "Total news articles found related to anomaly reported: " + str(len(linearRegression_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_linearRegression))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(linearRegression_news_article_result,all_articles_linearRegression)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in linearRegression_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : Graph Based anomaly result"
        print "Total anomalies reported: " + str(len(graphBasedAnomaly_result))
        print "Total news articles found related to anomaly reported: " + str(len(graphBasedAnomaly_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_graphBasedAnomaly))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in graphBasedAnomaly_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : Multivariate result"
        print "Total anomalies reported: " + str(len(multiple_arima_result))
        print "Total news articles found related to anomaly reported: " + str(len(multiple_arima_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_multiple_arima))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(multiple_arima_news_article_result,all_articles_multiple_arima)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in multiple_arima_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : union_result_of_H3"
        print "Total anomalies reported: " + str(len(union_result_of_H3))
        print "Total news articles found related to anomaly reported: " + str(len(union_result_of_H3_news_article))
        print "Total news articles present for this center " + str(len(all_articles_union_result_of_H3))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(union_result_of_H3_news_article,all_articles_union_result_of_H3)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in union_result_of_H3_news_article:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "**********"
        print "For Method : union_result_of_H1"
        print "Total anomalies reported: " + str(len(union_result_of_H1))
        print "Total news articles found related to anomaly reported: " + str(len(union_result_of_H1_news_article))
        print "Total news articles present for this center " + str(len(all_articles_union_result_of_H1))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(union_result_of_H1_news_article,all_articles_union_result_of_H1)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in union_result_of_H1_news_article:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "For Method : intersection_result_with_H3"
        print "Total anomalies reported: " + str(len(intersection_result_with_H3))
        print "Total news articles found related to anomaly reported: " + str(len(intersection_result_with_H3_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_intersection_result_with_H3))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in intersection_result_with_H3_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "-----------------------------------------------------"
          
          
        print "ARTICLES PRESENT FOR THIS CENTER: "
        for row in all_articles_correlationBased:
            print row
        # Plot Graph for i'th center
        # plotGraphForHypothesis(c_list, avgRetailTimeSeries, resultOfOneMethod(slopeBasedResult), slopeBased_news_article_result, all_articles_slope_based)
        
        # Save results in dictionary to process further
        # RvsR_anomalies_without_H3[i] = intersection_result_without_H3
        # RvsR_anomalies_with_H3[i] = intersection_result_with_H3
        # RvsR_anomalies_slope[i] = slopeBased_result
        # RvsR_anomalies_correlation[i] = correlationBased_result
        # RvsR_anomalies_linear_regression[i] = linearRegression_result
        # RvsR_anomalies_graph_based[i] = graphBasedAnomaly_result
        # RvsR_anomalies_multiple_arima[i] = multiple_arima_result
    # sys.exit(0)    
    print "END OF RETAIL VS AVERAGE \n\n\n"
    print "STARTING WITH RETAIL VS ARRIVAL \n\n\n"
    # Now lets consider arrival of each center and see whether these anomalies are due to that or not
    # Anomalies from Arrival vs Retail
    center_anomalies_arr_vs_retail = dict()
    for i,c_list in enumerate(arrivalList):
        
        # Hypothesis 2: START        
        
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
        graphBasedAnomaly = graphBasedAnomalyMain(temp5, 0,100)
        # graphBasedAnomaly = []
        graphBasedAnomaly_result = resultOfOneMethod(graphBasedAnomaly)
        
        
        lstWSRetailArrival =[]
        lstWSRetailArrival.append(getColumnFromListOfTuples(wholesaleList[i],1))
        lstWSRetailArrival.append(getColumnFromListOfTuples(retailList[i],1))
        lstWSRetailArrival.append(getColumnFromListOfTuples(arrivalList[i],1))
        lstRetail= concateLists(lstWSRetailArrival)
        #print lstRetail
        writeToCSV(lstRetail,"/home/kapil/Desktop/mtp/library/testingCSV/AllDataForeCast"+str(i+1)+".csv")
        args = ['/home/kapil/Desktop/mtp/library/testingCSV/AllDataForeCast'+str(i+1)+'.csv','FALSE','3','RetailWsArrival']
        multivaraiateAnalysis(args)
        multiVariate_Anomaly_Result = csvTransform('/home/kapil/Desktop/mtp/library/testingCSV/RetailWsArrival2.csv',temp1[startDatePoint])
        multiple_arima_result = resultOfOneMethod(multiVariate_Anomaly_Result)
        union_result_of_H3 = union(2,graphBasedAnomaly_result, multiple_arima_result)
        
        intersection_result_with_H3 = intersect(union_result_of_H1,union_result_of_H3)
        
        #print multiVariate_Anomaly_Result
                
        # Hypothesis 3 For Reatil vs ARRIVAL: END
        
        # Get stats of news articles for each method
        (slopeBased_news_article_result,all_articles_slope_based) = fetchNewsForCenter(slopeBased_result, i)
        (correlationBased_news_article_result,all_articles_correlationBased) = fetchNewsForCenter(correlationBased_result, i)
        (linearRegression_news_article_result,all_articles_linearRegression) = fetchNewsForCenter(linearRegression_result, i)
        (graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly) = fetchNewsForCenter(graphBasedAnomaly_result, i)
        (multiple_arima_news_article_result, all_articles_multiple_arima) = fetchNewsForCenter(multiple_arima_result, i)
        (union_result_of_H1_news_article,all_articles_union_result_of_H1) = fetchNewsForCenter(union_result_of_H1, i)
        (union_result_of_H3_news_article, all_articles_union_result_of_H3) = fetchNewsForCenter(union_result_of_H3, i)
        (intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3) = fetchNewsForCenter(intersection_result_with_H3, i)
        
        print "STATS FOR CENTER:" + placeMapping(i)
        print "For Method : Slope Based"
        print "Total anomalies reported: " + str(len(slopeBased_result))
        print "Total news articles found related to anomaly reported: " + str(len(slopeBased_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_slope_based))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(slopeBased_news_article_result, all_articles_slope_based)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in slopeBased_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : Correlation Based"
        print "Total anomalies reported: " + str(len(correlationBased_result))
        print "Total news articles found related to anomaly reported: " + str(len(correlationBased_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_correlationBased))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(correlationBased_news_article_result,all_articles_correlationBased)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in correlationBased_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : Linear Regression"
        print "Total anomalies reported: " + str(len(linearRegression_result))
        print "Total news articles found related to anomaly reported: " + str(len(linearRegression_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_linearRegression))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(linearRegression_news_article_result,all_articles_linearRegression)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in linearRegression_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : Graph Based anomaly result"
        print "Total anomalies reported: " + str(len(graphBasedAnomaly_result))
        print "Total news articles found related to anomaly reported: " + str(len(graphBasedAnomaly_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_graphBasedAnomaly))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in graphBasedAnomaly_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : Multivariate result"
        print "Total anomalies reported: " + str(len(multiple_arima_result))
        print "Total news articles found related to anomaly reported: " + str(len(multiple_arima_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_multiple_arima))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(multiple_arima_news_article_result,all_articles_multiple_arima)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in multiple_arima_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "For Method : union_result_of_H3"
        print "Total anomalies reported: " + str(len(union_result_of_H3))
        print "Total news articles found related to anomaly reported: " + str(len(union_result_of_H3_news_article))
        print "Total news articles present for this center " + str(len(all_articles_union_result_of_H3))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(union_result_of_H3_news_article,all_articles_union_result_of_H3)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in union_result_of_H3_news_article:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "**********"
        print "**********"
        print "For Method : union_result_of_H1"
        print "Total anomalies reported: " + str(len(union_result_of_H1))
        print "Total news articles found related to anomaly reported: " + str(len(union_result_of_H1_news_article))
        print "Total news articles present for this center " + str(len(all_articles_union_result_of_H1))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(union_result_of_H1_news_article,all_articles_union_result_of_H1)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in union_result_of_H1_news_article:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "For Method : intersection_result_with_H3"
        print "Total anomalies reported: " + str(len(intersection_result_with_H3))
        print "Total news articles found related to anomaly reported: " + str(len(intersection_result_with_H3_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_intersection_result_with_H3))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3)
        print "#######################################################################"
        print "############### Articles Matched #####################"
        print "#######################################################################"
        for row in intersection_result_with_H3_news_article_result:
            print row
        print "#######################################################################"
        print "#######################################################################"
        print "#######################################################################"
        print "-----------------------------------------------------"
        
       
    
    print "END OF RETAIL VS ARRIVAL \n\n\n"
    
    
    
hypothesisForCenter(2,"testingCSV/MumbaiSILData.csv","testingCSV/DelhiSILData.csv")


