Here, each folder represents news source. When you visit that folder, you will see html pages named as natural numbers in order. These HTML pages are saved manually doing manual search on news.google.com.

Query to search news (All of these words): onion price
Date Range: 1/1/2006 to 4/4/2016
Location: India
News Souce: <Different for different query>

------------------------------------------------------------------------------------------------------

Note : pioneer source had no news articles

-------------------------------------------------------------------------------------------------------

there are multiple folders in this directory corresponding to each news source as,

sourcefolder = 'hindustan_times/'
sourcename = 'The Hindustan Times'
sourceid = '1'
sourcehomepage = 'hindustantimes.com'
typeofpaper='National Regular Daily'


.....................................................................................

We select one by one of this and comment rest and execute script (html2csv.py). Each execution creates csv according to sourceid of that news source.

----------------------------------------------------------------------------------------------------------------------

combine_csv.sh :

This shell script is used to combine all the CSVs generated using html2csv.py script.
It takes total 17 scripts right now, numbered from 1 to 17. If you have diffenet number of CSVs change it in shell script.
After combining all CSVs it creates csv named "output.csv". If you want to change it, make change in script.

