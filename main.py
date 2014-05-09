# -*- coding: utf-8 -*-
import base64
import json
import sys
import urllib2

from engine import keyWordEngine
from optparse import OptionParser

accountKey = ''
noOfResults = 10

class MyOptionParser(OptionParser):
    def error(self, msg):
        error = """Running command is 
        python main.py --key <bing account key> 
        --userFB <user feedback (Y or N), If Y then query expansion runs till target precision is reached If N then its auto mode>
        --targetPrec <Precision to target, used when user feedback is on>
        --f <file containing queries in format "MB051<newline>35124912364457984<newline>Feb 2011 British Government cuts<endOfFile>">
        --Ngram <1|2 for Unigram or Bigram terms processing>
        --ordering <Y or N for ordering or non-ordering>
        --posTagging <Y or N, Y means part of speech tagging is used. In this case, proper noun and verbs will be ignored for query expansion>
        --maxWords <number of words to expand in one iteration>
        --iter <no of iterations to run when run in auto mode, Default 1>
        --iterResults <no of results to fetch from API for a query, Default is 10>
        """
        print error 
        sys.exit(0)

def main():
    # parse the input options
    parser = MyOptionParser()
    parser.add_option("--key", dest="key")
    parser.add_option("--userFB", dest="feedBack")
    parser.add_option("--targetPrec", dest="targetPrec")
    parser.add_option("--f", dest="fileName")
    parser.add_option("--Ngram", dest="nGram")
    parser.add_option("--ordering",  dest="ordering")
    parser.add_option("--posTagging",  dest="posTagging")
    parser.add_option("--maxWords",  dest="maxWords")
    parser.add_option("--iter",  dest="iterNo")
    parser.add_option("--iterResults",  dest="iterResults")
    (options, args) = parser.parse_args()
    
    isFbActive = options.feedBack
    isFbActive = isFbActive.strip()
    if isFbActive == 'Y' or isFbActive == 'y':
        targetPrec = options.targetPrec
        if not targetPrec:
            parser.error('error')
        targetPrec = targetPrec.strip()
        if not targetPrec:
            parser.error('error')
        try:
            targetPrec = float(targetPrec)
            if targetPrec<=0.0 or targetPrec>1.0:
                print 'Please enter a valid precision value (0-1)'
                sys.exit()
        except ValueError:
            print 'Please enter a valid precision value (0-1)'
            sys.exit()
    
    global accountKey
    accountKey =  options.key
    accountKey = accountKey.strip()
    
    queryFileName = options.fileName
    queryFileName = queryFileName.strip()
    if not queryFileName:
        parser.error('error')
    
    nGram = options.nGram
    ordering = options.ordering
    posTagging = options.posTagging
    maxWords = options.maxWords
    iterResults = options.iterResults
    iterNo = options.iterNo
    if not nGram or not ordering or not posTagging:
        parser.error('error')
    
    if not iterNo:
        iterNo = 1
    else :
        iterNo = iterNo.strip()
        try:
            iterNo = int(iterNo)
            if iterNo < 1:
                parser.error('error')
        except ValueError:
            parser.error('error')
    
    nGram = nGram.strip()
    try:
        nGram = int(nGram)
        if nGram < 1 or nGram > 2:
            parser.error('error')
    except ValueError:
        parser.error('error')
        
    ordering = ordering.strip()
    posTagging = posTagging.strip()
    iterResults = iterResults.strip()
    try:
        iterResults = int(iterResults)
    except ValueError:
        parser.error('error')
    global noOfResults
    noOfResults = iterResults
    
    maxWords = maxWords.strip()
    try:
        maxWords = int(maxWords)
    except ValueError:
        parser.error('error')
        
    
    '''
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
    '''
    #queryList = readQueryFile("E:\Watson-Project-Data\SearchQueryExpansion\queriesForBing.txt")
    queryList = readQueryFile(queryFileName)
    if nGram == 1:
        gramStr = 'Unigram'
        isBigram = False
    elif nGram == 2:
        gramStr = 'Bigram'
        isBigram = True
    else :
        parser.error('error')
    
    if ordering == 'Y' or ordering == 'y':
        orderingStr = 'Ordering'
        isOrder = True
    elif ordering == 'N' or ordering == 'n':
        orderingStr = 'NoOrdering'
        isOrder = False
    else :
        parser.error('error')
    
    if posTagging == 'Y' or posTagging == 'y':
        posTagStr = 'posTagging'
        isPosTagging = True
    elif posTagging == 'N' or posTagging == 'n':
        posTagStr = 'NoPosTagging'
        isPosTagging = False
    else :
        parser.error('error')
    
    if isFbActive == 'N':  
        outputFileName = "queryExpansionBingAPI_Top_" + str(noOfResults)+ "_" + gramStr + "_" + orderingStr + "_" + posTagStr + "_Expand_" + str(maxWords)
    else:
        outputFileName = "queryExpansionBingAPI_Top_" + str(noOfResults)+ "_UserFB" + "_" + gramStr + "_" + orderingStr + "_" + posTagStr + "_Expand_" + str(maxWords)

    if iterNo > 1:
        outputFileName = outputFileName +"_Iter_" + str(iterNo)
        
    outputFile = open(outputFileName,'w')
    
    if isFbActive == 'N':
        print 'Auto run'
        for queryDict in queryList:
            processAutoQuery(queryDict, iterNo, outputFile, isBigram, isOrder, isPosTagging, maxWords) # no of iterations is 1
    else:
        for queryDict in queryList:
            processQueryWithFB(queryDict,queryDict['query'], outputFile, targetPrec, isBigram, isOrder, isPosTagging, maxWords)
    
    outputFile.close()

