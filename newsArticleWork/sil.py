from alchemyapi import AlchemyAPI
from client import DiffbotClient
from config import API_TOKEN
import psycopg2
import time
import json
import pandas as pd
import time
import datetime

######################################################################
##########          BEAUTIFUL SOUP: START                     ########
######################################################################

# Diffbot gave error in fetching dates for Hindustan times, dna, firstpost, ndtv. So beautiful soup is used for that

import urllib2,cookielib
from lxml import etree

date_xpath_ht = '/html/head/meta[@property="article:published_time"]/@content'
date_xpath_dna = '/html/head/meta[@property="og:updated_time"]/@content'
date_xpath_firstpost = '/html/head/article/meta[@property="article:published_time"]/@content'
date_xpath_ndtv = "/html/head/meta[@name='publish-date']/@content"

# ht : <meta property="article:published_time" content="2015-08-22T02:00Z">
# ndtv : <meta name='publish-date' content='Wed, 01 Jul 2015 12:23:28 +0530'/>
# firstpost : <meta property="article:published_time" content="2014-10-14T10:25:32+05:30" />
# dna : <meta property="og:updated_time" content="2015-08-20T14:57:00+05:30" />

def getDate(url, news_souce):
    publish_fmt = "%a, %d %b %Y %H:%M:%S %Z"
    if(news_souce == 'dna'):
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = urllib2.Request(url,headers=hdr)
        response = urllib2.urlopen(req)
    else:
        response = urllib2.urlopen(url)
    htmlparser = etree.HTMLParser()
    tree = etree.parse(response, htmlparser)
    print tree
    if(news_souce == 'ht'):
        date_object = tree.xpath(date_xpath_ht)
        # Format :  2015-08-22T02:00Z
        date =  date_object[0]
        date = date.split("T")[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date.strftime(publish_fmt)
        return date
    elif(news_souce == 'dna'):
        date_object = tree.xpath(date_xpath_dna)
        # Format : 2015-08-20T14:57:00+05:30
        date = date_object[0]
        date = date.split("T")[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date.strftime(publish_fmt)
        return date
    elif(news_souce == 'firstpost'):
        # 2014-10-14T10:25:32+05:30
        date_object = tree.xpath(date_xpath_firstpost)
        date = date_object[0]
        date = date.split("T")[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date.strftime(publish_fmt)
        return date
    elif(news_souce == 'ndtv'):
        date_object = tree.xpath(date_xpath_ndtv)
        # Wed, 01 Jul 2015 12:23:28 +0530
        date = date_object[0]
        date = date.split("+")[0]
        date =date.strip()
        date = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S')
        date = date.strftime(publish_fmt)
        return date

    # date path : /html/body/div[1]/div[2]/section/div/div[1]/div[2]/ul/li[2]

def getNewsSource(exact_url):
    if(exact_url.find('www.hindustantimes.com') >= 0 ):
        return 'ht'
    elif(exact_url.find('www.dnaindia.com') >= 0 ):
        return 'dna'
    elif(exact_url.find('www.firstpost.com') >= 0 ):
        return 'firstpost'
    elif(exact_url.find('ndtv.com') >= 0 ):
        return 'ndtv'

######################################################################
##########          BEAUTIFUL SOUP: END                       ########
######################################################################



##Globals##
####Urls
csv_file = 'Articles/test.csv'
df_urls = pd.read_csv(csv_file)

####Alchemy object
alchemyapi = AlchemyAPI()

####Diffbot object
diffbot = DiffbotClient()
token = API_TOKEN
api = "article"

####PSQL cursor
conn_string = "host='localhost' dbname='news_articles' user='postgres' password='password'" 
conn = psycopg2.connect(conn_string) 
cursor = conn.cursor()
####Article Globals
meta_author = ''#to be used in set_author table
meta_text = '' #to be used with alchemy

def set_meta_table(article_hash,opinion_section,source_id,search_text_hash,exact_url,page_number,pos_on_page):
    
    print('')
    print "## running diffbot!"
    response = diffbot.request(exact_url,token,api,timeout=50000, verify = False)
    #print type(response)

    print "## diffbot parsing done!"
    onlytext,author = '',''
    if 'objects' in response.keys():
        parsed_objects = response['objects']
    else:
        print "Cannot parse for - {}".format(exact_url)
        return onlytext,author

    for p in parsed_objects:
        # print p
        title = p['title']
        onlytext = p['text']
        html = p['html']
        if 'author' in p.keys():
            author = p['author'] #how multiple authors represented???
        #publish_date = 'Sun, 1 Jan 1900 00:00:00 GMT'
        publish_date = ''
        # print p
        publish_fmt = "%a, %d %b %Y %H:%M:%S %Z"
        if 'date' in p.keys():            
            publish_date = p['date']
            publish_datetime =  datetime.datetime.strptime(publish_date,publish_fmt)
        else:
            news_souce = getNewsSource(exact_url)
            publish_datetime = getDate(exact_url,news_souce)


    word_count = len(onlytext.strip().split())
    analysis_date = time.asctime(time.localtime(time.time()))

    print "## Running alchemyapi"  
    response = alchemyapi.sentiment('text',onlytext)
    if response['status'] == "OK":
        document_sentiment =  response['docSentiment']['type']
        # print "##Document Sentiment - {}".format(document_sentiment)
        score = 0.0
        if 'score' in response['docSentiment']:
            score = response['docSentiment']['score']
            print "##Score - {}".format(score)

        source_url = exact_url #Why need this field???
        analysis_fmt = "%a %b %d %H:%M:%S %Y"
        
        analysis_datetime = datetime.datetime.strptime(analysis_date,analysis_fmt)
        


        sql_query = "insert into ArticleMetaData( \
                    article_hash_url , title, publish_date,\
                    onlytext, source_id, source_url, exact_url, \
                    opinion_section,search_text_hash, word_count, \
                    analysis_date, document_sentiment,pos_on_page,\
                    page_number, score) values " 

        query_fmt ="(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        query = sql_query + query_fmt
        t = (article_hash_url,title,publish_datetime,\
                onlytext,source_id, source_url, exact_url, opinion_section,\
                search_text_hash,word_count,analysis_datetime, \
                document_sentiment,pos_on_page,page_number,score)
        print "##Printing query -"
        print (query%t).encode("utf-8")

        try:
            print " "
            print "## Writing to DB----"
            cursor.execute(query,(article_hash_url,title,publish_datetime,\
                    onlytext,source_id, source_url, exact_url, opinion_section,\
                    search_text_hash,word_count,analysis_datetime, \
                    document_sentiment,pos_on_page,page_number,score))
            conn.commit()
            print "## DB Write success!! "
        except Exception,e:
            print "## DB write failed!!"
            print repr(e)
            conn.rollback()
            exit(5)

    else:
        print('Error in sentiment call: ', response['statusInfo'])
        exit(10)


    return onlytext,author


def set_entity_table(article_id,demo_text):
    
    print('')
    print "**setting entity table**"
    response = alchemyapi.entities('text', demo_text, {'sentiment': 1})
    if response['status'] == 'OK':

        print('## Entities ##')
        for entity in response['entities']:
            print('article_id:',article_id)
            text = entity['text'].encode('utf-8')
            print('text: ', text)
            e_type = entity['type']
            print('type: ', e_type)
            relevance = entity['relevance']
            print('relevance: ',relevance )
            sentiment_type = entity['sentiment']['type']
            print('sentiment: ', sentiment_type)
            sentiment_score =0.0
            if 'score' in entity['sentiment']:
                sentiment_score = entity['sentiment']['score']
                print('sentiment score: ' + sentiment_score)
            dbpedia = ''
            if 'disambiguated' in entity.keys():
                dbpedia = entity['disambiguated']['dbpedia']
            print('')

            sql_query = "insert into AlchemyEntity( \
                    article_id , entity, relevance,\
                    sentiment, type, dbpedia) values " 

            query_fmt ="(%s,%s,%s,%s,%s,%s)"
            query = sql_query + query_fmt
            try:
                print "## Writing to DB----"
                cursor.execute(query,(article_id,text,relevance,sentiment_type,\
                                e_type,dbpedia))
                conn.commit()
                print "## DB Write success!! "
            except Exception,e:
                print "## DB write failed!!"
                print repr(e)
                db.rollback()
                exit(4)
    else:
        print('Error in entity extraction call: ', response['statusInfo'])

    return


def set_keyword_table(article_id,demo_text):
    
    print('')
    print "**setting keyword table**"
    response = alchemyapi.keywords('text', demo_text, {'sentiment': 1})
    if response['status'] == 'OK':

        print('## Keywords ##')
        for keyword in response['keywords']:
            print('article_id:',article_id)
            text = keyword['text'].encode('utf-8')
            print('text: ', text)
            relevance = keyword['relevance']
            print('relevance: ',relevance )
            sentiment_type = keyword['sentiment']['type']
            print('sentiment: ', sentiment_type)
            sentiment_score =0.0
            if 'score' in keyword['sentiment']:
                sentiment_score = keyword['sentiment']['score']
                print('sentiment score: ' + sentiment_score)
            print('')

            sql_query = "insert into AlchemyKeyword( \
                    article_id , keyword, relevance,\
                    sentiment) values " 

            query_fmt ="(%s,%s,%s,%s)"
            query = sql_query + query_fmt
            try:
                print "## Writing to DB----"
                cursor.execute(query,(article_id,text,relevance,sentiment_type))
                conn.commit()
                print "## DB Write success!! "
            except Exception,e:
                print "## DB write failed!!"
                print repr(e)
                db.rollback()
                exit(3)
    else:
        print('Error in keyword extraction call: ', response['statusInfo'])

    return

def set_taxonomy_table(article_id,demo_text):
    
    print('')
    print "**setting taxonomy table**"
    response = alchemyapi.taxonomy('text', demo_text)
    if response['status'] == 'OK':

        print('## Taxonomy ##')
        for category in response['taxonomy']:
            print('article_id:',article_id)
            taxonomy_label = category['label']
            print('label: ', taxonomy_label)
            score = category['score']
            print('score: ',score )
            confident = ''
            if 'confident' in category.keys():
                confident = category['confident']
                print('confident:',confident)

            print('')
            if(confident == ''):
                confident = 'NA'

            sql_query = "insert into AlchemyTaxonomy( \
                    article_id , taxonomy_label, score, confident) values " 

            query_fmt ="(%s,%s,%s,%s)"
            query = sql_query + query_fmt
            try:
                print "## Writing to DB----"
                cursor.execute(query,(article_id,taxonomy_label, score,confident))
                conn.commit()
                print "## DB Write success!! "
            except Exception,e:
                print "## DB write failed!!"
                print repr(e)
                db.rollback()
                exit(2)
    else:
        print('Error in taxonomy call: ', response['statusInfo'])

    return

def set_author_table(article_id,author):
    
    print('')
    print "**setting author table**"

    print('## Author ##')
    print('article_id:',article_id)
    print('author:',author)
    print('')

    sql_query = "insert into ArticleAuthor( \
            article_id , author) values " 

    query_fmt ="(%s,%s)"
    query = sql_query + query_fmt
    try:
        print "## Writing to DB----"
        cursor.execute(query,(article_id,author))
        conn.commit()
        print "## DB Write success!! "
    except Exception,e:
        print "## DB write failed!!"
        print repr(e)
        db.rollback()
        exit(1)

    return

if __name__ == "__main__":

        for i,r in df_urls.iterrows():
            ####Taken from csv
            print "processing Index: {} of 621".format(r['index'])
            article_hash_url = r['article_hash_url']
            page_number = r['page_number']
            pos_on_page = r['pos_on_page']
            page_number = r['page_number']
            opinion_section = r['opinion_section']
            source_id = r['source_id']
            search_text_hash = 'npa'
            exact_url = r['exact_url']
            print ("Print exact_url:",exact_url)
            #### Taken from csv

            meta_text,meta_author = set_meta_table(article_hash_url,opinion_section,source_id,search_text_hash,exact_url,page_number,pos_on_page)
            if meta_text == '':
                print "No parsed content from diffbot! Moving to next record. Index: {}".format(r['index'])
                exit(1)
            set_entity_table(article_hash_url,meta_text)
            set_keyword_table(article_hash_url,meta_text)
            set_taxonomy_table(article_hash_url,meta_text)
            set_author_table(article_hash_url,meta_author)

	conn.close()
