import string
import math
import re
import itertools
import heapq

stopwords = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an', 'and', 'any', 'are', 'as',
             'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear', 'did', 'do', 'does', 'either', 'else',
             'ever', 'every', 'for', 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how', 'however',
             'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my',
             'neither', 'no', 'nor', 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she',
             'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too',
             'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet',
             'you', 'your', 's', 'february', 'january', '2', '1', '3']

alpha = 1
beta = 0.75
gamma = -0.15
titleFactor = 0.2
qualityFactor = 0.2
qualityDocs = ['wikipedia.org']

def keyWordEngine(query,relevant,nonrel,bigram,ordering):
     
    query = query.replace('%20',' ')

    # finding N for calculating IDF
    N_Rel = len(relevant)
    N_Nonrel = len(nonrel)

    #finding TF
    if bigram == True:
        tfRel,titleRel = findTFBigram(relevant)
        tfNonRel,titleNonRel = findTFBigram(nonrel)
        tfQuery = findQueryTFBigram(query)
    else:
        tfRel,titleRel = findTF(relevant)
        tfNonRel,titleNonRel = findTF(nonrel)
        tfQuery = findQueryTF(query)

    #finding IDF
    idfRel = findIDF(tfRel, N_Rel)
    idfNonRel = findIDF(tfNonRel, N_Nonrel)
    
    #finding Relevant weights
    weightsRel = {}
    weightsRel = findWeights(tfRel, idfRel, titleRel, N_Rel)

    #finding Nonrelevant weights
    weightsNonRel = {}
    weightsNonRel = findWeights(tfNonRel, idfNonRel, titleNonRel, N_Nonrel)

    #implemented Rochio to find the new query
    (first,second) = findWords(weightsRel, weightsNonRel, tfQuery)

    # if no new words to be added
    if first =='' and second =='':
        return ''

    finalList = []
    
    print 'Augmented by ' + first + ' ' + second

    #original query modified
    query = query.split()
    if second=="":
        finalList.extend(query)
        finalList.append(first)
    else:
        finalList.extend(query)
        finalList.append(first)
        finalList.append(second)

    
    #find the best order of the words in the query
    if ordering == True:    
        print "Determining the best order of terms"
        finalOrderedList = findPermutations(finalList, relevant)

    modifiedQuery = []
    if ordering == True:
        for wordList in finalOrderedList:
            for word in wordList:
                if word not in modifiedQuery:
                    modifiedQuery.append(word)
    else :
        for word in finalList:
            if word not in modifiedQuery:
                modifiedQuery.append(word)
            
    #clusters are appended
    return " ".join(modifiedQuery)


def searchResults(phrase, docs):
    weight = 0
    for doc in docs:
        content = doc['Title'] + ' ' + doc['Description']
        #Converting to lowercase
        content = content.lower()
        #Removing punctuation
        content = content.translate(string.maketrans("",""), string.punctuation)
        matches = re.findall(re.escape(phrase[0])+'\s'+re.escape(phrase[1]), content)
        weight = weight + len(matches)
    return weight


def findPermutations(queryList,docRel):
    pairWeight = {}
    bestQueryList = []
    useless = set()
    # find all the permutations of the query terms in pairs
    for pair in itertools.permutations(queryList, 2):
        # find the number of times the permutation occurs in relevants docs 
        pairWeight[pair] = searchResults(pair,docRel)
    sortedPairs = sorted(pairWeight.items(), key=lambda x:x[1], reverse = True)

    
    # combine the pairs in order of decreasing weights.
    N = len(queryList)

    for pair in sortedPairs:
        bestQueryList,useless = addPair(0, bestQueryList, pair[0],pair[1], useless)
        

    bestQueryList.append(useless)

    return bestQueryList

def addPair(index, QueryList, pair, weight, useless):
    if len(QueryList)<=index:
        QueryList.append([])
        QueryList[index].append(pair[0])
        QueryList[index].append(pair[1])
    else:
        n = len(QueryList[index])
        if (not isNewWord(pair[0], QueryList, useless)) and (not isNewWord(pair[1], QueryList, useless)):
            return QueryList,useless
        if pair[0]==QueryList[index][n-1]:
            if(weight==0):
                useless.add(pair[1])
            else:
                QueryList[index].append(pair[1])
        elif pair[1]==QueryList[index][0]:
            if(weight==0):
                useless.add(pair[0])
            else:
                QueryList[index].insert(0,pair[0])

        elif pair[0] not in QueryList[index] and pair[1] not in QueryList[index]:
            QueryList,useless = addPair(index+1, QueryList,pair, weight, useless)
                           
    return QueryList,useless

