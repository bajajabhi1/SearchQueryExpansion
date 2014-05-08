# -*- coding: utf-8 -*-
import base64
import json
import sys
import urllib2

from engine import keyWordEngine


accountKey = ''
noOfResults = 20

def main():
    if len(sys.argv) != 5:
        print 'Running command is python main.py [N/Y] <bing account key> <precision> \'<query>\''
        sys.exit()
    
    isFbActive = sys.argv[1]
    query = sys.argv[4]
    targetPrec = sys.argv[3]
    global accountKey
    accountKey = sys.argv[2]
    try:
        targetPrec = float(targetPrec)
        if targetPrec<=0.0 or targetPrec>1.0:
            print 'Please enter a valid precision value (0-1)'
            sys.exit()
    except ValueError:
        print 'Please enter a valid precision value (0-1)'
        sys.exit()
    
    if isFbActive == 'N':
        print 'Auto run'
        queryList = readQueryFile("E:\Watson-Project-Data\SearchQueryExpansion\queriesForBing.txt")
        outputFile = open("queryExpansionBingAPI_Unigram_NoOrdering.txt",'w')
        for queryDict in queryList:
            processAutoQuery(queryDict, targetPrec, 1, outputFile, False, False) # no of iterations is 1
        
        outputFile.close()
    else:
        processQueryWithFB(query, targetPrec)

def bing_search(query,targetPrec):
    query = query.replace(" ","%20")
    global noOfResults
    print '==============================================================='
    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + query + '%27&$top='+ str(noOfResults)+'&$format=json'
    #print bingUrl
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
    #content contains the json response from Bing.
    json_result = json.loads(content)
    result_list = json_result['d']['results']
    
    print "Parameters:"
    #print "Client key  =  " + accountKey
    print "Query       =  " + query.replace("%20"," ")
    #print "Precision   =  " + str(targetPrec)
    print "Url: " + bingUrl
    #print "Total no of results : " + str(len(result_list))
    
    return result_list
    

def processAutoQuery(queryDict, targetPrec, iterCount, outputFile, bigram, ordering):
    relevant = []
    nonrel = []
    for _ in range(iterCount):
        result_list = bing_search(queryDict['query'], targetPrec)
        #if len(result_list)<5:
        #    print 'There are less than 5 results to this query. So exiting.'
        #    sys.exit()
        #print "Bing Search Results:"
        print "======================"
        num = 1
        for result in result_list:
            desc = result[u'Description'].encode("iso-8859-15", "replace")
            title = result[u'Title'].encode("iso-8859-15", "replace")
            url = result[u'Url'].encode("iso-8859-15", "replace")
            #print "Result " + str(num)
            #print "["
            #print "URL: " + url
            #print "Title: " + title
            #print "Summary: " + desc
            #print "]"
            num = num + 1
            entry = {}
            entry['Title'] = title
            entry['Description'] = desc
            entry['Url'] = url            
            relevant.append(entry)
        
        print "Indexing results ...."
        expQuery = keyWordEngine(queryDict['query'],relevant,nonrel,bigram,ordering) # updated query used in nest iteration
        expQuery = expQuery.replace('2011', '').replace('Feb', '').replace('Jan', '').replace('  ', ' ')
        query = queryDict['query'].replace('2011', '').replace('Feb', '').replace('Jan', '').replace('  ', ' ')
        print >> outputFile, queryDict['id']+ ','+queryDict['tweetTime']+','+query.strip().replace('  ', ' ')+','+expQuery.strip().replace('  ', ' ')
    print "Expanded Query - " + expQuery


def readQueryFile(filePathName):
    f = open(filePathName)
    lines = f.readlines()
    queryList = []
    #print len(lines)
    loopCount = len(lines)/3
    #print loopCount
    for i in range(loopCount):
        queryDict = dict()
        queryId = lines[i*3].strip()
        tweetTime = lines[3*i+1].strip()
        query = lines[3*i+2].strip()
        queryDict['id'] = queryId
        queryDict['tweetTime'] = tweetTime
        queryDict['query'] = query
        #print queryId, tweetTime, query
        queryList.append(queryDict)
    
    f.close()
    return queryList

def processQueryWithFB(query, targetPrec):
    result_list = bing_search(query, targetPrec)
    getRelevantFB(query, result_list, targetPrec)

def getRelevantFB(query, result_list, targetPrec):
    userPrec = 0.0;
    relevant = []
    nonrel = []
    global noOfResults
    if len(result_list)<noOfResults:
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

    userPrec = userPrec/noOfResults

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
        query = keyWordEngine(query,relevant,nonrel,False,True)
        if query == '':
            print "Quitting as query is unchanged"
            sys.exit()
        else:            
            processQueryWithFB(query,targetPrec)
            

if __name__ == "__main__":
    main()
