import numpy
import numpy as np
import csv
import matplotlib.pyplot as plt
import datetime
import StringIO
from datetime import date
from datetime import datetime
from datetime import timedelta
import math
import psycopg2


'''

This function takes 3 arguments:

resultsOfSystem: List of tupls/list of the format (date, ... ,...)
intervalToConsider: News will be fetched from news articles for a particular date(given by system as anomaly) in interval [date-intervalToConsider, date+intervalToConsider]

returns result of the following form....
A tuple:

	(resultList, allArticlesQueryResult)
	
Where:

* resultList : This is of tuples with following fields:
				(System_anomaly_date, news_article_date, news_source, source_url, difference_between_system_date_and_news_article_date, list_of_keywords)
				
				1. System_anomaly_date: date reported by our system which is reported as anomolous date
				2. news_article_date: date of news article correpsonding to above System_anomaly_date
				3. news_source: souce of news (which media?)
				4. source_url: link of the news article
				5. difference_between_system_date_and_news_article_date: difference between dates of (news_article_date - System_anomaly_date)
				6. list_of_keywords: List of keywords related with this article
				
* allArticlesQueryResult: List of dates of all news articles for this center which is present in the database


'''

def fetchNewsFor5Centers(resultsOfSystem, intervalToConsider=5):	
	# Create connection to Database
	conn = psycopg2.connect(database="news_articles", user="postgres", password="password", host="127.0.0.1", port="5432")
	cur = conn.cursor()
	
	# Result dictionary
	result = dict()
	
	# Let's see details for each date...
	for row_resultsOfSystem in resultsOfSystem:
		date = row_resultsOfSystem[0].date()
		
		start_date = date - timedelta(days=intervalToConsider)
		start_date = start_date.strftime('%Y/%m/%d')
		end_date = date + timedelta(days=intervalToConsider)
		end_date = end_date.strftime('%Y/%m/%d')
		
		query = "select publish_date, name, source_url, article_hash_url, an.reason, an.comment, an.days from articlemetadata amd, newssource ns, analysis an where amd.source_id = ns.id and publish_date >= '"+start_date+"' and publish_date<= '"+end_date+"' and article_hash_url = an.article_id and article_hash_url in (select distinct(article_id) from analysis where place iLike 'Ahmedabad' or place iLike 'Bengaluru' or place iLike 'Mumbai' or place iLike 'Patna' or place iLike 'Delhi' or place iLike 'India'  and comment not ilike '%delete%' )"
		cur.execute(query)
		queryResult = cur.fetchall()
		
		resultOfThisDate = []
		for row_queryResult in queryResult:			
			# Find All keyword corresponding to that article using : article_hash_url
			# query = "select keyword from alchemykeyword where article_id = '" + row_queryResult[3] + "'"
			# keywordQueryResult = cur.fetchall()
			# smallTuple = (row_queryResult[0], row_queryResult[1], row_queryResult[2], (row_queryResult[0] - date).days, keywordQueryResult)
			smallTuple = (row_queryResult[0], row_queryResult[1], row_queryResult[2], (row_queryResult[0] - date).days , row_queryResult[4], row_queryResult[5], row_queryResult[6])
			resultOfThisDate.append(smallTuple)
		result[date] = resultOfThisDate
		
	# Fetch all dates of news articles corresponding to this center
	query = "select publish_date, an.reason, an.comment, an.days from articlemetadata, analysis an where article_hash_url = an.article_id and article_hash_url in (select distinct(article_id) from analysis where place iLike 'Ahmedabad' or place iLike 'Bengaluru' or place iLike 'Mumbai' or place iLike 'Patna' or place iLike 'Delhi' or place iLike 'India'  and comment not ilike '%delete%' )  order by publish_date"
	cur.execute(query)
	allArticlesQueryResult = cur.fetchall()
	
	# Convert result to list from dictionary
	resultList = []
	for date in result:
		temp_list = result[date]
		for row_temp_list in temp_list:
			(a,b,c,d,e, f, g) = row_temp_list
			resultList.append((date,a,b,c,d,e,f,g))
	# Sort by anomaly date
	resultList = sorted(resultList, key=lambda x: x[0])
	# Filter resultList for duplicates
	filteredResult = []
	newsSet = set()
	for Tuple in resultList:
		if(str(Tuple[1]) + str(Tuple[2]) + str(Tuple[3]) in newsSet):
			continue
		else:
			filteredResult.append(Tuple)
			newsSet.add(str(Tuple[1]) + str(Tuple[2]) + str(Tuple[3]))
	
	return(filteredResult, allArticlesQueryResult)