def isNewWord(word, QueryList, useless):
    if word in useless:
        return False
    for wordlist in QueryList:
        if word in wordlist:
            return False
    return True

def findWords(RelDoc, NonrelDoc, query):

    finalWeight = {}
    first = ''
    second = ''
    finalWeight[first]=0
    finalWeight[second]=0

    #finding the final weights based on Rochio algorithm
    for word in RelDoc:
        finalWeight[word] = beta * RelDoc[word]

    for word in query:
        if word in finalWeight:
            finalWeight[word] = finalWeight[word] + alpha * query[word]
        else:
            finalWeight[word] = alpha * query[word]
                        
    for word in NonrelDoc:
        if word in finalWeight:
            finalWeight[word] = finalWeight[word] + gamma * NonrelDoc[word]
        else:
            finalWeight[word] = gamma * NonrelDoc[word]

    # find top 10 words(excluding query terms) from the finalweights using a heap, runs faster than sorting the whole list
    sortWeights = heapq.nlargest(10 + len(query),finalWeight,key=finalWeight.get)

    #Finding top two words by weigths such that the word is not in query
    querySet = set()
    for bigram in query:
        singleList = bigram.split(" ")
        for single in singleList:
            querySet.add(single)
    i = 0
    found = False
    while i < len(sortWeights):
        #if ~any(sortWeights[i] in x for x in querySet):
        if sortWeights[i] not in query:
            candPart = sortWeights[i].split(" ")
            for part in candPart:
                if part not in querySet:
                    first = part
                    finalWeight[first] = finalWeight[sortWeights[i]]                    
                    found = True
                    break
            if found == False:
                i = i+1 # if word not found
            else :
                break
        else:
            i = i+1

    querySet.add(first)
    i = i+1
    while i < len(sortWeights):
        #if ~any(sortWeights[i] in x for x in query):
        if sortWeights[i] not in query:
            candPart = sortWeights[i].split(" ")
            for part in candPart:
                if part not in querySet:
                    second = part
                    finalWeight[second] = finalWeight[sortWeights[i]]
                    found = True
                    break
            if found == False:
                i = i+1 # if word not found
            else :
                break
        else:
            i = i+1
    
    # If top two words have similar weights then take both
    # NOTE - in case first and second are empty then we will return in this check
    if checkSimilarWeights(finalWeight[first],finalWeight[second]):
        return first,second

    # Choosing whether to add one or two new words to the query
    # Taking the avg of top 10 weigths. Take the avg of first term and this avg.
    # Lets call it threshold. if the second term weight is greater than this threshold then take it as well.
    count = 0
    total = 0
    for word in sortWeights:
        if finalWeight[word] < 0:
            break
        count = count + 1
        total = total + finalWeight[word]
    avg = float(total) / float(count)
    threshold = (avg + finalWeight[first])/2.0;

    if finalWeight[second] >= threshold:
        return first, second
    else:
        return first, ""

    
def findWeights(tfDict, idfDict, titleDict, N):
    weight = {}
    for word in tfDict:
        idf = idfDict[word]
        tfTotal = 0
        for doc in tfDict[word]:
            tfTotal = tfTotal + tfDict[word][doc]
        weight[word] = tfTotal * idf
        if word in titleDict: # give more weightage to title words
            weight[word] = weight[word]*(1 + (float(titleDict[word])/float(N))*titleFactor)        
    return weight


def findIDF(tf,N):
    idf = {}
    for word in tf:
        df = len(tf[word]) # document freq is the size of posting list for that term
        idf[word] = math.log10(float(N)/float(df))+1
    return idf
    
def findQueryTF(query):
    tf = {}
    vocab = query
    #Converting to lowercase
    vocab = vocab.lower()
    #Removing punctuation
    vocab = vocab.translate(string.maketrans("",""), string.punctuation)
    #Tokenize into word list
    vocabList = vocab.split()
    for word in vocabList:
      #Adding to dictionary
        if word in tf:
            tf[word] = tf[word] + 1
        else:
            tf[word] = 1
    return tf