def bing_search(query):
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
    print "Client key  =  " + accountKey
    print "Query       =  " + query.replace("%20"," ")
    print "Url: " + bingUrl
    
    return result_list
    

def processAutoQuery(queryDict, iterCount, outputFile, bigram, ordering, ignorePosList, maxExpTerms):
    relevant = []
    nonrel = []
    query = queryDict['query']
    for _ in range(iterCount):
        result_list = bing_search(query)
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
        query = keyWordEngine(query,relevant,nonrel,bigram,ordering,ignorePosList, maxExpTerms) # updated query used in nest iteration
        
    expQuery = query.replace('2011', '').replace('Feb', '').replace('Jan', '').replace('  ', ' ')
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

def processQueryWithFB(queryDict, query, outputFile, targetPrec, bigram, ordering, ignorePosList, maxAppTerms):
    result_list = bing_search(query)
    getRelevantFB(queryDict, query, result_list, outputFile, targetPrec, bigram, ordering, ignorePosList, maxAppTerms)

def getRelevantFB(queryDict, query, result_list, outputFile, targetPrec, bigram, ordering, ignorePosList, maxAppTerms):
    userPrec = 0.0;
    relevant = []
    nonrel = []
    global noOfResults
    if len(result_list)<noOfResults:
        print 'There are less than' + noOfResults + ' results to this query. So exiting.'
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
    
    # Get the expanded query
    print "Indexing results ...."
    query = keyWordEngine(query, relevant, nonrel, bigram, ordering, ignorePosList, maxAppTerms)        
        
    # If targetPrecision is achieved
    if userPrec == 0:
        print "Relevance feedback score is zero for this query."
    elif userPrec >= targetPrec:
        print "Desired precision reached, writing expanded query to file"
        expQuery = query.replace('2011', '').replace('Feb', '').replace('Jan', '').replace('  ', ' ')
        origQuery = queryDict['query'].replace('2011', '').replace('Feb', '').replace('Jan', '').replace('  ', ' ')
        print >> outputFile, queryDict['id']+ ','+queryDict['tweetTime']+','+origQuery.strip().replace('  ', ' ')+','+expQuery.strip().replace('  ', ' ')
    else:
        # get next level expansion
        processQueryWithFB(queryDict, query, outputFile, targetPrec, bigram, ordering, ignorePosList, maxAppTerms)
            

if __name__ == "__main__":
    main()