def statsPrintHelperAllCentersUnion(result1,result2, result3, result4, result5, methodName):
    result = []
    result1Set = set()
    for tuple in result1:
        result1Set.add(tuple[0])
        result.append(tuple)    
    for tuple in result2:
        if(tuple[0] not in result1Set):
            result.append(tuple)
            result1Set.add(tuple[0])            
    for tuple in result3:
        if(tuple[0] not in result1Set):
            result.append(tuple)
            result1Set.add(tuple[0])
    for tuple in result4:
        if(tuple[0] not in result1Set):
            result.append(tuple)
            result1Set.add(tuple[0])
    for tuple in result5:
        if(tuple[0] not in result1Set):
            result.append(tuple)
            
    result = sorted(result, key=lambda x: x[0])
    (news_article_result,all_articles_intersect) = fetchNewsFor5Centers(result)
    print "STATS TAKING UNION OF ALL CENTRES"
    print "For Method : " + methodName
    print "Total anomalies reported: " + str(len(result))
    print "Total news articles found related to anomaly reported: " + str(len(news_article_result))
    print "Total news articles present for this center " + str(len(all_articles_intersect))
    print "How far is news articles from reported anomalies? "
    print getDiffStatsOfNewsArticles(news_article_result,all_articles_intersect)
    print "**********"


'''

This function help to print stats

'''
def statsPrintHelperIntersect(result1, result2, methodName, centerID):
    intersect = intersectionOfFinalResults(result1,result2)
    (intersect_news_article_result,all_articles_intersect) = fetchNewsForCenter(intersect, centerID)
    print "STATS FOR CENTER:" + str(placeMapping(centerID))
    print "For Method : " + methodName
    print "Total anomalies reported: " + str(len(intersect))
    print "Total news articles found related to anomaly reported: " + str(len(intersect_news_article_result))
    print "Total news articles present for this center " + str(len(all_articles_intersect))
    print "How far is news articles from reported anomalies? "
    print getDiffStatsOfNewsArticles(intersect_news_article_result,all_articles_intersect)
    print "**********"
    pass

'''

This function help to print stats

'''
def statsPrintHelperUnion(result1, result2, methodName, centerID):
    intersect = unionOfFinalResults(result1,result2)
    (intersect_news_article_result,all_articles_intersect) = fetchNewsForCenter(intersect, centerID)
    print "STATS FOR CENTER:" + str(placeMapping(centerID))
    print "For Method : " + methodName
    print "Total anomalies reported: " + str(len(intersect))
    print "Total news articles found related to anomaly reported: " + str(len(intersect_news_article_result))
    print "Total news articles present for this center " + str(len(all_articles_intersect))
    print "How far is news articles from reported anomalies? "
    print getDiffStatsOfNewsArticles(intersect_news_article_result,all_articles_intersect)
    print "**********"
    pass

'''

This function takes 3 arguments:

resultsOfSystem: List of tupls/list of the format (date, ... ,...)
centerNumber: Center Number
intervalToConsider: News will be fetched from news articles for a particular date(given by system as anomaly) in interval [date-intervalToConsider, date+intervalToConsider]

Following is assumed for center Numbers:

0: Ahmedabad
1: Bengaluru
2: Mumbai
3: Patna
4: Delhi


returns result of the following form....
A tuple:

	(resultList, allArticlesQueryResult)
	
Where:

* resultList : This is of tuples with following fields:
				(System_anomaly_date, news_article_date, news_source, source_url, difference_between_system_date_and_news_article_date ,reason, comment, days_compared_in_article)
				1. System_anomaly_date: date reported by our system which is reported as anomolous date
				2. news_article_date: date of news article correpsonding to above System_anomaly_date
				3. news_source: souce of news (which media?)
				4. source_url: link of the news article
				5. difference_between_system_date_and_news_article_date: difference between dates of (news_article_date - System_anomaly_date)
				6. reason: what reason is stated by article
				7. comment: any comment on article if present
				8. days_compared_in_article: Article has compared data between how many days to state that it is anomaly?
				
* allArticlesQueryResult: List of dates of all news articles for this center which is present in the database


'''

