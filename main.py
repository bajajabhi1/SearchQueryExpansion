# -*- coding: utf-8 -*-
import urllib
import urllib2
import base64
import json
import sys
from engine import keyWordEngine

accountKey = ''

def main():
    if len(sys.argv) != 4:
        print 'Running command is python main.py <bing account key> <precision> \'<query>\''
        sys.exit()
    
    query = sys.argv[3]
    targetPrec = sys.argv[2]
    global accountKey
    accountKey = sys.argv[1]
    try:
        targetPrec = float(targetPrec)
        if targetPrec<=0.0 or targetPrec>1.0:
            print 'Please enter a valid precision value (0-1)'
            sys.exit()
    except ValueError:
        print 'Please enter a valid precision value (0-1)'
        sys.exit()
    
    bing_search(query, targetPrec)

def bing_search(query,targetPrec):
    query = query.replace(" ","%20")
    print '==============================================================='
    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + query + '%27&$top=10&$format=json'
    print bingUrl
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
    #content contains the json response from Bing.
    json_result = json.loads(content)
    result_list = json_result['d']['results']
    
    print "Parameters:"
    print "Client key  =  " + accountKey
    print "Query       =  " + query.replace("%20"," ")
    print "Precision   =  " + str(targetPrec)
    print "Url: " + bingUrl
    print "Total no of results : " + str(len(result_list))
    
    print getRelevantFB(query, result_list,targetPrec)

def getRelevantFB(query, result_list, targetPrec):
    userPrec = 0.0;
    relevant = []
    nonrel = []
    if len(result_list)<10:
        print 'There are less than 10 results to this query. So exiting.'
        sys.exit()
    print "Bing Search Results:"
    print "======================"
    num = 1
    for result in result_list:
        desc = result[u'Description'].encode("iso-8859-15", "replace")
        title = result[u'Title'].encode("iso-8859-15", "replace")
        url = result[u'Url'].encode("iso-8859-15", "replace")
        print "Result " + str(num)
        print "["
        print "URL: " + url
        print "Title: " + title
        print "Summary: " + desc
        print "]"
        num = num + 1
        entry = {}
        entry['Title'] = title
        entry['Description'] = desc
        entry['Url'] = url            
        
        while True:
            isRel = raw_input('Relevant (Y/N)?: ')
            if isRel == 'y' or isRel == 'Y':
                userPrec = userPrec+1
                relevant.append(entry)
                break;
            elif isRel == 'n' or isRel == 'N':
                nonrel.append(entry)
                break;
            else :
                print 'Please provide a feedback(y or n)'

            
    userPrec = userPrec/10

    print '==============================================================='
    print "FEEDBACK SUMMARY"
    print "Query " + query.replace('%20',' ')
    print "Precision from user relevance feedback - " + str(userPrec)
    print 'Target Precision - ' + str(targetPrec)
    
    # If targetPrecision is achieved
    if userPrec == 0:
        print "Quitting as the relevance feedback score is zero."
        sys.exit()
    elif userPrec >= targetPrec:
        print "Desired precision reached, done"
        sys.exit()
    else:
        print "Indexing results ...."
        query = keyWordEngine(query,targetPrec,relevant,nonrel)
        if query == '':
            print "Quitting as query is unchanged"
            sys.exit()
        else:            
            bing_search(query,targetPrec)

if __name__ == "__main__":
    main()
