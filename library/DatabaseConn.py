import psycopg2
import datetime

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
				(System_anomaly_date, news_article_date, news_source, source_url, difference_between_system_date_and_news_article_date, list_of_keywords)
				
				1. System_anomaly_date: date reported by our system which is reported as anomolous date
				2. news_article_date: date of news article correpsonding to above System_anomaly_date
				3. news_source: souce of news (which media?)
				4. source_url: link of the news article
				5. difference_between_system_date_and_news_article_date: difference between dates of (news_article_date - System_anomaly_date)
				6. list_of_keywords: List of keywords related with this article
				
* allArticlesQueryResult: List of dates of all news articles for this center which is present in the database


'''

def fetchNewsForCenter(resultsOfSystem, centerNumber, intervalToConsider=5):
	center = ""
	
	if(centerNumber == 0):
		center = "Ahmedabad"
	elif(centerNumber == 1):
		center = "Bengaluru"
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
		date = row_resultsOfSystem[0].date()
		
		start_date = date - datetime.timedelta(days=-1*intervalToConsider)
		start_date = start_date.strftime('%Y/%m/%d')
		end_date = date + datetime.timedelta(days=intervalToConsider)
		end_date = end_date.strftime('%Y/%m/%d')
		
		query = "select publish_date, name, source_url, article_hash_url from articlemetadata amd, newssource ns where amd.source_id = ns.id and publish_date >= '"+start_date+"' and publish_date<= '"+end_date+"' and article_hash_url in (select distinct(article_id) from alchemyentity where entity iLike '"+center+"' )"
		cur.execute(query)
		queryResult = cur.fetchall()
		
		resultOfThisDate = []
		for row_queryResult in queryResult:			
			# Find All keyword corresponding to that article using : article_hash_url
			query = "select keyword from alchemykeyword where article_id = '" + row_queryResult[3] + "'"
			cur.execute(query)
			keywordQueryResult = cur.fetchall()
			smallTuple = (row_queryResult[0], row_queryResult[1], row_queryResult[2], (row_queryResult[0] - date).days, keywordQueryResult)
			resultOfThisDate.append(smallTuple)
		result[date] = resultOfThisDate
		
	# Fetch all dates of news articles corresponding to this center
	query = "select distinct publish_date from articlemetadata where article_hash_url in (select distinct(article_id) from alchemyentity where entity iLike '"+center+"' )"
	cur.execute(query)
	allArticlesQueryResult = cur.fetchall()
	
	# Convert result to list from dictionary
	resultList = []
	for date in result:
		temp_list = result[date]
		for row_temp_list in temp_list:
			(a,b,c,d,e) = row_temp_list
			resultList.append((date,a,b,c,d,e))
	# Sort by anomaly date
	resultList = sorted(resultList, key=lambda x: x[0])
	
	return(resultList, allArticlesQueryResult)


def Conn(dd,place):
	conn = psycopg2.connect(database="news_articles", user="postgres", password="password", host="127.0.0.1", port="5432")
	cur = conn.cursor()
	
	intervalToConsider =5
	start_date =dd+ datetime.timedelta(days=-1*intervalToConsider)
	start_date = start_date.strftime('%Y/%m/%d')
	end_date = dd + datetime.timedelta(days=intervalToConsider)
	end_date = end_date.strftime('%Y/%m/%d')
	
	cur.execute("select * from articlemetadata am, newssource ns, articleauthor aa where publish_date >= '"+start_date+"' and publish_date<= '"+end_date+"' and ns.id= am.source_id and am.article_hash_url= aa.article_id")
	rows = cur.fetchall()
	listDict =[]
	for row in rows:
	   article_id= row[0]
	   title = row[1]
 	   publish_date = row[2]
 	   onlytext= row[3]
 	   sourcename = row[21]
 	   exact_url = row[6]
 	   source_url= row[22]
 	   
 	   
 	   '''
 	   	b169b4ff0549ce6f0f4bf01f81307b2c
		Prices slump as early harvest rains potatoes, onions too may turn cheaper
		2010-11-17
		While consumers may gain from low prices in the short term, potato may become costly later because experts say the market may see a shortfall after the glut as rain-hit crops cannot be stored for long. Farmers said cold storage owners were not ready to take potato crop with moisture as it could rot other crops.
		economictimes.indiatimes.com
		http://articles.economictimes.indiatimes.com/2015-03-19/news/60286644_1_potato-crop-potato-traders-potato-prices
		The Economic Times

 	   '''
	   entityCurr = conn.cursor()
	   entityCurr.execute("select * from alchemyentity where article_id = '"+ article_id+"'")
	   entityrows = entityCurr.fetchall()
	   flag=0
	   for r in entityrows:
	   	entityName = r[2]
		if(place.lower() in entityName.lower()):
			dictsample={'article_id': article_id,'title':title,'publish_date':publish_date, 'sourcename':sourcename, 'exact_url':exact_url,'source_url':source_url}
			#'onlytext':onlytext,
			flag=1
			listDict.append(dictsample)
			break
	   if(flag==0):
		   keywordCurr = conn.cursor()
		   keywordCurr.execute("select * from alchemykeyword where article_id = '"+ article_id+"'")
		   keywordrows = keywordCurr.fetchall()
		   for r in keywordrows:
			keyName = r[2]
			if(place.lower() in keyName.lower()):
				dictsample={'article_id': article_id,'title':title,'publish_date':publish_date,'onlytext':onlytext, 'sourcename':sourcename, 'exact_url':exact_url,'source_url':source_url}
				listDict.append(dictsample)
				break
				
	conn.close()
	return listDict
	
def ConnQuery(query):
	conn = psycopg2.connect(database="news_articles", user="postgres", password="password", host="127.0.0.1", port="5432")
	cur = conn.cursor()
	
	
	
	cur.execute(query)
	rows = cur.fetchall()
	result =[]
	for row in rows:
	   dates= row
	   result.append(dates)
	conn.close()
	return dates