def fetchNewsForCenter(resultsOfSystem, centerNumber, intervalToConsider=5):
	center = ""
	
	if(centerNumber == 0):
		center = "Mumbai"
	elif(centerNumber == 1):
		center = "Delhi"
	elif(centerNumber == 2):
		center = "Mumbai"
	elif(centerNumber == 3):
		center = "Patna"
	elif(centerNumber == 4):
		center = "Delhi"
	
	# Create connection to Database
	conn = psycopg2.connect(database="news_articles", user="postgres", password="password", host="127.0.0.1", port="5432")
	cur = conn.cursor()
	
	# Result dictionary
	result = dict()
	
	# Let's see details for each date...
	for row_resultsOfSystem in resultsOfSystem:
		# date = row_resultsOfSystem[0].date()
		date = row_resultsOfSystem[0].date()
		
		start_date = date - timedelta(days=intervalToConsider)
		start_date = start_date.strftime('%Y/%m/%d')
		end_date = date + timedelta(days=intervalToConsider)
		end_date = end_date.strftime('%Y/%m/%d')
		query = "select publish_date, name, source_url, article_hash_url, an.reason, an.comment, an.days  from articlemetadata amd, newssource ns, analysis an where amd.source_id = ns.id and publish_date >= '"+start_date+"' and publish_date<= '"+end_date+"' and article_hash_url = an.article_id and article_hash_url in (select distinct(article_id) from analysis where comment not ilike '%delete%' and reason not ilike '%prices dropped%' and (place iLike '"+center+"' or place iLike 'india') )"

		cur.execute(query)
		queryResult = cur.fetchall()
		
		resultOfThisDate = []
		for row_queryResult in queryResult:		
			# Find All keyword corresponding to that article using : article_hash_url
			# query = "select keyword from alchemykeyword where article_id = '" + row_queryResult[3] + "'"
			# keywordQueryResult = cur.fetchall()
			# smallTuple = (row_queryResult[0], row_queryResult[1], row_queryResult[2], (row_queryResult[0] - date).days, keywordQueryResult)
			smallTuple = (row_queryResult[0], row_queryResult[1], row_queryResult[2], (row_queryResult[0] - date).days , row_queryResult[4], row_queryResult[5], row_queryResult[6])
			resultOfThisDate.append(smallTuple)
		result[date] = resultOfThisDate
		
	# Fetch all dates of news articles corresponding to this center
	query = "select distinct publish_date,  an.reason, an.comment, an.days  from articlemetadata, analysis an where  article_hash_url = an.article_id and article_hash_url in (select distinct(article_id) from analysis where  comment not ilike '%delete%' and reason not ilike '%prices dropped%' and publish_date <= '2015-07-06' and (place iLike '"+center+"' or place iLike 'india') ) order by publish_date"
	
	cur.execute(query)
	allArticlesQueryResult = cur.fetchall()
	
	# Convert result to list from dictionary
	resultList = []
	for date in result:
		temp_list = result[date]
		for row_temp_list in temp_list:
			(a,b,c,d,e,f,g) = row_temp_list
			resultList.append((date,a,b,c,d,e,f,g))
	# Sort by anomaly date
	# resultList = sorted(resultList, key=lambda x: (x[0],x[1]))
	resultList = sorted(sorted(resultList, key = lambda x : x[0]), key = lambda x : x[1], reverse = True) 
	
	
	
	# Filter resultList for duplicates
	filteredResult = []
	newsSet = set()
	for Tuple in resultList:
		if(Tuple[0] in newsSet):
			continue
		else:
			filteredResult.append(Tuple)
			newsSet.add(Tuple[0])
	
	
	
	return(filteredResult, resultList, allArticlesQueryResult)


'''

This function takes one argument:
li : list of elements

Returns list of elements after converting each element into float 

'''
def convertListToFloat(li):
    return [float(i) for i in li]


'''

This function returns i'th element of all tuples in the list.
Takes two arguments:

lstTuples : List of tuples
i: which tuple element to return, index starting from zero


Returns list of elements.


'''
def getColumnFromListOfTuples(lstTuples,i):
    if len(lstTuples) == 0:
        return []
    elif len(lstTuples[0])< i-1 :
        return []
    else:
        return [item[i] for item in lstTuples]


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

