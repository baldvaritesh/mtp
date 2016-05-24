import psycopg2

# Query : select distinct article_hash_url,exact_url from articlemetadata where article_hash_url NOT IN (select distinct article_id from analysis);
# Updated Query: select distinct article_hash_url,exact_url from articlemetadata where article_hash_url NOT IN (select distinct article_id from analysis) order by article_hash_url asc;
# New Query: select article_hash_url,publish_date, exact_url from articlemetadata where extract(year from publish_date) = 2006;

conn = psycopg2.connect(database="news_articles", user="postgres", password="password", host="127.0.0.1", port="5432")

def addToAnalysis(article_hash_url, place, reason, comment, days):
    cur = conn.cursor()
    query = "INSERT INTO analysis(article_id, place, reason, comment, days) VALUES ('"+article_hash_url+"', '"+place+"', '"+reason+"', '"+comment+"',"+days+");"
    cur.execute(query)
    conn.commit()
    
def deleteArticle(article_hash_url):
    pass

def isArticleExist(hash_url):
    cur = conn.cursor()
    query = "Select * from analysis where article_id='" + hash_url + "';"
    cur.execute(query)
    rows = cur.fetchall()
    if(len(rows) > 0) :
        return True
    else:
        return False

def updateDateInArticleMetadata(hash_url, updatedDate):
    cur = conn.cursor()
    query = "Update articlemetadata set publish_date = '"+ updatedDate +"' where article_hash_url='" + hash_url + "';"
    cur.execute(query)
    conn.commit()

while(True):
    option = int(raw_input("Do you want to continue? (1-Yes, 2 -No) \n\n"))
    if(option == 2):
        break
    hash_url = raw_input("Enter hash of url of article \n\n")
    # keep = int(raw_input("Do you want to delete this article? (1-Yes, 2 -No) \n\n"))
    article_check = isArticleExist(hash_url)
    if(article_check):
        print "**********************************************************************"
        print "Just check date of article. Article is already processed before. \n\n"
        print "**********************************************************************"
    updateDate = int(raw_input( "Do you want to update date? (1-Yes, 2 -No) \n\n"))
    if(updateDate == 1):
        updatedDate = raw_input("Input new date in the format (YYYY-MM-DD) \n\n")
        updateDateInArticleMetadata(hash_url, updatedDate)
    
    # if(keep == 1):
    #     pass
    # else:
    while(True):
        cont = int(raw_input("Do you want to add to table for this article? (1-Yes, 2 -No) \n\n"))
        if(cont == 2):
            break
        else:
            print "Select Place:"
            print "1 - Ahmedabad"
            print "2 - Delhi"
            print "3 - Mumbai"
            print "4 - Banglore"
            print "5 - Patna"
            print "6 - Chennai"
            print "7 - Kolkata"
            print "8 - Chandigarh"
            print "9 - Nashik"
            print "10 - Other"
            placeOption = int(raw_input("Select one from above \n\n"))
            if(placeOption == 1):
                place = "Ahmedabad"
            elif(placeOption == 2):
                place = "Delhi"
            elif(placeOption == 3):
                place = "Mumbai"
            elif(placeOption == 4):
                place = "Banglore"
            elif(placeOption == 5):
                place = "Patna"
            elif(placeOption == 6):
                place = "Chennai"
            elif(placeOption == 7):
                place = "Kolkata"
            elif(placeOption == 8):
                place = "Chandigarh"
            elif(placeOption == 9):
                place = "Nashik"
            else:
                place = ""
                while(place == ""):
                    place = raw_input("Enter Place \n\n")
            print "Select Reason:"
            print "1 - unseasonal rainfall"
            print "2 - traders nexus"
            print "3 - low production"
            print "4 - not stated"
            print "5 - prices dropped"
            print "6 - low supply"
            print "7 - other"
            reasonOption = int(raw_input("Select one from above \n\n"))
            if(reasonOption == 1):
                reason = "unseasonal rainfall"
            elif(reasonOption == 2):
                reason = "traders nexus"
            elif(reasonOption == 3):
                reason = "low production"
            elif(reasonOption == 4):
                reason = "not stated"
            elif(reasonOption == 5):
                reason = "prices dropped"
            elif(reasonOption == 6):
                reason = "low supply"
            else:
                reason = ""
                while(reason == ""):
                    reason = raw_input("Enter Reason \n\n")
            # Add to database
            comment = raw_input("Any comment? \n\n")
            days = raw_input("Number of days for which prices are compared \n\n")
            addToAnalysis(hash_url,place,reason, comment, days)
                
conn.close()