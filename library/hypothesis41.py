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
from DatabaseConn import Conn
from DatabaseConn import ConnQuery
import matplotlib.pyplot as plt


from Utility import placeMapping
from Utility import getGBAResultsRvA
from Utility import getGBAResultsRvR
import datetime

def plotGraph(original,average,list1, list2):
	datetange = [row[0] for row in original]
	original1 = [row[1] for row in original]
	avg = [row[1] for row in average]
	plt.plot(datetange,original1, color = 'b')
	plt.plot(datetange,avg, color = 'r')
	for row in list1:
		plt.axvspan(row[0], row[0], color='y', alpha=0.5, lw=0)
	for row in list2:
		plt.axvspan(row, row, color='g', alpha=0.5, lw=0)
	plt.show()


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
    
    RRSlope=[]
    RRCorr=[]
    RRlinear=[]
    
    RRSlope1=[]
    RRCorr1=[]
    RRlinear1=[]
    
    scnt=0
    ccnt=0
    lcnt=0
    
    slopeBasedResult=[]
    correlationResult=[]
    lrResult=[]
    for i,c_list in enumerate(centresList):
        # CALL SLOPE BASED
        slopeBasedResult = slopeBased(c_list,False,avgTimeSeries, False,7,True,0, -1)
        # print slopeBasedResult
        slopeBasedResult = mergeDates(slopeBasedResult)
        #scnt=scnt+len(slopeBasedResult)
        
        RRSlope.append(slopeBasedResult)
        RRSlope1=RRSlope1+slopeBasedResult
        #print 'Done slope based'
        # Correlation
        correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,avgTimeSeries)
        correlationResult = mergeDates(correlationResult)
        #ccnt=ccnt+len(correlationResult)
        
        RRCorr.append(correlationResult)
        RRCorr1=RRCorr1+correlationResult
        
        #print 'Done correlation based'
        # Linear Regression
        lrResult = linear_regressionMain(avgTimeSeries,c_list,1)
        lrResult = mergeDates(lrResult)
        #lcnt=lcnt+len(lrResult)
        
        RRlinear.append(lrResult)
        RRlinear1=RRlinear1+lrResult
        result = intersection(3,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression')
        # Lets save these results.
        center_anomalies_only_retail[i] = result
        
        if(i==0):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Ahmedabad') union (select distinct(article_id) from alchemyentity where entity iLike 'Ahmedabad' )) order by publish_date"
        elif(i==1):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Bangalore') union (select distinct(article_id) from alchemyentity where entity iLike 'Bangalore' )) order by publish_date"       
        elif(i==2):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Mumbai') union (select distinct(article_id) from alchemyentity where entity iLike 'Mumbai' )) order by publish_date"   
        elif(i==3):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Patna') union (select distinct(article_id) from alchemyentity where entity iLike 'Patna' )) order by publish_date"          
        elif(i==4):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Delhi') union (select distinct(article_id) from alchemyentity where entity iLike 'Delhi' )) order by publish_date"
        
        rdates = ConnQuery(query)
        
        print "For center " + str(i)
        print "Total results: " + str(len(result))
        dates_temp_set = set()
        for t in result:
            dates_temp_set.add(t[0])
        
        count = 0
        for date in rdates:
            if(date in dates_temp_set):
                count = cpunt +1
        print "Total artcles found " + str(count) + " out of  " + str(len(rdates))
        '''
        print "Anomalies fior time-series " + str(i) + " are:"
        for (a,b,c,d,e,f,g) in result:
            print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
        '''
        
    RASlope=[]
    RACorr=[]
    RAlinear=[]
    print "Done Retail vs Retail"
    sacnt=0
    cacnt=0
    lacnt=0
    # Now lets consider arrival of each center and see whether these anomalies are due to that or not
    # Anomalies from Arrival vs Retail
    center_anomalies_arr_vs_retail = dict()
    for i,c_list in enumerate(arrivalAtCentres):
        # CALL SLOPE BASED
        slopeBasedResult = slopeBased(c_list,False,centresList[i], False,7,True,0, 1)
        slopeBasedResult = mergeDates(slopeBasedResult)
        sacnt=sacnt+len(slopeBasedResult)
        
        RASlope.append(slopeBasedResult)
        #print slopeBasedResult
        #print"########################################################################"
        #print RASlope
        # Correlation
        correlationResult = anomaliesFromWindowCorrelationWithConstantlag(c_list,centresList[i],15,15,False)
        correlationResult = mergeDates(correlationResult)
        cacnt=cacnt+len(correlationResult)
        
        RACorr.append(correlationResult)
        # Linear Regression
        lrResult = linear_regressionMain(c_list,centresList[i],1)
        lrResult = mergeDates(lrResult)
        lacnt=lacnt+len(lrResult)
        
        RAlinear.append(lrResult)
        #print lrResult
        result = intersection(3,slopeBasedResult,'slope_based',correlationResult,'correlation',lrResult,'linear_regression')
        # Lets save these results.
        center_anomalies_arr_vs_retail[i] = result
        
        if(i==0):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Ahmedabad') union (select distinct(article_id) from alchemyentity where entity iLike 'Ahmedabad' )) order by publish_date"
        elif(i==1):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Bangalore') union (select distinct(article_id) from alchemyentity where entity iLike 'Bangalore' )) order by publish_date"       
        elif(i==2):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Mumbai') union (select distinct(article_id) from alchemyentity where entity iLike 'Mumbai' )) order by publish_date"   
        elif(i==3):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Patna') union (select distinct(article_id) from alchemyentity where entity iLike 'Patna' )) order by publish_date"          
        elif(i==4):
            query = "select distinct(publish_date) from articlemetadata where article_hash_url in ((select distinct(article_id) from alchemykeyword where keyword iLike 'Delhi') union (select distinct(article_id) from alchemyentity where entity iLike 'Delhi' )) order by publish_date"
        
        rdates = ConnQuery(query)
        
        print "For center " + str(i)
        print "Total results: " + str(len(result))
        dates_temp_set = set()
        for t in result:
            dates_temp_set.add(t[0])
        
        count = 0
        for date in rdates:
            if(date in dates_temp_set):
                count = cpunt +1
        print "Total artcles found " + str(count) + " out of  " + str(len(rdates))
         
        '''
        print "Anomalies fior time-series with arrival " + str(i) + " are:"
        for (a,b,c,d,e,f,g) in result:
            print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
        '''
    
    file = open("NewsAnalysisResult_xx.csv", "a")

    cnt=0
    rnt=0
    newsReportsDates=[]
    publishDates=set()
    # Time to analyse both results:
    for i in range(0,len(arrivalAtCentres)):
        print "\n\n\n\nFOR CENTER " + str(i) + "  INTERSECTION OF RETAIL VS AVG AND RETAIL VS ARRIVAL IS..... \n\n"
        place = placeMapping(i)
        #result = intersection(2,RRCorr1,'correlation',RRCorr1,'correlation')
        reatilVSarrival = getGBAResultsRvA(i,50)
        reatilVSretail= getGBAResultsRvR(i,50)
        result = intersectionOfFinalResults(reatilVSretail,reatilVSarrival)
        print result
        #cnt=cnt+len(result)
        for (a,b) in result:
            lli=Conn(datetime.datetime.strptime(a, "%Y-%m-%d"),place)
            if(len(lli) !=0):
                newsReportsDates.append(a)
                
                rnt= rnt+1
                print str(a) + "," + str(b) + "," + " " + "," + "" + "," + ""+ "," + ""+ "," + ""
                print lli
                for li in lli:
                    publishDates.add(li['publish_date'])
                    file.write(str(a) + "||" + str(b) + "||" + " " +  "||" + "Linear" + "||" + "" + "||" + "" + "||" + "" + "||" +li['title']+ "||"+li['sourcename']+ "||"+li['source_url']+ "||"+str(li['publish_date'])+ "||"+li['article_id']+ "||"+li['exact_url']+ "||"+li['title']+"||"+place+"\n")
        print "Publish Dates ::::::::: "
        plotGraph(centresList[i],avgTimeSeries,newsReportsDates, list(publishDates))
        print "-----------------------------------------------------------------------------------------------------------------------"
    '''    
    print "Received::: "+ str( len(RRCorr1))
    print "Received News::: "+ str(rnt)
    rvsrcnt=0
    rvsrrnt=0
    rvsacnt=0
    rvsarnt=0
    icnt=0
    irnt=0
    # Time to analyse both results:
    for i in range(0,len(arrivalAtCentres)):
        print "\n\n\n\nFOR CENTER " + str(i) + "  INTERSECTION OF RETAIL VS AVG AND RETAIL VS ARRIVAL IS..... \n\n"
        place = placeMapping(i)
        retailVSreatil = center_anomalies_only_retail[i]
        reatilVSarrival = center_anomalies_arr_vs_retail[i]
        print "Retail Results ::::::: "+ place
        rvsrcnt=rvsrcnt+len(retailVSreatil)
        for (a,b,c,d,e,f,g) in retailVSreatil:
            lli=Conn(a,place)
            #print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
            #print li
            if(len(lli) !=0):
                rvsrrnt=rvsrrnt+1
                print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
                print lli
                for li in lli:
                    file.write(str(a) + "||" + str(b) + "||" + str(c) + "||" + str(d) + "||" + str(e)+ "||" + str(f)+ "||" + str(g) + "||"+li['title']+ "||"+li['sourcename']+ "||"+li['source_url']+ "||"+str(li['publish_date'])+ "||"+li['article_id']+ "||"+li['exact_url']+ "||"+li['title']+"||"+place+"\n")
        print "-----------------------------------------------------------------------------------------------------------------------"
        print "Retail vs Arrival Results ::::::: "
        rvsacnt= rvsacnt+len(reatilVSarrival)
        for (a,b,c,d,e,f,g) in reatilVSarrival:
            lli=Conn(a,place)
            if(len(lli) !=0):
                rvsarnt=rvsarnt+1
                print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
                print lli
                for li in lli:
                    file.write(str(a) + "||" + str(b) + "||" + str(c) + "||" + str(d) + "||" + str(e)+ "||" + str(f)+ "||" + str(g) + "||"+li['title']+ "||"+li['sourcename']+ "||"+li['source_url']+ "||"+str(li['publish_date'])+ "||"+li['article_id']+ "||"+li['exact_url']+ "||"+li['title']+"||"+place+"\n")       
        print "-----------------------------------------------------------------------------------------------------------------------"
        
        intersect = intersectionOfFinalResults(reatilVSarrival,retailVSreatil)
        icnt=icnt+len(intersect)
        for (a,b,c,d,e,f,g) in intersect:
            lli=Conn(a,place)
            if(len(lli) !=0):
                irnt=irnt+1
                print str(a) + "," + str(b) + "," + str(c) + "," + str(d) + "," + str(e)+ "," + str(f)+ "," + str(g)
                print lli
                for li in lli:
                    file.write(str(a) + "||" + str(b) + "||" + str(c) + "||" + str(d) + "||" + str(e)+ "||" + str(f)+ "||" + str(g) + "||"+li['title']+ "||"+li['sourcename']+ "||"+li['source_url']+ "||"+str(li['publish_date'])+ "||"+li['article_id']+ "||"+li['exact_url']+ "||"+li['title']+"||"+place+"\n")
        print "-----------------------------------------------------------------------------------------------------------------------"
    
    print "Linear Result Total counts :" + str(rvsrcnt)
    print "Linear Result counts :" + str(rvsrrnt)
    
    print "Linear Result Total counts :" + str(rvsacnt)
    print "Linear Result counts :" + str(rvsarnt)
    
    print "Linear Result Total counts :" + str(icnt)
    print "Linear Result counts :" + str(irnt)
    
    file.close()
    '''
    
    
# hypothesis4Testing(1,"AhmedabadSILData.csv")
# For Centers
#start_date = "2010/11/11"
#date_1 = datetime.datetime.strptime(start_date, "%Y/%m/%d")
#res= Conn(date_1,"")
#print "REsult :::::::::::::::::::::::::::"
#print res
hypothesis4Testing(5,"testingCSV/AhmedabadSILData.csv","testingCSV/BengaluruSILData.csv","testingCSV/MumbaiSILData.csv","testingCSV/PatnaSILData.csv","testingCSV/DelhiSILData.csv")