'''

This function takes 5 arguments:
original: Original Time Series of retail of the format list of tuples . Tuple (date, value)
average: Average Retail Time Series of avg retail of the format list of tuples . Tuple (date, value)
list1: Predicted By system : list of tuples ... (date, ... , ...)
list2: Actual results : List of Dates
total_news_articles: All articles present in the databse for this center/entity
Plots Grpah.

'''
def plotGraphForHypothesis(original,average,list1, list2, total_news_articles):
	dates = [row[0] for row in original]
	daterange = [datetime.strptime(x, "%Y-%m-%d") for x in dates]
	original = [row[1] for row in original]
	avg = [row[1] for row in average]
	fig, ax = plt.subplots()
	ax.plot(daterange,original, color = 'g', label='Original Series')
	ax.plot(daterange,avg, color = 'b')
	for row in list1:
		ax.axvspan(row[0], row[0] + timedelta(days=1), color='y', alpha=0.5, lw=0)
	# print type(list2)
	# print type(total_news_articles)
	# print (list2)
	# print (total_news_articles)
	list2 = [row[0] for row in list2]
	total_news_articles = [row[0] for row in total_news_articles]
	for row in list2:
		ax.axvspan(row, row + timedelta(days=1), color='r', alpha=0.5, lw=0)
	list2 = set(list2)
	total_news_articles = set(total_news_articles)
	not_found_articles = total_news_articles - list2
	not_found_articles = list(not_found_articles)
	not_found_articles.sort()
	for row in not_found_articles:
		ax.axvspan(row, row + timedelta(days=1), color='b', alpha=0.5, lw=0)
	plt.show()




'''

This function takes 5 arguments:
series 1 : original : list of tuples . Tuple (date, value)
series 2 : average : (date, value)
list2: Actual results : List of Dates
total_news_articles: All articles present in the databse for this center/entity
Plots Grpah.

'''
def plotGraphForHypothesisArrival(original,average,list1, list2, total_news_articles):
	dates = [row[0] for row in original]
	daterange = [datetime.strptime(x, "%Y-%m-%d") for x in dates]
	original = [row[1] for row in original]
	avg = [row[1] for row in average]
	fig, ax = plt.subplots()
	ax.plot(daterange,original, color = 'g', label='Original Series')
	ax2 = ax.twinx()
	ax2.plot(daterange,avg, color = 'b')
	ax2.set_ylabel('Price', color='b')
	for row in list1:
		ax.axvspan(row[0], row[0] + timedelta(days=1), color='y', alpha=0.5, lw=0)
	# print type(list2)
	# print type(total_news_articles)
	# print (list2)
	# print (total_news_articles)
	list2 = [row[0] for row in list2]
	total_news_articles = [row[0] for row in total_news_articles]
	for row in list2:
		ax.axvspan(row, row + timedelta(days=1), color='r', alpha=0.5, lw=0)
	list2 = set(list2)
	total_news_articles = set(total_news_articles)
	not_found_articles = total_news_articles - list2
	not_found_articles = list(not_found_articles)
	not_found_articles.sort()
	for row in not_found_articles:
		ax.axvspan(row, row + timedelta(days=1), color='b', alpha=0.5, lw=0)
	plt.show()


def writeToCSV(lstData,fileName):
	with open(fileName,'w') as out:
		csv_out=csv.writer(out)
		for row in lstData:
			csv_out.writerow(row)

def concateLists(lstData):
	return zip(*lstData)

'''
This function removes nan from the list.

Takes one argument : list of floats

'''

def cleanArray(array):
    result = []
    for element in array:
        if(math.isnan(element)):
            continue
        result.append(element)
    return result
    
def placeMapping(i):
    if (i==0):
    	return "Mumbai"
    elif (i==1):
    	return "Delhi"
    elif(i==2):
    	return "Mumbai"
    elif(i==3):
    	return "Patna"
    elif(i==4):
    	return "Delhi"
    

'''
This function takes one argument:
array: Array of integers, real numbers, etc

returns threshold value to be consider using MAD Test
'''
def MADThreshold(array):
    # return 1.4826*numpy.median(np.array(array))
    array = cleanArray(array)
    array = np.array(array)
    median = numpy.median(array)
    diff = []
    for i in range(0,len(array)):
        diff.append(abs(median - array[i]))
    median_of_diff = numpy.median(np.array(diff))
    tolerance = 1.4826 * median_of_diff
    return (median - tolerance,median + tolerance)
    
