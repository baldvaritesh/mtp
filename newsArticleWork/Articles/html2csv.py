from bs4 import BeautifulSoup
import os
import sys
import hashlib

if sys.version_info[0] > 2:
    from urllib.parse import urlparse, parse_qs
else:
    from urlparse import urlparse, parse_qs


# Filter links found in the Google result pages HTML code.
# Returns None if the link doesn't yield a valid result.
def filter_result(link):
    try:

        # Valid results are absolute URLs not pointing to a Google domain
        # like images.google.com or googleusercontent.com
        o = urlparse(link, 'http')
        if o.netloc and 'google' not in o.netloc:
            return link

        # Decode hidden URLs.
        if link.startswith('/url?'):
            link = parse_qs(o.query)['q'][0]

            # Valid results are absolute URLs not pointing to a Google domain
            # like images.google.com or googleusercontent.com
            o = urlparse(link, 'http')
            if o.netloc and 'google' not in o.netloc:
                return link

    # Otherwise, or on error, return None.
    except Exception:
        pass
    return None

def somefn(filename):
    only_standard = True
    hashes = set() ## contains a number! ##can be md5hashtoo!
    html = open(filename,'r')
    soup = BeautifulSoup(html,"lxml")
    anchors = soup.find(id='search').findAll('a')

    #current position
    currpos = 0
    
    for a in anchors:

        # Leave only the "standard" results if requested.
        # Otherwise grab all possible links.
        if only_standard and (
                    not a.parent or a.parent.name.lower() != "h3"):
            continue

        # Get the URL from the anchor tag.
        try:
            link = a['href']
        except KeyError:
            continue

        # Filter invalid links and links pointing to Google itself.
        link = filter_result(link)
        if not link:
            continue
            
        currpos= currpos + 1

        # Discard repeated results.
        # h = hash(link)
        # if h in hashes:
        #    continue
        # hashes.add(h)

        # Yield the result.
        yield link,currpos


#def main():



#################################################################################
'''
sourcefolder = 'hindustan_times/'
sourcename = 'The Hindustan Times'
sourceid = '1'
sourcehomepage = 'hindustantimes.com'
typeofpaper='National Regular Daily'

sourcefolder = 'the_hindu/'
sourcename = 'The Hindu'
sourceid = '2'
sourcehomepage = 'http://www.thehindu.com/'
typeofpaper='National Regular Daily'

sourcefolder = 'the_economic_times/'
sourcename = 'The Economic Times'
sourceid = '3'
sourcehomepage = 'economictimes.indiatimes.com'
typeofpaper='National Financial Daily'


sourcefolder = 'times_of_india/'
sourcename = 'The Times of India'
sourceid = '4'
sourcehomepage = 'timesofindia.indiatimes.com'
typeofpaper='National Regular Daily'

sourcefolder = 'the_indian_express/'
sourcename = 'The Indian Express'
sourceid = '5'
sourcehomepage = 'indianexpress.com'
typeofpaper='National Regular Daily'

sourcefolder = 'dna/'
sourcename = 'DNA'
sourceid = '6'
sourcehomepage = 'dnaindia.com'
typeofpaper='National Regular Daily'

sourcefolder = 'business_standard/'
sourcename = 'Business Standard'
sourceid = '7'
sourcehomepage = 'business-standard.com'
typeofpaper='National Financial Daily'

sourcefolder = 'deccan_chronicle/'
sourcename = 'Deccan Chronicle'
sourceid = '8'
sourcehomepage = 'deccanchronicle.com'
typeofpaper='Regional Regular Daily'

sourcefolder = 'telegraph/'
sourcename = 'Telegraph'
sourceid = '9'
sourcehomepage = 'telegraphindia.com'
typeofpaper='Regional Regular Daily'

sourcefolder = 'pioneer/'
sourcename = 'Daily Pioneer'
sourceid = '10'
sourcehomepage = 'dailypioneer.com'
typeofpaper='Regional Regular Daily'

sourcefolder = 'new_indian_express/'
sourcename = 'New Indian Express'
sourceid = '11'
sourcehomepage = 'newindianexpress.com'
typeofpaper='Regional Regular Daily'

sourcefolder = 'tribuneindia/'
sourcename = 'Tribune'
sourceid = '12'
sourcehomepage = 'tribuneindia.com'
typeofpaper='Regional Regular Daily'

sourcefolder = 'livemint/'
sourcename = 'Live Mint'
sourceid = '13'
sourcehomepage = 'livemint.com'
typeofpaper='Online Regular'

sourcefolder = 'firstpost/'
sourcename = 'First Post'
sourceid = '14'
sourcehomepage = 'firstpost.com'
typeofpaper='Online Regular'

sourcefolder = 'ndtv/'
sourcename = 'NDTV'
sourceid = '15'
sourcehomepage = 'ndtv.com'
typeofpaper='News Channel'

sourcefolder = 'zeenews/'
sourcename = 'Zee News'
sourceid = '16'
sourcehomepage = 'zeenews.com'
typeofpaper='News Channel'

sourcefolder = 'moneycontrol/'
sourcename = 'Money Control'
sourceid = '17'
sourcehomepage = 'moneycontrol.com'
typeofpaper='Online Financial'
'''
sourcefolder = 'ibnlive/'
sourcename = 'IBN Live'
sourceid = '18'
sourcehomepage = 'ibnlive.com'
typeofpaper='News Channel'

##############################################################################################


thehidustantimes = ['/opinion/','/opinions/','/analysis/','/column/','/columns/','/editorial/','/editorials/','/blog/','/blogs/']
thehindu = ['/op-ed/','/letter/','/letters/','/Readers-Editor/','/open-page/']
thetimesofindia = ['/toi-edit-page/','/toi-editorials/','blog.','blogs.']
theindianexpress= ['/letters-to-editor/']
deccanchronicle = ['/commentary-op-ed/']
tribune = ['/perspective/','/sunday-special/','/sunday/']
opinion_diff = thehindu + thehidustantimes + thetimesofindia + theindianexpress + deccanchronicle + tribune
print len(opinion_diff)


files = os.listdir(sourcefolder)
allindex = 1
delimiter = ','
hashes = set()
header = 'index' + delimiter + 'sourceid'+ delimiter + 'pagenumber' + delimiter + 'pos_on_page';
header = header + delimiter + 'exact_url' + delimiter + 'hash_url' + delimiter + 'opinion_section'
tocsv = header
#print header
for htmlfile in files:
    if htmlfile.find('.html')!=-1:
        pagenumber = htmlfile[:htmlfile.find('.')]
        pagenumber = pagenumber.strip()
        for someurl, somepos in somefn(sourcefolder+htmlfile):
            h = hash(someurl)
            if h in hashes:
                continue
            hashes.add(h)
            
            opinionated = 'No'
            for op_text in opinion_diff:
                if (someurl.lower()).find(op_text)!=-1:
                    opinionated = 'Yes'
                    break
        
            
            newline = str(allindex) + delimiter + sourceid+ delimiter + str(pagenumber) + delimiter + str(somepos);
            newline = newline + delimiter + someurl + delimiter + hashlib.md5(someurl).hexdigest() + delimiter + opinionated;
            #print newline
            tocsv = tocsv + '\n' + newline
            allindex = allindex + 1
print tocsv
tocsvfile = open(str(sourceid)+'.csv','w')
tocsvfile.write(tocsv)
tocsvfile.close()