def findQueryTFBigram(query):
    tf = {}
    vocab = query
    #Converting to lowercase
    vocab = vocab.lower()
    #Removing punctuation
    vocab = vocab.translate(string.maketrans("",""), string.punctuation)
    #Tokenize into word list
    vocabList = vocab.split()
    vocabListN = len(vocabList)
    vocabListN = vocabListN - 1
    for wordNum in range(0,vocabListN):
        word = vocabList[wordNum] + " " + vocabList[wordNum + 1]
        #Adding to dictionary
        if word in tf:
            tf[word] = tf[word] + 1
        else:
            tf[word] = 1
    return tf

def findTF(docs):
    tf = {}
    docId = 1
    titleDocTF = {}
    replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
    wordWeight = 1
    for doc in docs:
        url = doc['Url']
        #if the url has the word from quality documents list, then improve the weight by a factor of 0.2
        for domain in qualityDocs:
            if re.match(r'.*'+re.escape(domain)+'.*', url):
                wordWeight = 1 + qualityFactor
                break
                
            else:
                wordWeight = 1
            
        vocab = doc['Description']+' '+doc['Title']
        title = doc['Title']
        #Converting to lowercase
        title = title.lower()
        #Removing punctuation
        title = title.translate(replace_punctuation)

        
        titleList = title.split()
        repeat ={}
        for word in titleList:
            if word in titleDocTF and word not in repeat:
                titleDocTF[word] = titleDocTF[word] + 1
                repeat[word] = 1
                
            elif word not in repeat:
                titleDocTF[word] = 1
                repeat[word] = 1
        

        #Converting to lowercase
        vocab = vocab.lower()

        #Removing punctuation
        vocab = vocab.translate(replace_punctuation)

        #Tokenize into word list
        vocabList = vocab.split()

        #Remove stop words
        vocabList= [w for w in vocabList if not w in stopwords]


        
        for word in vocabList:
           #Adding to dictionary
            if word in tf:
                if docId in tf[word]:
                    tf[word][docId] = tf[word][docId] + 1 * wordWeight
                else:
                    tf[word][docId] = 1
            else:
                tf[word] = {}
                tf[word][docId] = 1


        docId = docId + 1 

    return tf, titleDocTF

def findTFBigram(docs):
    tf = {}
    docId = 1
    titleDocTF = {}
    replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
    wordWeight = 1
    for doc in docs:
        url = doc['Url']
        #if the url has the word from quality documents list, then improve the weight by a factor of 0.2
        for domain in qualityDocs:
            if re.match(r'.*'+re.escape(domain)+'.*', url):
                wordWeight = 1 + qualityFactor
                break
                
            else:
                wordWeight = 1
            
        vocab = doc['Description']+' '+doc['Title']
        title = doc['Title']
        #Converting to lowercase
        title = title.lower()
        #Removing punctuation
        title = title.translate(replace_punctuation)
        
        
        titleList = title.split()
        titleListN = len(titleList)
        titleListN = titleListN - 1
        #print titleListN
        #print len(titleList)
        repeat = {}
        for wordNum in range(0,titleListN ):
            word = titleList[wordNum] + " " + titleList[wordNum + 1] 
            if word in titleDocTF and word not in repeat:
                titleDocTF[word] = titleDocTF[word] + 1
                repeat[word] = 1
                
            elif word not in repeat:
                titleDocTF[word] = 1
                repeat[word] = 1
        

        #Converting to lowercase
        vocab = vocab.lower()

        #Removing punctuation
        vocab = vocab.translate(replace_punctuation)

        #Tokenize into word list
        vocabList = vocab.split()

        #Remove stop words
        vocabList= [w for w in vocabList if not w in stopwords]
        vocabListN = len ( vocabList)
        vocabListN = vocabListN - 1
        
        for wordNum in range(0,vocabListN):
           #Adding to dictionary
            word = vocabList[wordNum] + " " + vocabList[wordNum + 1]
            if word in tf:
                if docId in tf[word]:
                    tf[word][docId] = tf[word][docId] + 1 * wordWeight
                else:
                    tf[word][docId] = 1
            else:
                tf[word] = {}
                tf[word][docId] = 1


        docId = docId + 1 

    return tf, titleDocTF
    
def checkSimilarWeights(first, second):
    # check if second and first are close values
    # close is defined by 5% tolerance
    if (first - 0.05*first) <= second:
        return True
    else:
        return False
        