'''def MADThreshold(array):
	array = cleanArray(array)
	array = np.array(array)
	median = numpy.median(array, axis=0)
	diff = np.sum((array - median)**2, axis=-1)
	diff = np.sqrt(diff)
	med_abs_deviation = numpy.median(diff)
	modified_z_score = 0.6745 * diff / med_abs_deviation
	return (-1*modified_z_score,modified_z_score)
'''	
'''
This function takes 2 arguments:
array: Array of integers, real numbers, etc
alpha: smoothening factor of exponential average smoothing

returns threshold value to be consider using MAD Test
'''
def smoothArray(array, alpha = 2.0/15.0):
    array = np.array(array,dtype = float)
    if(len(array) == 0):
        return []
    new_data = []
    prevVal = -1
    prevVal = array[0]
    new_data.append(array[0])
    for i in range(1,len(array)):
        newVal = ( array[i] - prevVal ) * alpha + prevVal
        new_data.append(newVal)
        prevVal = newVal   
    return new_data

def csv2array(filePath):
    result = []
    with open(filePath, 'rb') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        for row in csvReader:
            result.append(row)
    return result

def getColumn(array, column_number):
    temp = []
    for x in array:
        temp.append(x[column_number])
    return temp

'''
While reading CSV file, by default it takes each row as string, but second column should be float, so this function does that work.

1 Argument:

z : Array from CSV file consisting of 2 columns, date and values
return same array changing data type of second column to float

'''
def formatCSV2Array(z):
    result = []
    for row in z:
        result.append((row[0],float(row[1])))
    return result

def plotGraph(series1,series2,anomalies):
    dates = [datetime.datetime.strptime(x[0], "%Y-%m-%d").date() for x in series1]
    s1 = [x[1] for x in series1]
    s2 = [x[1] for x in series2]
    html = '''
    <html>
        <body>
            <img src="data:image/png;base64,{}"  height="800" width="1100"/>
        </body>
    </html>
    '''
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(dates,s1,'r')
    ax.plot(dates,s2,'b')
    
    # Highlighting Anomalies
    for i in range(0,len(anomalies)):
        # ax.axvspan(datetime.datetime.strptime(anomalies[i][0], "%Y-%m-%d").date(), datetime.datetime.strptime(anomalies[i][1], "%Y-%m-%d").date(), color='y', alpha=0.5, lw=0)
        ax.axvspan(anomalies[i][0], anomalies[i][1], color='y', alpha=0.5, lw=0)
    
    
    fig.set_size_inches(20,12)
    plt.show()
    io = StringIO.StringIO()
    fig.savefig(io, format='png')
    data = io.getvalue().encode('base64')
    
    trace1 = go.Scatter(
    x=dates,
    y=s1,
    name='Series 1'
    )
    trace2 = go.Scatter(
        x=dates,
        y=s2,
        name='Series 2',
        yaxis='y2'
    )
    data = [trace1, trace2]
    layout = go.Layout(
        title='Correlation Test',
        yaxis=dict(
            title='Series 1'
        ),
        yaxis2=dict(
            title='Series 2',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'
        )
    )
    fig = go.Figure(data=data, layout=layout)
    # plot_url = plotly.offline.plot(fig, filename='graph1', auto_open=False)
    temp = plotly.offline.plot( fig, filename='graph1')
    print "Kapil"
    print temp
    return template('graphPlot', graph=temp)

'''

This function takes one argument:

li: List of tuples of the forms as follows:

(start_date, end_date, value)


It merges windows if it overlaps.

returns list of tuples of the form:

(start_date, end_date, value)

'''
def mergeDates(li):
    # Convert first and second item of tuple to date from string
    # print li
    li = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c) for (a,b,c) in li]
    li = sorted(li, key=lambda x: x[0]) # sort input list
    new_list_of_ranges = [] # output list
    
    new_range_item_start = None
    new_range_item_end = None
    new_value = None
    
    length = len(li)
    for i,range_item in enumerate(li):
        if new_range_item_start is None:
            new_range_item_start = range_item[0]
            new_range_item_end = range_item[1]
            new_value = range_item[2]
        #elif new_range_item_end >= range_item[0]:
        elif((abs(new_range_item_end- range_item[0]).days) == 1):
            new_range_item_end = max(range_item[1], new_range_item_end)
            new_value = max(new_value, range_item[2])
        else:
            new_list_of_ranges.append((new_range_item_start, new_range_item_end, new_value))
            new_range_item_start = range_item[0]
            new_range_item_end = range_item[1]
            new_value = range_item[2]
        # save if this is last item
        if i + 1 == length:
            new_list_of_ranges.append((new_range_item_start, new_range_item_end, new_value))
    return new_list_of_ranges



