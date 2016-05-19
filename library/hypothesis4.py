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
from Utility import fetchNewsForCenter
from Utility import placeMapping
from Utility import getGBAResultsRvA
from Utility import getGBAResultsRvR
from Utility import findAverageTimeSeries
from Utility import getColumnFromListOfTuples
from Utility import convertListToFloat
from Utility import plotGraphForHypothesis
import datetime
from Utility import resultOfOneMethod
from Utility import getDiffStatsOfNewsArticles
from Utility import statsPrintHelperIntersect
from Utility import statsPrintHelperUnion,statsPrintHelperAllCentersUnion

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
    
    # Hashmap to save results of comparison of retail prices vs average
    RvsR_anomalies_without_H3 = dict()
    RvsR_anomalies_with_H3 = dict()
    RvsR_anomalies_slope = dict()
    RvsR_anomalies_correlation = dict()
    RvsR_anomalies_linear_regression = dict()
    RvsR_anomalies_graph_based = dict()
    
    
    # Hashmap to save results of comparison of retail prices vs arrival
    RvsA_anomalies_without_H3 = dict()
    RvsA_anomalies_with_H3 = dict()
    RvsA_anomalies_slope = dict()
    RvsA_anomalies_correlation = dict()
    RvsA_anomalies_linear_regression = dict()
    RvsA_anomalies_graph_based = dict()
    
    print "STARTING WITH RETAIL VS AVERAGE \n\n\n"
    
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
        slopeBased_result = resultOfOneMethod(slopeBasedResult)
        correlationBased_result = resultOfOneMethod(correlationResult)
        linearRegression_result = resultOfOneMethod(lrResult)
        intersection_result_without_H3 = intersection(3,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression')
        
        # Hypothesis 1: END
        
        # Hypothesis 3 For Reatil vs AVG: START
        
        graphBasedAnomaly = getGBAResultsRvR(i,50)
        graphBasedAnomaly_result = resultOfOneMethod(graphBasedAnomaly)
        intersection_result_with_H3 = intersection(4,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression', graphBasedAnomaly, 'graph_based')
        
        # Hypothesis 3 For Reatil vs AVG: END
        
        # Get stats of news articles for each method
        (slopeBased_news_article_result,all_articles_slope_based) = fetchNewsForCenter(slopeBased_result, i)
        (correlationBased_news_article_result,all_articles_correlationBased) = fetchNewsForCenter(correlationBased_result, i)
        (linearRegression_news_article_result,all_articles_linearRegression) = fetchNewsForCenter(linearRegression_result, i)
        (graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly) = fetchNewsForCenter(graphBasedAnomaly_result, i)
        (intersection_result_without_H3_news_article_result,all_articles_intersection_result_without_H3) = fetchNewsForCenter(intersection_result_without_H3, i)
        (intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3) = fetchNewsForCenter(intersection_result_with_H3, i)
        '''
        print "STATS FOR CENTER:" + str(i)
        print "For Method : Slope Based"
        print "Total anomalies reported: " + str(len(slopeBased_result))
        print "Total news articles found related to anomaly reported: " + str(len(slopeBased_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_slope_based))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(slopeBased_news_article_result)
        print "**********"
        print "For Method : Correlation Based"
        print "Total anomalies reported: " + str(len(correlationBased_result))
        print "Total news articles found related to anomaly reported: " + str(len(correlationBased_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_correlationBased))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(correlationBased_news_article_result)
        print "**********"
        print "For Method : Linear Regression"
        print "Total anomalies reported: " + str(len(linearRegression_result))
        print "Total news articles found related to anomaly reported: " + str(len(linearRegression_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_linearRegression))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(linearRegression_news_article_result)
        print "**********"
        print "For Method : Graph Based anomaly result"
        print "Total anomalies reported: " + str(len(graphBasedAnomaly_result))
        print "Total news articles found related to anomaly reported: " + str(len(graphBasedAnomaly_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_graphBasedAnomaly))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(graphBasedAnomaly_news_article_result)
        print "**********"
        print "For Method : Intersection of Slope Based,Correlation Based and Linear Regression"
        print "Total anomalies reported: " + str(len(intersection_result_without_H3))
        print "Total news articles found related to anomaly reported: " + str(len(intersection_result_without_H3_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_intersection_result_without_H3))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(intersection_result_without_H3_news_article_result)
        print "**********"
        print "For Method : Intersection of Slope Based,Correlation Based, Linear Regression and Graph based"
        print "Total anomalies reported: " + str(len(intersection_result_with_H3))
        print "Total news articles found related to anomaly reported: " + str(len(intersection_result_with_H3_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_intersection_result_with_H3))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(intersection_result_with_H3_news_article_result)
        print "-----------------------------------------------------"
        '''       
        # Plot Graph for i'th center
        # plotGraphForHypothesis(c_list, avgRetailTimeSeries, resultOfOneMethod(correlationResult), news_article_matched_dates, all_articles)
        
        # Save results in dictionary to process further
        RvsR_anomalies_without_H3[i] = intersection_result_without_H3
        RvsR_anomalies_with_H3[i] = intersection_result_with_H3
        RvsR_anomalies_slope[i] = slopeBased_result
        RvsR_anomalies_correlation[i] = correlationBased_result
        RvsR_anomalies_linear_regression[i] = linearRegression_result
        RvsR_anomalies_graph_based[i] = graphBasedAnomaly_result
        
    print "END OF RETAIL VS AVERAGE \n\n\n"
    print "STARTING WITH RETAIL VS ARRIVAL \n\n\n"
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
        slopeBased_result = resultOfOneMethod(slopeBasedResult)
        correlationBased_result = resultOfOneMethod(correlationResult)
        linearRegression_result = resultOfOneMethod(lrResult)
        intersection_result_without_H3 = intersection(3,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression')
        
        # Hypothesis 2: END
        
        # Hypothesis 3 For Reatil vs ARRIVAL: START
        
        graphBasedAnomaly = getGBAResultsRvA(i,50)
        graphBasedAnomaly_result = resultOfOneMethod(graphBasedAnomaly)
        intersection_result_with_H3 = intersection(4,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression', graphBasedAnomaly, 'graph_based')
        
        # Hypothesis 3 For Reatil vs ARRIVAL: END
        
        # Get stats of news articles for each method
        (slopeBased_news_article_result,all_articles_slope_based) = fetchNewsForCenter(slopeBased_result, i)
        (correlationBased_news_article_result,all_articles_correlationBased) = fetchNewsForCenter(correlationBased_result, i)
        (linearRegression_news_article_result,all_articles_linearRegression) = fetchNewsForCenter(linearRegression_result, i)
        (graphBasedAnomaly_news_article_result,all_articles_graphBasedAnomaly) = fetchNewsForCenter(graphBasedAnomaly_result, i)
        (intersection_result_without_H3_news_article_result,all_articles_intersection_result_without_H3) = fetchNewsForCenter(intersection_result_without_H3, i)
        (intersection_result_with_H3_news_article_result,all_articles_intersection_result_with_H3) = fetchNewsForCenter(intersection_result_with_H3, i)
        '''
        print "STATS FOR CENTER:" + str(i)
        print "For Method : Slope Based"
        print "Total anomalies reported: " + str(len(slopeBased_result))
        print "Total news articles found related to anomaly reported: " + str(len(slopeBased_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_slope_based))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(slopeBased_news_article_result)
        print "**********"
        print "For Method : Correlation Based"
        print "Total anomalies reported: " + str(len(correlationBased_result))
        print "Total news articles found related to anomaly reported: " + str(len(correlationBased_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_correlationBased))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(correlationBased_news_article_result)
        print "**********"
        print "For Method : Linear Regression"
        print "Total anomalies reported: " + str(len(linearRegression_result))
        print "Total news articles found related to anomaly reported: " + str(len(linearRegression_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_linearRegression))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(linearRegression_news_article_result)
        print "**********"
        print "For Method : Graph Based anomaly result"
        print "Total anomalies reported: " + str(len(graphBasedAnomaly_result))
        print "Total news articles found related to anomaly reported: " + str(len(graphBasedAnomaly_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_graphBasedAnomaly))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(graphBasedAnomaly_news_article_result)
        print "**********"
        print "For Method : Intersection of Slope Based,Correlation Based and Linear Regression"
        print "Total anomalies reported: " + str(len(intersection_result_without_H3))
        print "Total news articles found related to anomaly reported: " + str(len(intersection_result_without_H3_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_intersection_result_without_H3))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(intersection_result_without_H3_news_article_result)
        print "**********"
        print "For Method : Intersection of Slope Based,Correlation Based, Linear Regression and Graph based"
        print "Total anomalies reported: " + str(len(intersection_result_with_H3))
        print "Total news articles found related to anomaly reported: " + str(len(intersection_result_with_H3_news_article_result))
        print "Total news articles present for this center " + str(len(all_articles_intersection_result_with_H3))
        print "How far is news articles from reported anomalies? "
        print getDiffStatsOfNewsArticles(intersection_result_with_H3_news_article_result)
        print "-----------------------------------------------------"
        '''       
        # Plot Graph for i'th center
        # plotGraphForHypothesis(c_list, avgRetailTimeSeries, resultOfOneMethod(correlationResult), news_article_matched_dates, all_articles)
        
        # Save results in dictionary to process further
        RvsA_anomalies_without_H3[i] = intersection_result_without_H3
        RvsA_anomalies_with_H3[i] = intersection_result_with_H3
        RvsA_anomalies_slope[i] = slopeBased_result
        RvsA_anomalies_correlation[i] = correlationBased_result
        RvsA_anomalies_linear_regression[i] = linearRegression_result
        RvsA_anomalies_graph_based[i] = graphBasedAnomaly_result
    
    print "END OF RETAIL VS ARRIVAL \n\n\n"
    
    print "Going for (RETAIL VS ARRIVAL) Intersect (Retail vs Retail Average) CENTER BY CENTER"
    # For each center
    '''
    for i in range(0,5):
        statsPrintHelperIntersect(RvsA_anomalies_slope[i], RvsR_anomalies_slope[i], "Slope Based", i)
        statsPrintHelperIntersect(RvsA_anomalies_correlation[i], RvsR_anomalies_correlation[i], "Correlation Based", i)
        statsPrintHelperIntersect(RvsA_anomalies_linear_regression[i], RvsR_anomalies_linear_regression[i], "Linear Regression", i)
        statsPrintHelperIntersect(RvsA_anomalies_graph_based[i], RvsR_anomalies_graph_based[i], "Graph Based", i)
        statsPrintHelperIntersect(RvsA_anomalies_without_H3[i], RvsR_anomalies_without_H3[i], "Intersection of Slope Based, Correlation based and linear regression", i)
        statsPrintHelperIntersect(RvsA_anomalies_with_H3[i], RvsR_anomalies_with_H3[i], "Intersection of Slope Based, Correlation based, graph based and linear regression", i)
    '''
    print "END OF (RETAIL VS ARRIVAL) Intersect (Retail vs Retail Average) CENTER BY CENTER"
    
    print "Going for (RETAIL VS ARRIVAL) Union (Retail vs Retail Average) CENTER BY CENTER"
    # For each center
    '''
    for i in range(0,5):
        statsPrintHelperUnion(RvsA_anomalies_slope[i], RvsR_anomalies_slope[i], "Slope Based", i)
        statsPrintHelperUnion(RvsA_anomalies_correlation[i], RvsR_anomalies_correlation[i], "Correlation Based", i)
        statsPrintHelperUnion(RvsA_anomalies_linear_regression[i], RvsR_anomalies_linear_regression[i], "Linear Regression", i)
        statsPrintHelperUnion(RvsA_anomalies_graph_based[i], RvsR_anomalies_graph_based[i], "Graph Based", i)
        statsPrintHelperUnion(RvsA_anomalies_without_H3[i], RvsR_anomalies_without_H3[i], "Intersection of Slope Based, Correlation based and linear regression", i)
        statsPrintHelperUnion(RvsA_anomalies_with_H3[i], RvsR_anomalies_with_H3[i], "Intersection of Slope Based, Correlation based, graph based and linear regression", i)
    print "END OF (RETAIL VS ARRIVAL) Union (Retail vs Retail Average) CENTER BY CENTER"
    '''
    
    # Time to combine all centers
    # Take Union
    print "Union of Retail vs Arrival"
    statsPrintHelperAllCentersUnion(RvsA_anomalies_slope[0],RvsA_anomalies_slope[1],RvsA_anomalies_slope[2],RvsA_anomalies_slope[3],RvsA_anomalies_slope[4],"Slope Based")
    statsPrintHelperAllCentersUnion(RvsA_anomalies_correlation[0],RvsA_anomalies_correlation[1],RvsA_anomalies_correlation[2],RvsA_anomalies_correlation[3],RvsA_anomalies_correlation[4],"Correlation Based")
    statsPrintHelperAllCentersUnion(RvsA_anomalies_linear_regression[0],RvsA_anomalies_linear_regression[1],RvsA_anomalies_linear_regression[2],RvsA_anomalies_linear_regression[3],RvsA_anomalies_linear_regression[4],"Linear Regression")
    statsPrintHelperAllCentersUnion(RvsA_anomalies_graph_based[0],RvsA_anomalies_graph_based[1],RvsA_anomalies_graph_based[2],RvsA_anomalies_graph_based[3],RvsA_anomalies_graph_based[4],"Graph based anomaly")
    statsPrintHelperAllCentersUnion(RvsA_anomalies_without_H3[0],RvsA_anomalies_without_H3[1],RvsA_anomalies_without_H3[2],RvsA_anomalies_without_H3[3],RvsA_anomalies_without_H3[4],"3 methods")
    statsPrintHelperAllCentersUnion(RvsA_anomalies_slope[0],RvsA_anomalies_slope[1],RvsA_anomalies_slope[2],RvsA_anomalies_slope[3],RvsA_anomalies_slope[4],"All 4 methods")
    
    # Intersection for all methods 
    
    
hypothesisForCenter(5,"testingCSV/AhmedabadSILData.csv","testingCSV/BengaluruSILData.csv","testingCSV/MumbaiSILData.csv","testingCSV/PatnaSILData.csv","testingCSV/DelhiSILData.csv")