def resultOfOneMethod(array):
    result = []
    for (a,b,c) in array:
        i = a
        while i <= b:
            result.append((i,c))
            i = i + timedelta(days = 1)
    return result

'''

This function requires minumum 5 arguments:

numOfResults: number of lists you are passing, minimum 2

listi : result from ith alorithm : list
resultOfi : result of which algorithm : string, it can be from following:
            (slope_based, linear_regression, graph_based, spike_detection, multiple_arima)

It finds intersection of all algos.

returns list of tuples.

Return Tuple format:

(date, correlation, slope_based, linear_regression, graph_based, spike_detection, multiple_arima)

'''
def intersection(numOfResults, list1, resultOf1, list2, resultOf2, list3 = [], resultOf3="linear_regression", list4=[], resultOf4="graph_based", list5=[], resultOf5="multiple_arima" , list6=[], resultOf6="spike_detection"):
    # Convert first and second item of tuple to date from string
    # First Combine both the results into one, 3 tuples to 4 tuples -> 4th will be from which time series it is.
    '''
    li1 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf1) for (a,b,c) in list1]
    li2 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf2) for (a,b,c) in list2]
    li3 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf3) for (a,b,c) in list3]
    li4 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf4) for (a,b,c) in list4]
    li5 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf5) for (a,b,c) in list5]
    li6 = [ (datetime.strptime(a, "%Y-%m-%d"),datetime.strptime(b, "%Y-%m-%d"),c, resultOf6) for (a,b,c) in list6]
    '''
    
    li1 = [ (a,b,c, resultOf1) for (a,b,c) in list1]
    li2 = [ (a,b,c, resultOf2) for (a,b,c) in list2]
    li3 = [ (a,b,c, resultOf3) for (a,b,c) in list3]
    li4 = [ (a,b,c, resultOf4) for (a,b,c) in list4]
    li5 = [ (a,b,c, resultOf5) for (a,b,c) in list5]
    li6 = [ (a,b,c, resultOf6) for (a,b,c) in list6]
    
    '''print "LIST 1"
    print li1
    print "LIST 2"
    print li2
    print "LIST 3"
    print li3
    print "List printing done"
    '''
    
    # Append one list to other
    list = li1 + li2 + li3 + li4 + li5 + li6

    temp = dict()

    for (a,b,c,d) in list:
        i = a
        while i <= b:
            # for i in range(a,b+timedelta(days = 1)):
            if(i in temp):
                temp[i] = temp[i] + 1
            else:
                temp[i] = 1
            i = i + timedelta(days = 1)

    dates_to_consider = set()
    for i in temp:
        if(temp[i] == numOfResults):
            dates_to_consider.add(i)
    
    #print "FInal anomaly dates are : "
    #print dates_to_consider
    #print "date printing done"
    
    # Fetch data
    results = dict()
    for (a,b,c,d) in list:
        i = a
        while i <= b:
            # for i in range(a,b+timedelta(days = 1)):
            if(i in dates_to_consider):
                if(i in results):
                    previous_tuple = results[i]
                else:
                    previous_tuple = [i,0,0,0,0,0,0]
                if(d == "correlation"):
                    previous_tuple[1] = c
                elif(d== "slope_based"):
                    previous_tuple[2] = c
                elif(d== "linear_regression"):
                    previous_tuple[3] = c
                elif(d== "graph_based"):
                    previous_tuple[4] = c
                elif(d== "spike_detection"):
                    previous_tuple[5] = c
                elif(d== "multiple_arima"):
                    previous_tuple[6] = c
                results[i] = previous_tuple
            i = i + timedelta(days = 1)


    # output list
    new_list_of_ranges = [] 
    for i in results:
        new_list_of_ranges.append(results[i])

    #Sort it
    new_list_of_ranges = sorted(new_list_of_ranges, key=lambda x: x[0])

    return new_list_of_ranges


'''

Takes intersection of 2 lists of the form:
(date, correlation, slope_based, linear_regression, graph_based, spike_detection, multiple_arima)

return list of tuple of the same form....

'''

def intersectionOfFinalResults(list1, list2):
    list1Set = set()
    for tuple in list1:
        list1Set.add(tuple[0])
        
    result = []
    for tuple in list2:
        if(tuple[0] in list1Set):
            result.append(tuple)
    
    return result

'''

Takes union of 2 lists of the form:
(date, correlation, slope_based, linear_regression, graph_based, spike_detection, multiple_arima)

return list of tuple of the same form....

'''
def unionOfFinalResults(list1, list2):
    result = []
    list1Set = set()
    for tuple in list1:
        list1Set.add(tuple[0])
        result.append(tuple)
    
    for tuple in list2:
        if(tuple[0] not in list1Set):
            result.append(tuple)
    result = sorted(result, key=lambda x: x[0])
    
    return result

# For reading Graph based anomaly results
# Read CSVs and get top 500 results

def removeQuotes(string):
    if string.startswith('"') and string.endswith('"'):
        return string[1:-1]
    return string

def getGBAResultsRvR(i, numOfPtsReqd):
    if(i==0):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/abd1gba.csv"
    elif(i==1):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/bglr2gba.csv"
    elif(i==2):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/mumbai3gba.csv"
    elif(i==3):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/patna4gba.csv"
    elif(i==4):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/delhi5gba.csv"
    
    results = []
    for i,line in enumerate(open(file)):
        line = line.strip()
        tokens = line.split(",")

        date = removeQuotes(tokens[3])
        value = float(removeQuotes(tokens[1]))
        rank = int(removeQuotes(tokens[2]))
        results.append((date,value,rank))
    
    # Sort by rank
    results = sorted(results, key=lambda x: x[2])
    
    # Take top numOfPtsReqd
    results = results[0:numOfPtsReqd]
    
    # Sort by date
    results = sorted(results, key=lambda x: x[0])
    
    results = [ (datetime.strptime(a, "%d/%m/%y"),datetime.strptime(a, "%d/%m/%y"),b) for (a,b,c) in results]
    
    return results

def getGBAResultsRvA(i, numOfPtsReqd):
    if(i==0):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/abd1gbaRetailVsArr.csv"
    elif(i==1):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/bglr2gbaRetailVsArr.csv"
    elif(i==2):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/mumbai3gbaRetailVsArr.csv"
    elif(i==3):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/patna4gbaRetailVsArr.csv"
    elif(i==4):
        file = "/home/kapil/Desktop/mtp/library/resultsOfGBA/delhi5gbaRetailVsArr.csv"
    
    results = []
    for i,line in enumerate(open(file)):
        line = line.strip()
        tokens = line.split(",")
        date = removeQuotes(tokens[3])
        value = float(removeQuotes(tokens[1]))
        rank = int(removeQuotes(tokens[2]))
        results.append((date,value,rank))
    
    # Sort by rank
    results = sorted(results, key=lambda x: x[2])
    
    # Take top numOfPtsReqd
    results = results[0:numOfPtsReqd]
    
    # Sort by date
    results = sorted(results, key=lambda x: x[0])
    
    results = [ (datetime.strptime(a, "%d/%m/%y"),datetime.strptime(a, "%d/%m/%y"),b) for (a,b,c) in results]
    
    return results

'''

this function takes one argument:

array: list of tuples of the following form:
        (System_anomaly_date, news_article_date, news_source, source_url, difference_between_system_date_and_news_article_date, list_of_keywords)
        
This function will create bins for "difference_between_system_date_and_news_article_date"

returns array of tuples of the following form:

    (a,b)
    
    Where a: one of the distinct value from "difference_between_system_date_and_news_article_date"
          b: How many a's are present

'''

def getDiffStatsOfNewsArticles(array, array2):
	# First let's return year by year result
	news_present = dict()
	news_matched_with_system = dict()
	
	
	for row in array2:
		if(row[0].year in news_present):
			news_present[row[0].year] = news_present[row[0].year] + 1
		else:
			news_present[row[0].year] = 1
			
	for row in array:
		if(row[0].year in news_matched_with_system):
			news_matched_with_system[row[0].year] = news_matched_with_system[row[0].year] + 1
		else:
			news_matched_with_system[row[0].year] = 1
	
	news_present_array = []
	news_matched_with_system_array = []
	
	for key in news_present:
		news_present_array.append((key,news_present[key]))
	
	for key in news_matched_with_system:
		news_matched_with_system_array.append((key,news_matched_with_system[key]))
	
	news_present_array = sorted(news_present_array, key=lambda x: x[0])
	news_matched_with_system_array = sorted(news_matched_with_system_array, key=lambda x: x[0])
	
	print "News Present in Database : "
	for row in news_present_array:
		print row
	print "News matched with our system: "
	for row in news_matched_with_system_array:
		print row
		
	bins = dict()
	for row in array:
		if(row[4] in bins):
			bins[row[4]] = bins[row[4]] + 1
		else:
			bins[row[4]] = 1
			
	result = []
	for key in bins:
		result.append((key,bins[key]))
		
	# Sort by first element of tuple
	result = sorted(result, key=lambda x: x[0])
	return result 

#dt= datetime.strptime('2010-01-01' , '%Y-%m-%d')
#csvTransform("/home/reshma/Desktop/Arrivalresults.csv",dt)
#csvTransform("/home/kapil/Desktop/mtp/library/testingCSV/Retailresults.csv",dt)

'''
This function takes 2 arguments:
numOfLists: It stats number of lists, whose union is to be found
lists: each element of lists is a list, whose union is to be found, each of this list should be list of tuples, whose first element should be date

returns list of dates after union
'''

def union(numOfLists, *lists):
	n = len(lists)
	dates = set()
	for lst in lists:
		for row in lst:
			dates.add(row[0])
	result = list(dates)
	result.sort()
	result = [(date,) for date in result]
	return result
	pass

'''
This function takes 2 arguments:
list1 : list of dates in tuple format (date,)
list2 : list of dates

returns intersection of list1 and list2
'''

def intersect(list1,list2):
	dates1 = set()
	result = set()
	for date in list1:
		dates1.add(date[0])
	for date in list2:
		if(date[0] in dates1):
			result.add(date[0])
	result = list(result)
	result.sort()
	result =[(date,) for date in result]
	return result


def getYearWiseStats(*results):
	numOfColumns = len(results)
	columns = dict()
	result = []
	if(numOfColumns == 8):
		tempList1 = [2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
	else: # numOfColumns = 9
		tempList1 = [2010,2011,2012,2013,2014,2015]
	columns[0] = result = tempList1
	i = 1
	for lst in results:
		vals = dict()
		for val in tempList1:
			vals[val] = 0
		for Tuple in lst:
			vals[Tuple[0].year] = vals[Tuple[0].year] +1
		temp = []
		for val in tempList1:
			temp.append(vals[val])
		columns[i] = temp
		i = i+1
	# for i in range(1,numOfColumns+1):
	# 	result = zip(result,columns[i])
	
		
	if(numOfColumns == 8):
		result = zip(columns[0],columns[1],columns[2],columns[3],columns[4],columns[5],columns[6],columns[7],columns[8])
	else: # numOfColumns = 9
		result = zip(columns[0],columns[1],columns[2],columns[3],columns[4],columns[5],columns[6],columns[7],columns[8],columns[9])
	return result


'''
This function is just to take series from 2010 onwards for the graph based anomaly method.
Cuts given 2 input list and start from 2010 and returns them
'''
def processListForGB(listOfList):
	oneList = listOfList[0]
	tempList = [datetime.strptime(row[0],"%Y-%m-%d") for row in oneList]
	date = datetime.strptime("2010-01-01","%Y-%m-%d")
	i = 0
	for dateVal in tempList:
		if(date<dateVal):
			break
		i=i+1
	result = []
	for anyList in listOfList:
		result.append(anyList[i:])
	return result

'''
This function will help to determine how much news articles are away from anomaly normally.

Takes input list of tuples of the form:

(System_anomaly_date, news_article_date, news_source, source_url, difference_between_system_date_and_news_article_date ,reason, comment, days_compared_in_article)

returns list of tuples the form:
(difference_between_system_date_and_news_article_date, number_of_articles_with_this_value)

'''
def newsAnomalyDiffDays(array):
	data = dict()
	for row in array:
		if(row[4] not in data):
			data[row[4]] = 1
		else:
			data[row[4]] = data[row[4]] + 1
	result = []
	for key in data:
		result.append((key,data[key]))
	result.sort()
	return result
	pass